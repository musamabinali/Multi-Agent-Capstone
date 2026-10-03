"""Tests for the thin FastAPI adapter (no business logic here)."""

from __future__ import annotations


def _client():
    from fastapi.testclient import TestClient

    from makpa.api.server import app

    return TestClient(app)


def test_health_reports_mode_and_downgrades():
    client = _client()
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    for key in (
        "mode",
        "llm_provider",
        "vector_store",
        "github_path",
        "google_path",
        "oauth_state",
        "downgrades",
        "probe",
    ):
        assert key in body


def test_thread_lifecycle_invoke():
    client = _client()
    created = client.post("/api/threads")
    assert created.status_code == 200
    thread_id = created.json()["thread_id"]
    assert thread_id.startswith("makpa-web-") or "-web-" in thread_id

    listed = client.get("/api/threads")
    assert thread_id in [t["thread_id"] for t in listed.json()["threads"]]

    invoked = client.post(
        f"/api/threads/{thread_id}/invoke",
        json={"message": "What does the sample PDF say?"},
    )
    assert invoked.status_code == 200
    body = invoked.json()
    assert body["thread_id"] == thread_id
    assert "rag_agent" in body["agents"] or body["agent_outputs"]
    assert body["status"] in (
        "ok",
        "partial",
        "error",
        "empty",
        "confirmation_required",
        "cancelled",
    )

    fetched = client.get(f"/api/threads/{thread_id}")
    assert fetched.status_code == 200

    deleted = client.delete(f"/api/threads/{thread_id}")
    assert deleted.json()["deleted"] is True


def test_resume_requires_pause():
    client = _client()
    created = client.post("/api/threads").json()
    thread_id = created["thread_id"]
    response = client.post(
        f"/api/threads/{thread_id}/resume", json={"confirm": True}
    )
    # Fresh thread is not paused at a gate.
    assert response.status_code in (404, 409, 500)
    client.delete(f"/api/threads/{thread_id}")


def test_resume_validation():
    client = _client()
    created = client.post("/api/threads").json()
    thread_id = created["thread_id"]
    response = client.post(f"/api/threads/{thread_id}/resume", json={})
    assert response.status_code == 422
    client.delete(f"/api/threads/{thread_id}")


def test_interrupt_kind_derives_from_payload_preview():
    from makpa.api.server import _interrupt_kind

    assert _interrupt_kind({"gate": 2, "payload_preview": []}) == "2"
    assert _interrupt_kind({"gate": 1, "payload_preview": []}) == "1"
    assert (
        _interrupt_kind({"payload_preview": [{"tool": "gmail_send_message"}]})
        == "gmail_send_message"
    )
    assert (
        _interrupt_kind({"payload_preview": [{"tool": "github_create_issue"}]})
        == "github_create_issue"
    )
    assert _interrupt_kind({"payload_preview": []}) == "confirm"
    assert _interrupt_kind({"action": "schedule_meeting"}) == "schedule_meeting"


def test_thread_ids_deterministic_unique():
    client = _client()
    first = client.post("/api/threads").json()["thread_id"]
    second = client.post("/api/threads").json()["thread_id"]
    assert first != second
    assert "-web-" in first and "-web-" in second
