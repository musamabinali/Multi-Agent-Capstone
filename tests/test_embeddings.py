"""Unit tests for the embedding factory (both branches)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from makpa.vectorstore import clear_embeddings_cache, get_embeddings_for_provider


def test_huggingface_branch_mocked():
    clear_embeddings_cache()
    fake = MagicMock()
    with patch(
        "makpa.vectorstore.embeddings.EmbeddingFactory._create_huggingface_embeddings",
        return_value=fake,
    ):
        model = get_embeddings_for_provider("huggingface")
        assert model is fake
    clear_embeddings_cache()


def test_gemini_branch_falls_back_when_no_key():
    clear_embeddings_cache()
    fake_hf = MagicMock()
    with (
        patch(
            "makpa.vectorstore.embeddings.EmbeddingFactory._create_gemini_embeddings",
            return_value=None,
        ),
        patch(
            "makpa.vectorstore.embeddings.EmbeddingFactory._create_huggingface_embeddings",
            return_value=fake_hf,
        ),
    ):
        model = get_embeddings_for_provider("gemini")
        assert model is fake_hf
    clear_embeddings_cache()


def test_gemini_branch_mocked():
    clear_embeddings_cache()
    fake = MagicMock()
    with patch(
        "makpa.vectorstore.embeddings.EmbeddingFactory._create_gemini_embeddings",
        return_value=fake,
    ):
        # Direct internal call path via provider override still uses cache logic
        from makpa.vectorstore.embeddings import EmbeddingFactory

        factory = EmbeddingFactory()
        factory.clear_cache()
        # Monkey-patch settings-independent path
        with patch.object(factory, "_create_gemini_embeddings", return_value=fake):
            assert factory.get_embeddings("gemini") is fake
    clear_embeddings_cache()
