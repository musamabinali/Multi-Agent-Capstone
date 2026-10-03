"""Pre-warm the HuggingFace embedding model cache (MAKPA).

The first embedding download takes ~60s; running this once during
bootstrap keeps demos fast. Safe to re-run (idempotent).

Usage: python scripts/prewarm_embeddings.py
"""

from __future__ import annotations

import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main() -> None:
    """Download and cache the configured embedding model."""
    from makpa.vectorstore import get_embeddings

    start = time.time()
    model = get_embeddings()
    # Touch the model so weights/tokenizer materialize in the HF cache.
    try:
        vec = model.embed_query("prewarm")
        dim = len(vec)
    except Exception as exc:
        print(f"Pre-warm failed: {exc}")
        raise SystemExit(1)
    elapsed = time.time() - start
    print(f"Embeddings ready: dim={dim} in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
