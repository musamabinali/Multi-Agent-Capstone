"""Shared terminal UX helpers for MAKPA CLIs.

Centralizes logging setup so every CLI behaves the same:

- all ``logging`` output goes to **stderr** (never stdout),
- default level is ``WARNING`` (``--verbose`` restores ``INFO``),
- ``--quiet`` caps at ``ERROR``, ``--log-file`` captures full logs,
- repeated calls are safe (no handler duplication, never raises).

Also owns the CLI rendering layer: one-time banner/probe state,
confirmation-card emoji + card formatting, sectioned answer output
(Answer / Citations / Actions), timing footers, and color/emoji gates.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import textwrap
import time
from typing import Any

#: Third-party loggers that spam INFO during normal CLI runs.
QUIET_LOGGERS = (
    "httpx",
    "httpcore",
    "google_genai",
    "google_genai.models",
    "google.api_core",
    "google.auth",
    "urllib3",
    "mcp",
    "sentence_transformers",
    "huggingface_hub",
)

_VERBOSE_VALUES = ("1", "true", "yes", "on")

#: Box width cap — never wider than 78 columns.
CARD_WIDTH = 78

#: Agent emojis (one per agent, stable across CLIs).
AGENT_EMOJI = {
    "rag": "\U0001f50d\u0020",
    "github": "\U0001f419\u0020",
    "calendar": "\U0001f4c5\u0020",
    "gmail": "\u2709\ufe0f\u0020",
    "supervisor": "\U0001f916\u0020",
}

# ---------------------------------------------------------------------------
# Session state (one-time banner / probe / fallback notice per process)
# ---------------------------------------------------------------------------

_BANNER_PRINTED = False
_FALLBACK_NOTICED = False


def reset_cli_ux_state() -> None:
    """Reset one-time UX state. Used by tests to simulate a fresh session."""
    global _BANNER_PRINTED, _FALLBACK_NOTICED
    _BANNER_PRINTED = False
    _FALLBACK_NOTICED = False


def verbose_enabled() -> bool:
    """Return True when MAKPA_VERBOSE requests full debug logging."""
    return os.environ.get("MAKPA_VERBOSE", "").strip().lower() in _VERBOSE_VALUES


def quiet_enabled() -> bool:
    """Return True when MAKPA_QUIET requests error-only logging."""
    return os.environ.get("MAKPA_QUIET", "").strip().lower() in _VERBOSE_VALUES


def probe_once_enabled() -> bool:
    """Return False only when MAKPA_LLM_PROBE_ONCE is explicitly disabled."""
    raw = os.environ.get("MAKPA_LLM_PROBE_ONCE", "true").strip().lower()
    return raw not in ("0", "false", "no", "off")


def should_use_color() -> bool:
    """Honor --no-color / NO_COLOR (and quiet JSON scripting)."""
    if os.environ.get("NO_COLOR", "").strip():
        return False
    if os.environ.get("MAKPA_NO_COLOR", "").strip().lower() in _VERBOSE_VALUES:
        return False
    return sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False


def should_use_emoji() -> bool:
    """Honor --no-emoji / NO_EMOJI=1 (Windows CI, some SSH terminals)."""
    if os.environ.get("NO_EMOJI", "").strip() in ("1", "true", "yes"):
        return False
    if os.environ.get("MAKPA_NO_EMOJI", "").strip().lower() in _VERBOSE_VALUES:
        return False
    # Windows cp1252 consoles cannot encode emoji; fall back to ASCII tags.
    try:
        encoding = (getattr(sys.stdout, "encoding", "") or "").lower()
        if encoding and "utf" not in encoding:
            return False
    except Exception:
        return False
    return True


def mark_banner_printed() -> bool:
    """Mark the banner as printed. Returns True if it was already printed."""
    global _BANNER_PRINTED
    already = _BANNER_PRINTED
    _BANNER_PRINTED = True
    return already


def banner_already_printed() -> bool:
    """Return True when the startup banner was already printed this session."""
    return _BANNER_PRINTED


def mark_fallback_noticed() -> bool:
    """Mark the Gemini->Groq fallback as noticed. True if already noticed."""
    global _FALLBACK_NOTICED
    already = _FALLBACK_NOTICED
    _FALLBACK_NOTICED = True
    return already


def fallback_already_noticed() -> bool:
    """Return True when the fallback notice was already printed."""
    return _FALLBACK_NOTICED


def fallback_notice(provider: str = "Groq") -> str | None:
    """One-time fallback line, or None when already printed this session."""
    if mark_fallback_noticed():
        return None
    warn = "\u26a0 " if should_use_emoji() else "! "
    return f"{warn}Gemini unavailable (403) \u2014 using {provider} for this session."


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def setup_logging(
    verbose: bool | None = None,
    quiet: bool = False,
    log_file: str | None = None,
) -> None:
    """Configure root logging on stderr; always safe to call repeatedly.

    Args:
        verbose: force INFO on stderr (default: MAKPA_VERBOSE env).
        quiet: cap stderr at ERROR (useful for scripting).
        log_file: optional path receiving full DEBUG logs regardless of level.
    """
    if verbose is None:
        verbose = verbose_enabled()
    if not verbose:
        # Keep sentence-transformers/huggingface progress noise down; the
        # interactive progress lines carry stage timing instead.
        os.environ.setdefault("HUGGINGFACE_HUB_VERBOSITY", "error")
        os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
        os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
        os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
    if quiet or quiet_enabled():
        level = logging.ERROR
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    root = logging.getLogger()
    # Remove default stdout handlers installed by basicConfig so logs never
    # interleave with user-facing print() output on stdout.
    for handler in list(root.handlers):
        try:
            root.removeHandler(handler)
        except Exception:
            pass
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(level)
    stderr_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    class _NoiseFilter(logging.Filter):
        """Drop known-noisy third-party notices unless verbose."""

        def filter(self, record: logging.LogRecord) -> bool:
            if verbose:
                return True
            try:
                msg = record.getMessage().lower()
            except Exception:
                return True
            if "automatic function calling" in msg:
                return False
            if "unauthenticated requests" in msg:
                return False
            return True

    noise_filter = _NoiseFilter()
    stderr_handler.addFilter(noise_filter)
    root.addHandler(stderr_handler)
    root.setLevel(level)
    # Some third-party libs (huggingface_hub, sentence-transformers) attach
    # their own stderr handlers; filter those too so the AFC/HF notices stay
    # silent unless verbose. Logger levels are untouched (tests assert them).
    try:
        loggers = [root] + [
            logging.getLogger(name)
            for name in list(logging.root.manager.loggerDict.keys())
        ]
    except Exception:
        loggers = [root]
    for candidate in loggers:
        try:
            for handler in list(getattr(candidate, "handlers", [])):
                if handler is not stderr_handler:
                    handler.addFilter(noise_filter)
        except Exception:
            pass

    for name in QUIET_LOGGERS:
        logging.getLogger(name).setLevel(logging.DEBUG if verbose else logging.WARNING)

    # Silence known-noisy Python warnings unless verbose (AFC + HF hub).
    import warnings as _warnings

    if verbose:
        _warnings.filterwarnings("default", message=".*automatic function calling.*")
        _warnings.filterwarnings("default", message=".*unauthenticated requests.*")
    else:
        _warnings.filterwarnings("ignore", message=".*automatic function calling.*")
        _warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")

    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            root.addHandler(file_handler)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Confirmation titles, emoji, and cards
# ---------------------------------------------------------------------------


def confirmation_title(preview: dict[str, Any]) -> str:
    """Gate-aware confirmation title; no bogus "(gate ?)" when unset."""
    gate = preview.get("gate")
    if gate in (1, 2):
        return f"Confirmation required (gate {gate})"
    return "Confirmation required"


def _preview_blob(preview: dict[str, Any]) -> str:
    try:
        return json.dumps(preview, default=str).lower()
    except (TypeError, ValueError):
        return str(preview).lower()


def confirmation_emoji(preview: dict[str, Any]) -> str:
    """Derive the confirmation emoji from payload tools.

    - ``calendar_*`` -> calendar,
    - ``gmail_*`` -> email,
    - both -> calendar+email,
    - ``github_create_*``/``github_*`` write -> octopus,
    - unknown -> supervisor robot.
    """
    blob = _preview_blob(preview)
    has_cal = "calendar_" in blob
    has_mail = "gmail_" in blob or "gmail" in blob and "send" in blob
    # "gmail" alone is ambiguous (read tools mention gmail too); require a
    # mutating marker for the email emoji.
    if not has_mail:
        has_mail = any(
            marker in blob
            for marker in ("gmail_send", "gmail_draft", "send_message", "draft_message")
        )
    has_gh = "github_create_" in blob or "create_issue" in blob or "create_pr" in blob
    if has_cal and has_mail:
        return "\U0001f4c5\u0020\u2709\ufe0f\u0020" if should_use_emoji() else "[calendar+email]"
    if has_cal:
        return "\U0001f4c5\u0020" if should_use_emoji() else "[calendar]"
    if has_mail:
        return "\u2709\ufe0f\u0020" if should_use_emoji() else "[email]"
    if has_gh or "github_" in blob:
        return "\U0001f419\u0020" if should_use_emoji() else "[github]"
    gate = preview.get("gate")
    if gate == 1:
        return "\U0001f4c5\u0020" if should_use_emoji() else "[calendar]"
    if gate == 2:
        return "\u2709\ufe0f\u0020" if should_use_emoji() else "[email]"
    return "\U0001f916\u0020" if should_use_emoji() else "[confirm]"


def confirmation_indicator(preview: dict[str, Any]) -> str:
    """Human-readable indicator (emoji + agent name) for prompts."""
    emoji = confirmation_emoji(preview)
    blob = _preview_blob(preview)
    if "calendar_" in blob and ("gmail_" in blob or "gmail_send" in blob):
        return f"{emoji} Calendar+Gmail agent"
    if "calendar_" in blob:
        return f"{emoji} Calendar agent"
    if "gmail_" in blob or "gmail_send" in blob or "gmail_draft" in blob:
        return f"{emoji} Gmail agent"
    if "github_" in blob:
        return f"{emoji} GitHub agent"
    return f"{emoji} Supervisor"


def _truncate(value: str, limit: int = 87, label: str = "value") -> str:
    value = str(value)
    if len(value) <= limit:
        return value
    return f"{value[: limit - 20]}... [{label} \u2014 {len(value)} chars \u2014 press v to view]"


def _event_fields(event: dict[str, Any], combined: bool) -> list[tuple[str, str]]:
    """Format a structured event dict (gate previews carry an ``event`` key)."""
    out: list[tuple[str, str]] = []
    summary = str(event.get("summary", ""))
    if summary:
        out.append(("Event" if combined else "Summary", summary))
    start = str(event.get("start", ""))
    end = str(event.get("end", ""))
    if combined and start:
        out.append(("When", f"{start}\u2013{end}" if end else start))
    else:
        if start:
            out.append(("Start", start))
        if end:
            out.append(("End", end))
    attendees = event.get("attendees", event.get("attendee", ""))
    if attendees:
        out.append(
            (
                "Attendees",
                ", ".join(map(str, attendees))
                if isinstance(attendees, list)
                else str(attendees),
            )
        )
    link = event.get("html_link", event.get("link", ""))
    if link:
        out.append(("Link", _truncate(str(link), 60, label="link")))
    return out


def _email_fields(email: dict[str, Any], combined: bool) -> list[tuple[str, str]]:
    """Format a structured email dict (gate previews carry an ``email`` key)."""
    out: list[tuple[str, str]] = []
    to = email.get("to", email.get("recipients", ""))
    if to:
        out.append(
            ("Email to" if combined else "To",
             ", ".join(map(str, to)) if isinstance(to, list) else str(to))
        )
    if email.get("subject"):
        out.append(("Subject", str(email["subject"])))
    if email.get("body"):
        out.append(("Body", _truncate(str(email["body"]), label="full body")))
    if email.get("draft_id"):
        out.append(("Draft", str(email["draft_id"])))
    return out


def _preview_fields(preview: dict[str, Any]) -> list[tuple[str, str]]:
    """Extract display fields from a gate preview (never raw dict repr)."""
    fields: list[tuple[str, str]] = []
    raw_event: Any = preview.get("event")
    raw_email: Any = preview.get("email")
    event: dict[str, Any] | None = raw_event if isinstance(raw_event, dict) else None
    email: dict[str, Any] | None = raw_email if isinstance(raw_email, dict) else None
    has_event = event is not None and bool(event)
    has_email = email is not None and bool(email)
    if event is not None and has_event:
        fields.extend(_event_fields(event, combined=has_email))
    if email is not None and has_email:
        fields.extend(_email_fields(email, combined=has_event))
    if fields:
        return fields
    candidates: list[dict[str, Any]] = []
    # Gate previews carry the planned tool calls here (single + composite).
    steps = preview.get("payload_preview")
    if isinstance(steps, list):
        for step in steps:
            if isinstance(step, dict):
                args = step.get("args")
                if isinstance(args, dict):
                    candidates.append(args)
    payload = preview.get("payload")
    if isinstance(payload, dict):
        candidates.append(payload)
    if isinstance(preview.get("args"), dict):
        candidates.append(preview["args"])
    for key in ("tool_args", "tool_input", "params"):
        if isinstance(preview.get(key), dict):
            candidates.append(preview[key])
    merged: dict[str, Any] = {}
    for cand in candidates:
        for k, v in cand.items():
            merged.setdefault(k, v)
    consumed: set[str] = set()
    # Calendar-style gate (LLM planners emit "title"/"start_time" variants).
    if any(
        k in merged
        for k in ("summary", "title", "start", "time_min", "start_time", "attendees")
    ):
        summary = merged.get("summary", merged.get("title", ""))
        if summary:
            fields.append(("Summary", str(summary)))
        consumed.update(("summary", "title"))
        consumed.update(
            ("start", "time_min", "start_time", "end", "time_max", "end_time",
             "attendees", "mode", "attendee_mode")
        )
        start = merged.get("start", merged.get("time_min", merged.get("start_time", "")))
        end = merged.get("end", merged.get("time_max", merged.get("end_time", "")))
        if start:
            fields.append(("Start", str(start)))
        if end:
            fields.append(("End", str(end)))
        if "attendees" in merged:
            att = merged["attendees"]
            fields.append(
                ("Attendees", ", ".join(map(str, att)) if isinstance(att, list) else str(att))
            )
        if "mode" in preview:
            fields.append(("Mode", str(preview["mode"])))
        elif "attendee_mode" in merged:
            fields.append(("Mode", str(merged["attendee_mode"])))
    # Email-style gate.
    if any(k in merged for k in ("to", "recipients", "subject", "body")):
        to = merged.get("to", merged.get("recipients", ""))
        fields.append(("To", ", ".join(map(str, to)) if isinstance(to, list) else str(to)))
        if "subject" in merged:
            fields.append(("Subject", str(merged["subject"])))
        if "body" in merged:
            fields.append(("Body", _truncate(str(merged["body"]), label="full body")))
        if "draft_id" in merged and merged["draft_id"]:
            fields.append(("Draft", str(merged["draft_id"])))
        consumed.update(("to", "recipients", "subject", "body", "draft_id"))
    # GitHub-style gate (requires a repo/head/base marker so LLM arg
    # variants like calendar "title" never render as a GitHub Title/Body).
    if "repo" in merged or any(
        k in merged for k in ("head", "base", "issue", "pr", "issue_number", "pr_number")
    ):
        for key in ("repo", "title", "body", "head", "base"):
            if key in merged and merged[key]:
                label = key.capitalize()
                fields.append((label, _truncate(str(merged[key]), 60)))
                consumed.add(key)
    # Leftover scalar args (LLM planner variants like description/location):
    # formatted fields, never raw repr.
    leftovers = {
        k: v
        for k, v in merged.items()
        if k not in consumed and k not in ("tool", "status") and v not in (None, "", [], {})
    }
    for key in sorted(leftovers):
        value = leftovers[key]
        if isinstance(value, dict):
            rendered = json.dumps(value, default=str)[:120]
        elif isinstance(value, list):
            rendered = ", ".join(map(str, value))[:120]
        else:
            rendered = str(value)
        fields.append((key.replace("_", " ").title(), _truncate(rendered, 60)))
    if not fields:
        # Fallback: scalar preview keys only (skip nested raw dicts/lists).
        skip = {
            "gate", "payload", "args", "tool_args", "tool_input", "params",
            "payload_preview", "event", "email", "question",
        }
        for key, value in preview.items():
            if key in skip or isinstance(value, (dict, list)):
                continue
            fields.append((key.capitalize(), _truncate(str(value), 60)))
    if not fields:
        fields.append(("Preview", "(structured preview unavailable)"))
    return fields


def confirmation_card_title(preview: dict[str, Any]) -> str:
    """Adaptive card header including the payload-derived emoji."""
    emoji = confirmation_emoji(preview)
    blob = _preview_blob(preview)
    has_cal = "calendar_" in blob
    has_mail = "gmail_" in blob or "gmail_send" in blob or "gmail_draft" in blob
    if has_cal and has_mail:
        return f"{emoji} Confirm meeting + invite email"
    if has_cal:
        return f"{emoji} Confirm calendar event"
    if has_mail:
        return f"{emoji} Confirm email send"
    if "github_" in blob:
        return f"{emoji} Confirm GitHub write"
    gate = preview.get("gate")
    if gate == 1:
        return f"{emoji} Confirm calendar event"
    if gate == 2:
        return f"{emoji} Confirm email send"
    return f"{emoji} Confirm action"


def format_confirmation_card(preview: dict[str, Any], width: int = CARD_WIDTH) -> str:
    """Render an adaptive two-column confirmation card (<=78 cols)."""
    width = min(width, CARD_WIDTH)
    title = confirmation_card_title(preview)
    fields = _preview_fields(preview)
    inner = width - 4
    top = "\u250c\u2500 " + title[: inner - 2].ljust(inner - 2) + " \u2500\u2510"
    bottom = "\u2514" + "\u2500" * (width - 2) + "\u2518"
    lines = [top, "\u2502" + " " * (width - 2) + "\u2502"]
    label_w = max([len(label) for label, _ in fields] + [4])
    for label, value in fields:
        first = True
        chunks = textwrap.wrap(value, width=inner - label_w - 4) or [""]
        for chunk in chunks:
            tag = (label + ":").rjust(label_w + 1) if first else " " * (label_w + 1)
            row = f" {tag} {chunk}"
            lines.append("\u2502 " + row.ljust(inner - 1) + "")
            first = False
    lines.append("\u2502" + " " * (width - 2) + "\u2502")
    lines.append(bottom)
    return "\n".join(lines)


def wrap_box_lines(lines: list[str], width: int = 100) -> list[str]:
    """Word-wrap long confirmation-box lines so previews stay readable."""
    wrapped: list[str] = []
    for line in lines:
        wrapped.extend(textwrap.wrap(line, width=width) or [""])
    return wrapped


# ---------------------------------------------------------------------------
# Sectioned final answer
# ---------------------------------------------------------------------------


def clean_answer_text(answer: str) -> str:
    """Strip tool-result suffixes (Details:/Citations:) from model prose.

    Citations render in their own section; leaving them inline duplicates
    every citation (once as a blob, once formatted).
    """
    text = str(answer).strip()
    for marker in (
        "\nDetails:",
        "\n<details",
        "Details: -",
        "Details:",
        "\nCitations:",
        " Citations: [",
    ):
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].rstrip()
    return text


def _box(title: str, body_lines: list[str], width: int = CARD_WIDTH) -> str:
    width = min(width, CARD_WIDTH)
    inner = width - 4
    top = "\u250c\u2500 " + title[: inner - 2].ljust(inner - 2) + " \u2500\u2510"
    bottom = "\u2514" + "\u2500" * (width - 2) + "\u2518"
    out = [top]
    for line in body_lines:
        for chunk in textwrap.wrap(line, width=inner) or [""]:
            out.append("\u2502 " + chunk.ljust(inner - 1) + "")
    out.append(bottom)
    return "\n".join(out)


def format_answer_section(answer: str) -> str:
    """Render the Answer box (model synthesis only, no raw dicts)."""
    cleaned = clean_answer_text(answer) or "(no answer)"
    return _box("Answer", [cleaned])


def format_citations_section(citations: list[dict[str, Any]]) -> str:
    """Render the Citations box; empty string when no citations."""
    if not citations:
        return ""
    rows = []
    for cite in citations:
        src = cite.get("source", "?") if isinstance(cite, dict) else str(cite)
        page = cite.get("page", "?") if isinstance(cite, dict) else "?"
        chunk = cite.get("chunk_id", "?") if isinstance(cite, dict) else "?"
        rows.append(f"[{src} \u00b7 p.{page} \u00b7 chunk {chunk}]")
    return _box("Citations", rows)


def format_actions_section(
    structured: dict[str, Any] | None,
    tool_results: list[dict[str, Any]] | None = None,
    verbose: bool = False,
) -> str:
    """Render the Actions box from structured ids (never prose regex)."""
    blocks: list[str] = []
    data = structured or {}
    citations_free = {k: v for k, v in data.items() if k != "citations"}
    if data.get("event_id") or data.get("event_ids"):
        ids = data.get("event_ids") or [data.get("event_id")]
        cal_title = "\U0001f4c5\u0020 Calendar event created" if should_use_emoji() else "Calendar event"
        blocks.append(cal_title)
        blocks.append(f"   id:   {ids[0]}")
        if data.get("when"):
            blocks.append(f"   when: {data['when']}")
        if data.get("link"):
            blocks.append(f"   link: {data['link']}")
        if data.get("calendar_status"):
            blocks.append(f"   status: {data['calendar_status']}")
    if data.get("message_id") or data.get("draft_id"):
        blocks.append("")
        blocks.append("\u2709\ufe0f\u0020 Email sent" if should_use_emoji() else "Email sent")
        if data.get("to"):
            blocks.append(f"   to:      {data['to']}")
        if data.get("subject"):
            blocks.append(f"   subject: {data['subject']}")
        if data.get("message_id"):
            blocks.append(f"   message: {data['message_id']}")
        if data.get("draft_id"):
            blocks.append(f"   draft:   {data['draft_id']}")
    if data.get("pr_numbers") or data.get("issue_numbers") or data.get("commit_shas"):
        blocks.append("")
        blocks.append("\U0001f419\u0020 GitHub result" if should_use_emoji() else "GitHub result")
        if data.get("repo"):
            blocks.append(f"   repo:   {data['repo']}")
        for n in list(data.get("pr_numbers") or []):
            blocks.append(f"   pr:     {n}")
        for n in list(data.get("issue_numbers") or []):
            blocks.append(f"   issue:  {n}")
        for s in list(data.get("commit_shas") or []):
            blocks.append(f"   commit: {s}")
    if not blocks and citations_free:
        # Generic fallback: scalar structured fields only.
        for key, value in citations_free.items():
            if isinstance(value, (dict, list)) and not value:
                continue
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)[:120]
            blocks.append(f"{key}: {value}")
    if not blocks:
        return ""
    if verbose and tool_results:
        blocks.append("")
        blocks.append("Raw tool payloads:")
        for item in tool_results:
            blocks.append(json.dumps(item, default=str)[:200])
    # Strip one leading blank when the first block added it.
    while blocks and not blocks[0].strip():
        blocks.pop(0)
    return _box("Actions", blocks)


def format_timing(total_s: float, parts: dict[str, float], parallel: bool = False) -> str:
    """Render the timing footer (always the last line)."""
    clock = "\u23f1 " if should_use_emoji() else "timing: "
    sep = " \u2016 " if parallel else "   \u00b7   "
    chunks = [f"total {total_s:.1f}s"]
    for name, dur in parts.items():
        chunks.append(f"{name} {dur:.1f}s")
    suffix = "   (parallel)" if parallel else ""
    return f"{clock}" + sep.join(chunks) + suffix


def format_cancelled_timing(total_s: float) -> str:
    """Timing footer for flows declined at a confirmation gate."""
    clock = "\u23f1 " if should_use_emoji() else "timing: "
    return f"{clock}total {total_s:.1f}s   \u00b7   (cancelled at confirmation)"


def render_sectioned_result(
    answer: str,
    citations: list[dict[str, Any]] | None = None,
    structured: dict[str, Any] | None = None,
    tool_results: list[dict[str, Any]] | None = None,
    total_s: float = 0.0,
    parts: dict[str, float] | None = None,
    parallel: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> str:
    """Render Answer / Citations / Actions + timing footer in order.

    Empty sections are omitted entirely. Quiet mode keeps only Answer
    plus the timing footer.
    """
    sections = [format_answer_section(answer)]
    if not quiet:
        cites = format_citations_section(list(citations or []))
        if cites:
            sections.append(cites)
        actions = format_actions_section(structured, tool_results, verbose=verbose)
        if actions:
            sections.append(actions)
    sections.append(format_timing(total_s, parts or {}, parallel=parallel))
    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Progress lines + timing helpers
# ---------------------------------------------------------------------------


class StageTimer:
    """Lightweight per-stage timer for the timing footer."""

    def __init__(self) -> None:
        self._starts: dict[str, float] = {}
        self.durations: dict[str, float] = {}

    def start(self, name: str) -> None:
        """Start timing a stage."""
        self._starts[name] = time.monotonic()

    def stop(self, name: str) -> float:
        """Stop timing a stage and return its duration."""
        dur = time.monotonic() - self._starts.pop(name, time.monotonic())
        self.durations[name] = dur
        return dur


def progress_line(agent: str, message: str, duration_s: float | None = None) -> str:
    """Render one structured progress line (no timestamps, no level prefix)."""
    emoji = AGENT_EMOJI.get(agent, AGENT_EMOJI["supervisor"])
    label = {"rag": "RAG agent", "github": "GitHub agent", "calendar": "Calendar agent",
             "gmail": "Gmail agent"}.get(agent, agent)
    if not should_use_emoji():
        emoji = ""
        line = f"{label} {message}"
    else:
        line = f"{emoji} {label} {message}"
    if duration_s is not None:
        line = f"{line.ljust(60)} ({duration_s:.1f}s)"
    return line


def progress_done(agent: str, summary: str, duration_s: float) -> str:
    """Render a completed-stage line with a checkmark."""
    check = "\u2713 " if should_use_emoji() else "done: "
    return progress_line(agent, f"{check}{summary}", duration_s)


__all__ = [
    "AGENT_EMOJI",
    "CARD_WIDTH",
    "QUIET_LOGGERS",
    "StageTimer",
    "banner_already_printed",
    "clean_answer_text",
    "confirmation_card_title",
    "confirmation_emoji",
    "confirmation_indicator",
    "confirmation_title",
    "fallback_already_noticed",
    "fallback_notice",
    "format_actions_section",
    "format_answer_section",
    "format_cancelled_timing",
    "format_citations_section",
    "format_confirmation_card",
    "format_timing",
    "mark_banner_printed",
    "mark_fallback_noticed",
    "print_banner_once",
    "probe_once_enabled",
    "progress_done",
    "progress_line",
    "quiet_enabled",
    "render_sectioned_result",
    "reset_cli_ux_state",
    "setup_logging",
    "should_use_color",
    "should_use_emoji",
    "verbose_enabled",
    "wrap_box_lines",
]


def print_banner_once(banner_fn: Any) -> bool:
    """Call banner_fn once per session. Returns True when printed now."""
    if banner_already_printed():
        return False
    mark_banner_printed()
    banner_fn()
    return True
