"""Utilities module for MAKPA.

Contains shared helpers including logging, tracing, mock chat model,
and confirmation prompt rendering.
"""

from .mock import MockChatModel

__all__ = [
    "setup_logging",
    "setup_tracing",
    "MockChatModel",
    "render_confirmation_prompt",
]
