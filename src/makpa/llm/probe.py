"""Startup LLM model-name probe for MAKPA.

Validates the configured LLM model names with a one-token completion
*before* the first user query so stale model names fail fast with a
clear message instead of surfacing mid-demo.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from makpa.config import Mode, Settings, get_settings

logger = logging.getLogger(__name__)

#: Model names observed to rot (404/403 at runtime). Kept as a warning
#: list so defaults that predate a provider rename are flagged early.
KNOWN_STALE_MODELS: frozenset[str] = frozenset(
    {
        "gemini-1.5-flash",
        "llama-3.1-70b-versatile",
    }
)


@dataclass
class ProbeResult:
    """Outcome of the startup LLM probe."""

    provider: str
    model: str
    ok: bool
    message: str
    warnings: list[str] = field(default_factory=list)


def _describe_model(model: object, settings: Settings) -> tuple[str, str]:
    """Describe the *actual* model instance returned by the fallback chain."""
    llm_type = str(getattr(model, "_llm_type", "") or "").lower()
    cls_name = type(model).__name__.lower()
    if "groq" in cls_name:
        return "groq", settings.groq_chat_model
    if "google" in cls_name or "gemini" in cls_name:
        return "gemini", settings.gemini_chat_model
    if "mock" in llm_type or "mock" in cls_name:
        return "mock", "mock-canned"
    return str(settings.resolved_llm_provider.value), cls_name


_PROBE_CACHE: ProbeResult | None = None


def clear_probe_cache() -> None:
    """Clear the cached probe result (tests / session reset)."""
    global _PROBE_CACHE
    _PROBE_CACHE = None


def probe_llm() -> ProbeResult:
    """Probe the configured LLM and fail fast in live mode when unusable.

    Issues a one-token completion through the standard ``get_llm()``
    fallback chain, logs stale-name warnings, and raises ``RuntimeError``
    with a clear remediation message when ``MAKPA_MODE=live`` resolves
    to the mock provider. The result is cached per session unless
    ``MAKPA_LLM_PROBE_ONCE=false`` (debugging).

    Returns:
        ProbeResult describing the resolved provider and model.

    Raises:
        RuntimeError: In live mode when no real provider validates.
    """
    global _PROBE_CACHE
    from makpa.llm import get_llm
    from makpa.utils.terminal import probe_once_enabled

    if _PROBE_CACHE is not None and probe_once_enabled():
        return _PROBE_CACHE

    settings = get_settings()
    warnings: list[str] = []

    for label, name in (
        ("GEMINI_CHAT_MODEL", settings.gemini_chat_model),
        ("GROQ_CHAT_MODEL", settings.groq_chat_model),
    ):
        if name in KNOWN_STALE_MODELS:
            msg = (
                f"{label}={name!r} is a known-stale model name "
                "(previously returned 404/403); update it before a live demo"
            )
            warnings.append(msg)
            logger.warning("Model-name probe: %s", msg)

    model = get_llm()
    provider, model_name = _describe_model(model, settings)

    try:
        response = model.invoke("ok")
        content = getattr(response, "content", str(response))
        if not content:
            raise RuntimeError("empty probe completion")
    except Exception as e:
        message = (
            f"LLM probe failed for provider={provider} model={model_name!r}: {e}. "
            "Check LLM_PROVIDER/GEMINI_CHAT_MODEL/GROQ_CHAT_MODEL and API keys."
        )
        logger.error("Model-name probe: %s", message)
        if settings.resolved_mode == Mode.LIVE:
            raise RuntimeError(message) from e
        result = ProbeResult(
            provider=provider, model=model_name, ok=False,
            message=message, warnings=warnings,
        )
        _PROBE_CACHE = result
        return result

    if provider == "mock" and settings.resolved_mode == Mode.LIVE:
        message = (
            "Live mode requires a working LLM but GEMINI/Groq both failed "
            f"(gemini={settings.gemini_chat_model!r}, "
            f"groq={settings.groq_chat_model!r}); refusing to run live on mock. "
            "Update GEMINI_CHAT_MODEL/GROQ_CHAT_MODEL and API keys."
        )
        logger.error("Model-name probe: %s", message)
        raise RuntimeError(message)

    message = f"LLM probe ok: provider={provider} model={model_name!r}"
    logger.debug("Model-name probe: %s", message)
    result = ProbeResult(
        provider=provider, model=model_name, ok=True,
        message=message, warnings=warnings,
    )
    _PROBE_CACHE = result
    return result


__all__ = ["KNOWN_STALE_MODELS", "ProbeResult", "clear_probe_cache", "probe_llm"]
