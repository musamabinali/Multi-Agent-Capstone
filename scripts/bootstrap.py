#!/usr/bin/env python3
"""Bootstrap script for MAKPA.

Verifies Python version, creates virtual environment, installs dependencies,
copies .env.example to .env if needed, and prints next steps.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MIN_PYTHON_VERSION = (3, 10)


def check_python_version() -> bool:
    """Check if Python version meets minimum requirement."""
    if sys.version_info < MIN_PYTHON_VERSION:
        print(f"ERROR: Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ required")
        current = sys.version_info
        print(f"Current: {current.major}.{current.minor}.{current.micro}")
        return False
    print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def run_command(cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a command and return success status."""
    try:
        subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def main() -> int:
    """Main bootstrap routine."""
    project_root = Path(__file__).parent.parent
    venv_path = project_root / ".venv"
    env_example = project_root / ".env.example"
    env_file = project_root / ".env"
    requirements = project_root / "requirements.txt"

    print("=" * 60)
    print("MAKPA Bootstrap")
    print("=" * 60)

    # 1. Verify Python version
    print("\n[1/5] Checking Python version...")
    if not check_python_version():
        return 1

    # 2. Create virtual environment if absent
    print("\n[2/5] Setting up virtual environment...")
    if not venv_path.exists():
        print("  Creating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", str(venv_path)]):
            return 1
    else:
        print("  Virtual environment already exists")

    # Determine pip executable in venv
    if sys.platform == "win32":
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:
        venv_pip = venv_path / "bin" / "pip"

    # 3. Upgrade pip (non-fatal)
    print("\n[3/5] Upgrading pip...")
    run_command([str(venv_pip), "install", "--upgrade", "pip"])

    # 4. Install dependencies
    print("\n[4/5] Installing dependencies...")
    if not run_command([str(venv_pip), "install", "-r", str(requirements)]):
        return 1

    # 5. Copy .env.example to .env if .env doesn't exist
    print("\n[5/5] Setting up environment file...")
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy2(env_example, env_file)
        print("  Created .env from .env.example")
    elif env_file.exists():
        print("  .env already exists, skipping")
    else:
        print("  WARNING: .env.example not found")

    print("\n" + "=" * 60)
    print("Bootstrap complete!")
    print("=" * 60)
    print("\nNext steps:")
    if sys.platform == "win32":
        print("  .\\.venv\\Scripts\\activate")
    else:
        print("  source .venv/bin/activate")
    print("  python -m makpa.cli.smoke_test")
    print("\nOr use the task runner:")
    print("  make smoke")
    return 0


if __name__ == "__main__":
    sys.exit(main())
