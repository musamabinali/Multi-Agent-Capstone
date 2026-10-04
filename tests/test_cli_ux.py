"""CLI UX overhaul tests (log separation, one-time startup, cards, sections)."""

from __future__ import annotations

import json
import logging
import re
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

runner = CliRunner()


def _probe_ok() -> SimpleNamespace:
    return SimpleNamespace(provider="mock", model="mock-canned", warnings=[], message="ok")


def test_log_channel_separation_no_info_on_stdout(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Logging goes to stderr; stdout carries only user output."""
    from makpa.utils.terminal import setup_logging

    monkeypatch.delenv("MAKPA_VERBOSE", raising=False)
    monkeypatch.delenv("MAKPA_QUIET", raising=False)
    setup_logging()
    # Root must have at least one stderr handler and no stdout handler.
    import sys

    handlers = logging.getLogger().handlers
    assert handlers, "expected at least one log handler"
    for handler in handlers:
        stream = getattr(handler, "stream", None)
        assert stream is not sys.stdout, "logs must never write to stdout"
    logging.getLogger("makpa.test").warning("ux-probe-warning")
    out, err = capsys.readouterr()
    assert "ux-probe-warning" not in out
    assert "INFO" not in out and "WARNING" not in out


def test_one_time_banner() -> None:
    """Two commands in a session print the banner exactly once."""
    from makpa.utils.terminal import print_banner_once, reset_cli_ux_state

    reset_cli_ux_state()
    calls: list[int] = []

    def _banner() -> None:
        calls.append(1)

    assert print_banner_once(_banner) is True
    assert print_banner_once(_banner) is False
    assert len(calls) == 1


def test_one_time_fallback_notice(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gemini unavailable notice appears exactly once per session."""
    from makpa.utils.terminal import fallback_notice, reset_cli_ux_state

    reset_cli_ux_state()
    monkeypatch.delenv("NO_EMOJI", raising=False)
    monkeypatch.delenv("MAKPA_NO_EMOJI", raising=False)
    first = fallback_notice("Groq")
    second = fallback_notice("Groq")
    assert first is not None and "Gemini unavailable" in first
    assert second is None


def test_confirmation_card_emoji(monkeypatch: pytest.MonkeyPatch) -> None:
    """Emoji matches payload tools for calendar/email/composite/github."""
    from makpa.utils import terminal as term

    monkeypatch.delenv("NO_EMOJI", raising=False)
    monkeypatch.delenv("MAKPA_NO_EMOJI", raising=False)
    term.reset_cli_ux_state()
    cal = {"gate": 1, "payload": {"tool": "calendar_create_event", "summary": "S"}}
    mail = {"gate": 2, "payload": {"tool": "gmail_send_message", "subject": "Hi"}}
    both = {
        "gate": 2,
        "payload_preview": [{"tool": "calendar_create_event"}, {"tool": "gmail_send_message"}],
    }
    gh = {"payload": {"tool": "github_create_issue", "repo": "o/r"}}
    assert term.confirmation_emoji(cal) == "\U0001f4c5"
    assert term.confirmation_emoji(mail) == "\u2709\ufe0f"
    assert term.confirmation_emoji(both) == "\U0001f4c5\u2709\ufe0f"
    assert term.confirmation_emoji(gh) == "\U0001f419"
    # Cards never exceed 78 columns and never show raw dict repr.
    for preview in (cal, mail, both, gh):
        card = term.format_confirmation_card(preview)
        assert max(len(line) for line in card.splitlines()) <= 78
        assert re.search(r"\{\s*'", card) is None


def test_sectioned_answer_order_and_omission() -> None:
    """Answer/Citations/Actions + timing render in order; empties omitted."""
    from makpa.utils.terminal import render_sectioned_result

    cites = [
        {"source": "sample.pdf", "page": 7, "chunk_id": 36},
        {"source": "sample.pdf", "page": 12, "chunk_id": 61},
    ]
    structured = {"event_id": "evt-1", "event_ids": ["evt-1"], "message_id": "msg-1"}
    out = render_sectioned_result(
        "scheduled ok", citations=cites, structured=structured, total_s=12.4,
        parts={"RAG": 1.5, "Calendar": 5.1}, verbose=False,
    )
    ia, ic, id_, it = (
        out.find("Answer"), out.find("Citations"), out.find("Actions"), out.find("total")
    )
    assert -1 not in (ia, ic, id_, it) and ia < ic < id_ < it
    # Empty sections are omitted entirely.
    bare = render_sectioned_result("just answer", total_s=1.0)
    assert "Citations" not in bare and "Actions" not in bare
    assert "Answer" in bare and "total" in bare


def test_quiet_suppresses_progress_and_cards() -> None:
    """Quiet keeps only Answer + timing footer."""
    from makpa.utils.terminal import render_sectioned_result

    out = render_sectioned_result(
        "quiet answer",
        citations=[{"source": "s", "page": 1, "chunk_id": 1}],
        structured={"event_id": "e"},
        total_s=2.0, quiet=True,
    )
    assert "quiet answer" in out and "total" in out
    assert "Citations" not in out and "Actions" not in out


def test_json_mode_emits_valid_json() -> None:
    """--json emits one object with answer/citations/actions/timings/status."""
    from makpa.cli import google_demo

    graph = MagicMock()
    graph.get_state.return_value = SimpleNamespace(next=())
    graph.invoke.return_value = {"answer": "2 events", "status": "ok", "tool_results": []}
    with (
        patch("makpa.llm.probe_llm",
              return_value=SimpleNamespace(provider="mock", model="m", warnings=[], message="ok")),
        patch("makpa.subagents.google.create_google_graph", return_value=graph),
    ):
        res = runner.invoke(google_demo.app, ["ask", "List events", "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output.strip().splitlines()[-1])
    assert set(payload) >= {"answer", "citations", "actions", "timings", "status"}


def test_no_raw_dict_repr_in_default_output() -> None:
    """Default-mode output never contains Python dict repr."""
    from makpa.utils.terminal import (
        format_actions_section,
        format_answer_section,
        format_confirmation_card,
    )

    answer = format_answer_section("The event was created Details: - x: {'a': 1}")
    assert re.search(r"\{\s*'", answer) is None
    actions = format_actions_section({"event_id": "evt-1", "event_ids": ["evt-1"]})
    assert re.search(r"\{\s*'", actions) is None
    card = format_confirmation_card({"gate": 1, "payload": {"tool": "calendar_create_event"}})
    assert re.search(r"\{\s*'", card) is None


def test_answer_box_has_no_citations_suffix() -> None:
    """Citations: suffix is stripped; Answer box never contains it."""
    from makpa.utils.terminal import clean_answer_text, format_answer_section

    raw = (
        "The sample document covers RAG Retrieval. Additionally each subsection "
        "closes with a checklist.  Citations: [sample.pdf, p.7, chunk 35], "
        "[sample.pdf, p.5, chunk 25]"
    )
    assert "Citations:" not in clean_answer_text(raw)
    assert clean_answer_text(raw).endswith("checklist.")
    box = format_answer_section(raw)
    assert re.search(r"Citations:", box) is None
    # Details: stripping still works.
    assert "Details:" not in clean_answer_text("ok\nDetails: - x: 1")


def test_composite_card_renders_event_and_email() -> None:
    """Gate-2 structured preview renders event + email fields, no hint blob."""
    from makpa.utils import terminal as term

    preview = {
        "gate": 2,
        "payload_preview": [
            {"tool": "gmail_send_message", "args": {"to": ["a@x.com"]}},
        ],
        "event": {
            "summary": "Project Sync",
            "start": "2026-10-05T14:00:00+05:00",
            "end": "2026-10-05T14:30:00+05:00",
            "attendees": ["a@x.com"],
        },
        "email": {"to": ["a@x.com"], "subject": "Project Sync", "body": "Hi, confirming."},
    }
    card = term.format_confirmation_card(preview)
    for needle in ("Project Sync", "2026-10-05T14:00:00", "a@x.com", "Hi, confirming."):
        assert needle in card
    assert "Resume with" not in card
    assert max(len(line) for line in card.splitlines()) <= 78
    assert re.search(r"\{\s*'", card) is None


def test_payload_preview_steps_render_without_backend_keys() -> None:
    """Single-path combined preview (steps only) still renders both halves."""
    from makpa.utils import terminal as term

    preview = {
        "payload_preview": [
            {"tool": "calendar_create_event",
             "args": {"summary": "Sync", "start": "s", "end": "e",
                      "attendees": ["a@x.com"]}},
            {"tool": "gmail_send_message",
             "args": {"to": ["a@x.com"], "subject": "Sync", "body": "Hi"}},
        ],
        "hint": "Resume with ...",
    }
    card = term.format_confirmation_card(preview)
    for needle in ("Sync", "a@x.com", "Hi"):
        assert needle in card
    assert "Resume with" not in card
    assert re.search(r"\{\s*'", card) is None


def test_llm_variant_args_render_without_github_hijack() -> None:
    """LLM 'title' alias renders as Summary; Body appears exactly once."""
    from makpa.utils import terminal as term

    preview = {
        "payload_preview": [
            {"tool": "calendar_create_event",
             "args": {"title": "Sync", "attendees": ["a@x.com"]}},
            {"tool": "gmail_send_message",
             "args": {"to": ["a@x.com"], "subject": "Sync", "body": "Hi"}},
        ],
    }
    card = term.format_confirmation_card(preview)
    assert "Summary" in card and "Sync" in card
    assert "Title" not in card  # no GitHub block without a repo marker
    assert card.count("Body:") == 1
    assert re.search(r"\{\s*'", card) is None


def test_composite_gate_previews_carry_structured_fields() -> None:
    """confirm_event/confirm_email nodes emit display-ready event/email keys."""
    from makpa.subagents.google import graph as g

    captured: dict[str, object] = {}

    def _capture(value: object) -> dict[str, bool]:
        assert isinstance(value, dict)
        captured.update(value)
        return {"confirm": True}

    plan = [{
        "tool": "calendar_create_event",
        "args": {"summary": "S", "start": "s", "end": "e", "attendees": ["a@x.com"]},
    }]
    with patch("makpa.subagents.google.graph.interrupt", side_effect=_capture):
        g.confirm_event_node({"question": "q", "plan": plan})
    assert captured["event"] == {
        "summary": "S", "start": "s", "end": "e", "attendees": ["a@x.com"]
    }

    captured.clear()
    estate = {
        "question": "q",
        "plan": [{
            "tool": "gmail_send_message",
            "args": {"to": ["a@x.com"], "subject": "Hi", "body": "Yo", "draft_id": "d1"},
        }],
        "tool_results": [{
            "tool": "calendar_create_event", "status": "ok",
            "event": {"summary": "S", "start": "s", "end": "e", "html_link": "http://l"},
        }],
    }
    with patch("makpa.subagents.google.graph.interrupt", side_effect=_capture):
        g.confirm_email_node(estate)
    assert captured["email"] == {
        "to": ["a@x.com"], "subject": "Hi", "body": "Yo", "draft_id": "d1"
    }
    event = captured["event"]
    assert isinstance(event, dict) and event["summary"] == "S"
    assert event["attendees"] == ["a@x.com"]


def test_ingest_uses_progress_and_timing() -> None:
    """ingest prints a timed progress line plus a timing footer."""
    from makpa.cli import rag_demo
    from makpa.rag.ingestion import IngestionResult

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.cli.rag_demo.ingest_pdf",
            return_value=IngestionResult(75, 0, "chroma_local", 10, ["a"]),
        ),
    ):
        res = runner.invoke(rag_demo.app, ["ingest"])
    assert res.exit_code == 0, res.output
    assert "ingested 75 chunks" in res.output and "chroma_local" in res.output
    assert "total" in res.output


def test_cancelled_flow_prints_timing_footer() -> None:
    """Declining a gate prints the answer plus a cancelled timing footer."""
    import typer

    from makpa.cli import google_demo
    from makpa.cli.google_demo import _report_ask_result

    with pytest.raises(typer.Exit):
        _report_ask_result(
            {"status": "cancelled", "answer": "nope"}, total_s=4.2,
            verbose=False, quiet=False, json_output=False,
        )
    # Decline-at-gate end to end: card fields render, footer follows.
    snap = SimpleNamespace(
        next=("confirm_event",),
        tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value={
            "gate": 1,
            "payload_preview": [{"tool": "calendar_create_event",
                                 "args": {"summary": "S"}}],
        })])],
    )
    graph = MagicMock()
    graph.get_state.side_effect = [snap, snap]
    graph.invoke.side_effect = [
        {"status": "ok"},
        {"answer": "Operation cancelled: no changes were made.", "status": "cancelled"},
    ]
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=graph),
    ):
        res = runner.invoke(google_demo.app, ["ask", "schedule it"], input="n\n")
    assert res.exit_code == 2, res.output
    assert "cancelled at confirmation" in res.output
    assert "total" in res.output


