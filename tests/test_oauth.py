"""OAuth 2.0 + PKCE module tests (no network, no browser)."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


def _settings(**overrides):
    base = {
        "google_client_id": "client-123",
        "google_client_secret": "secret-abc",
        "google_redirect_uri": "http://localhost:8080/callback",
        "google_oauth_redirect_port": 8080,
        "google_oauth_scopes": "scope-a,scope-b",
        "google_token_cache_path": "/nonexistent/cache.json",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_pkce_pair_links_verifier_and_challenge():
    from makpa.google.oauth import generate_pkce_pair

    verifier, challenge = generate_pkce_pair()
    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    assert challenge == expected
    assert "=" not in verifier and "=" not in challenge


def test_parse_scopes_and_auth_url():
    from makpa.google.oauth import build_authorization_url, parse_scopes

    assert parse_scopes("a, b,,c") == ["a", "b", "c"]
    with patch("makpa.google.oauth.get_settings", return_value=_settings()):
        url = build_authorization_url("challenge-xyz")
    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "code_challenge=challenge-xyz" in url
    assert "code_challenge_method=S256" in url
    assert "access_type=offline" in url


def _urlopen_context(payload):
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode()
    context = MagicMock()
    context.__enter__.return_value = response
    return context


def test_exchange_code_posts_pkce_verifier():
    from makpa.google import oauth as oauth_mod

    seen = {}

    def fake_urlopen(request, timeout=30):
        seen["body"] = request.data.decode()
        return _urlopen_context({"access_token": "a", "expires_in": 3600})

    with (
        patch("makpa.google.oauth.get_settings", return_value=_settings()),
        patch("urllib.request.urlopen", side_effect=fake_urlopen),
    ):
        out = oauth_mod.exchange_code_for_tokens("code-1", "verifier-1")
    assert out["access_token"] == "a"
    assert "code_verifier=verifier-1" in seen["body"]
    assert "grant_type=authorization_code" in seen["body"]


def test_exchange_without_client_secret_omits_field():
    from makpa.google import oauth as oauth_mod

    seen = {}

    def fake_urlopen(request, timeout=30):
        seen["body"] = request.data.decode()
        return _urlopen_context({"access_token": "a"})

    settings = _settings(google_client_secret=None)
    with (
        patch("makpa.google.oauth.get_settings", return_value=settings),
        patch("urllib.request.urlopen", side_effect=fake_urlopen),
    ):
        oauth_mod.refresh_access_token("refresh-1")
    assert "client_secret" not in seen["body"]
    assert "grant_type=refresh_token" in seen["body"]


def test_token_endpoint_errors():
    import urllib.error

    from makpa.google import oauth as oauth_mod

    with (
        patch("makpa.google.oauth.get_settings", return_value=_settings()),
        patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("conn refused"),
        ),
    ):
        try:
            oauth_mod.refresh_access_token("r")
            raised = False
        except RuntimeError as e:
            raised = "unreachable" in str(e)
    assert raised

    bad = MagicMock()
    bad.read.return_value = b"not json{{"
    ctx = MagicMock()
    ctx.__enter__.return_value = bad
    with (
        patch("makpa.google.oauth.get_settings", return_value=_settings()),
        patch("urllib.request.urlopen", return_value=ctx),
    ):
        try:
            oauth_mod.refresh_access_token("r")
            raised = False
        except RuntimeError as e:
            raised = "invalid JSON" in str(e)
    assert raised

    with (
        patch("makpa.google.oauth.get_settings", return_value=_settings()),
        patch("urllib.request.urlopen", return_value=_urlopen_context({"error": "bad"})),
    ):
        try:
            oauth_mod.refresh_access_token("r")
            raised = False
        except RuntimeError as e:
            raised = "token error" in str(e)
    assert raised


def test_token_endpoint_http_error_surfaces_body():
    import urllib.error

    from makpa.google import oauth as oauth_mod

    err = urllib.error.HTTPError(
        "https://oauth2.googleapis.com/token", 400, "Bad Request", {}, None
    )
    err.read = lambda: b'{"error": "invalid_grant", "error_description": "stale"}'
    with (
        patch("makpa.google.oauth.get_settings", return_value=_settings()),
        patch("urllib.request.urlopen", side_effect=err),
    ):
        try:
            oauth_mod.refresh_access_token("r")
            raised = False
        except RuntimeError as e:
            raised = "400" in str(e) and "invalid_grant" in str(e)
    assert raised


def test_cache_round_trip_and_helpers(tmp_path):
    from makpa.google import oauth as oauth_mod

    cache_file = str(tmp_path / "tokens.json")
    settings = _settings(google_token_cache_path=cache_file)
    with patch("makpa.google.oauth.get_settings", return_value=settings):
        assert oauth_mod.load_token_cache() is None
        cache = oauth_mod.normalize_cache(
            {"access_token": "a1", "refresh_token": "r1", "expires_in": 3600},
            ["scope-a", "scope-b"],
        )
        oauth_mod.save_token_cache(cache)
        loaded = oauth_mod.load_token_cache()
        assert loaded is not None
        assert loaded["refresh_token"] == "r1"
        assert oauth_mod.access_token_valid(loaded) is True
        assert oauth_mod.cached_scopes(loaded) == ["scope-a", "scope-b"]
        assert oauth_mod.scopes_changed(loaded) is False

    # Scope drift detected.
    with patch(
        "makpa.google.oauth.get_settings",
        return_value=_settings(google_oauth_scopes="scope-a,scope-zzz"),
    ):
        assert oauth_mod.scopes_changed(loaded) is True

    # Expired and malformed caches.
    assert oauth_mod.access_token_valid({"access_token": "", "expiry": ""}) is False
    assert (
        oauth_mod.access_token_valid(
            {"access_token": "a", "expiry": "2000-01-01T00:00:00+00:00"}
        )
        is False
    )
    assert oauth_mod.cached_scopes({"scopes": "scope-a,scope-b"}) == ["scope-a", "scope-b"]
    assert oauth_mod.cached_scopes({}) == []

    # Refresh token preserved across refresh responses.
    merged = oauth_mod.normalize_cache({"access_token": "a2"}, ["scope-a"], previous=loaded)
    assert merged["refresh_token"] == "r1"


def test_save_cache_enforces_0600_where_supported(tmp_path):
    from makpa.google import oauth as oauth_mod

    cache_file = str(tmp_path / "sub" / "tokens.json")
    settings = _settings(google_token_cache_path=cache_file)
    with patch("makpa.google.oauth.get_settings", return_value=settings):
        oauth_mod.save_token_cache({"access_token": "a"})
    assert os.path.exists(cache_file)
    if os.name == "posix":
        assert oct(os.stat(cache_file).st_mode & 0o777) == "0o600"


def test_ensure_credentials_paths():
    from datetime import datetime, timedelta, timezone

    from makpa.google import oauth as oauth_mod
    from makpa.google.oauth import ReauthRequiredError

    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    valid = {
        "access_token": "a",
        "refresh_token": "r",
        "expiry": future,
        "scopes": ["scope-a", "scope-b"],
    }
    with patch("makpa.google.oauth.get_settings", return_value=_settings()):
        with patch("makpa.google.oauth.load_token_cache", return_value=valid):
            creds = oauth_mod.ensure_credentials()
        assert creds.token == "a" and creds.refresh_token == "r"

        # Expired access triggers silent refresh and re-save.
        expired = dict(valid, expiry="2000-01-01T00:00:00+00:00")
        saved = {}
        with (
            patch("makpa.google.oauth.load_token_cache", return_value=expired),
            patch(
                "makpa.google.oauth.refresh_access_token",
                return_value={"access_token": "a2", "expires_in": 3600},
            ),
            patch(
                "makpa.google.oauth.save_token_cache",
                side_effect=lambda data: saved.update(data),
            ),
        ):
            creds = oauth_mod.ensure_credentials()
        assert creds.token == "a2" and saved["refresh_token"] == "r"

        # Refresh failure -> reauth with URL.
        with (
            patch("makpa.google.oauth.load_token_cache", return_value=expired),
            patch(
                "makpa.google.oauth.refresh_access_token",
                side_effect=RuntimeError("down"),
            ),
        ):
            try:
                oauth_mod.ensure_credentials()
                raised = False
            except ReauthRequiredError as e:
                raised = "accounts.google.com" in e.auth_url
        assert raised

        # No cache -> reauth.
        with patch("makpa.google.oauth.load_token_cache", return_value=None):
            try:
                oauth_mod.ensure_credentials()
                raised = False
            except ReauthRequiredError:
                raised = True
        assert raised

        # Scope drift -> reauth even with valid tokens.
        drifted = dict(valid, scopes=["scope-a"])
        with patch("makpa.google.oauth.load_token_cache", return_value=drifted):
            try:
                oauth_mod.ensure_credentials()
                raised = False
            except ReauthRequiredError:
                raised = True
        assert raised


def test_run_browser_flow_and_reauth_codes():
    from makpa.google import oauth as oauth_mod
    from makpa.google.oauth import REAUTH_EXIT_CODE, ReauthRequiredError

    assert REAUTH_EXIT_CODE == 3

    # Missing client id refuses immediately.
    with patch(
        "makpa.google.oauth.get_settings", return_value=_settings(google_client_id=None)
    ):
        try:
            oauth_mod.run_browser_flow()
            raised = False
        except ReauthRequiredError:
            raised = True
    assert raised

    with (
        patch("makpa.google.oauth.get_settings", return_value=_settings()),
        patch("makpa.google.oauth.generate_pkce_pair", return_value=("v", "c")),
        patch("webbrowser.open", return_value=True),
        patch("makpa.google.oauth._receive_code_via_local_server", return_value="code-9"),
        patch(
            "makpa.google.oauth.exchange_code_for_tokens",
            return_value={"access_token": "a", "refresh_token": "r", "expires_in": 60},
        ),
        patch("makpa.google.oauth.save_token_cache") as save_mock,
    ):
        cache = oauth_mod.run_browser_flow()
    assert cache["refresh_token"] == "r"
    save_mock.assert_called_once()

    # Redirect timeout surfaces clearly.
    with (
        patch("makpa.google.oauth.get_settings", return_value=_settings()),
        patch("webbrowser.open", return_value=True),
        patch(
            "makpa.google.oauth._receive_code_via_local_server",
            side_effect=RuntimeError("Timed out waiting for the OAuth redirect"),
        ),
    ):
        try:
            oauth_mod.run_browser_flow()
            raised = False
        except RuntimeError as e:
            raised = "Timed out" in str(e)
    assert raised

    assert oauth_mod.get_google_credentials.__name__ == "get_google_credentials"
