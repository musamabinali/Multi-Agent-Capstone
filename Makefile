# MAKPA - Task Runner
# Makefile equivalent for Windows/PowerShell and Unix

.PHONY: bootstrap smoke lint typecheck test trace todo help

# Default target
help:
	@echo "MAKPA - Available targets:"
	@echo "  bootstrap  - Run bootstrap script (create venv, install deps, setup .env)"
	@echo "  smoke      - Run smoke test"
	@echo "  lint       - Run linter (ruff)"
	@echo "  typecheck  - Run type checker (mypy)"
	@echo "  test       - Run test suite (pytest)"
	@echo "  trace      - Open trace log (TRACE.md)"
	@echo "  todo       - Open todo tracker (TODO.md)"
	@echo "  help       - Show this help"

# Bootstrap: create venv, install deps, setup .env
bootstrap:
	python scripts/bootstrap.py

# Smoke test: run the smoke test entry point
smoke:
	python -m makpa.cli.smoke_test

# Lint: run ruff
lint:
	ruff check src/ tests/

# Typecheck: run mypy
typecheck:
	mypy --strict src/

# Test: run pytest
test:
	pytest tests/ -v

# Trace: open trace log
trace:
	@if command -v code >/dev/null 2>&1; then code docs/TRACE.md; \
	elif command -v notepad >/dev/null 2>&1; then notepad docs/TRACE.md; \
	elif command -v cat >/dev/null 2>&1; then cat docs/TRACE.md; \
	else echo "No suitable editor found"; fi

# Todo: open todo tracker
todo:
	@if command -v code >/dev/null 2>&1; then code docs/TODO.md; \
	elif command -v notepad >/dev/null 2>&1; then notepad docs/TODO.md; \
	elif command -v cat >/dev/null 2>&1; then cat docs/TODO.md; \
	else echo "No suitable editor found"; fi

# Full check pipeline
check: lint typecheck test smoke

# Clean: remove generated files
clean:
	rm -rf .venv __pycache__ .mypy_cache .ruff_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true