def test_setup_logging_disables_progress_bars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-verbose setup silences tqdm/HF progress env switches."""
    import os

    from makpa.utils.terminal import setup_logging

    for var in ("HF_HUB_DISABLE_PROGRESS_BARS", "TRANSFORMERS_NO_ADVISORY_WARNINGS"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.delenv("MAKPA_VERBOSE", raising=False)
    setup_logging()
    assert os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] == "1"
    assert os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] == "1"


def test_interactive_session_commands() -> None:
    """Interactive REPL honors :verbose, :thread, :reset, :exit."""
    from makpa.cli import google_demo

    graph = MagicMock()
    seen: list[str] = []

    def _fake_once(g: object, thread_id: str, q: str, quiet: bool = False) -> dict[str, str]:
        seen.append(f"{thread_id}:{q}")
        return {"answer": f"ok {q}", "status": "ok"}

    inputs = iter([":verbose", ":thread t-2", "hello", ":reset", ":exit"])
    with (
        patch("builtins.input", side_effect=lambda _prompt="": next(inputs)),
        patch.object(google_demo, "_ask_once", side_effect=_fake_once),
        patch.object(google_demo, "_report_ask_result", return_value=None),
    ):
        google_demo._ask_repl(graph, "base", verbose=False, quiet=True, json_output=False)
    assert any(s.endswith(":hello") and s.startswith("t-2:") for s in seen)
