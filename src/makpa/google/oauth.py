"""Google OAuth 2.0 + PKCE module for MAKPA Phase 3.

Authorization-code flow with PKCE, a local callback server, and a
0600 JSON refresh-token cache. Token contents are never logged —
only presence and expiry.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import secrets
import threading
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from makpa.config import get_settings

logger = logging.getLogger(__name__)

#: Exit code the CLI uses when interactive reauthentication is required.
REAUTH_EXIT_CODE = 3

#: Seconds of clock skew tolerated when judging access-token expiry.
EXPIRY_SKEW_SECONDS = 60

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


class ReauthRequiredError(RuntimeError):
    """Raised when silent refresh fails and the user must reauthenticate."""

    def __init__(self, auth_url: str) -> None:
        super().__init__("Google reauthentication required")
        self.auth_url = auth_url


def generate_pkce_pair() -> tuple[str, str]:
    """Generate a PKCE (verifier, challenge) pair.

    Returns:
        Tuple of (code_verifier, code_challenge_S256), base64url
        encoded without padding per RFC 7636.
    """
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def parse_scopes(raw: str) -> list[str]:
    """Split the comma-separated GOOGLE_OAUTH_SCOPES value."""
    return [scope.strip() for scope in raw.split(",") if scope.strip()]


def build_authorization_url(code_challenge: str) -> str:
    """Build the Google consent URL for the PKCE challenge."""
    settings = get_settings()
    params = {
        "client_id": settings.google_client_id or "",
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(parse_scopes(settings.google_oauth_scopes)),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{_GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


def _post_token_endpoint(payload: dict[str, str]) -> dict[str, Any]:
    """POST to the Google token endpoint and return the parsed JSON."""
    body = urllib.parse.urlencode(payload).encode()
    request = urllib.request.Request(_GOOGLE_TOKEN_URL, data=body)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode()
    except Exception as e:
        raise RuntimeError(f"Google token endpoint unreachable: {e}") from e
    try:
        data = json.loads(raw)
    except ValueError as e:
        raise RuntimeError("Google token endpoint returned invalid JSON") from e
    if not isinstance(data, dict) or "error" in data:
        raise RuntimeError(f"Google token error: {data}")
    return dict(data)


def exchange_code_for_tokens(code: str, verifier: str) -> dict[str, Any]:
    """Exchange an authorization code (with PKCE verifier) for tokens."""
    settings = get_settings()
    payload = {
        "client_id": settings.google_client_id or "",
        "code": code,
        "code_verifier": verifier,
        "grant_type": "authorization_code",
        "redirect_uri": settings.google_redirect_uri,
    }
    if settings.google_client_secret:
        payload["client_secret"] = settings.google_client_secret
    return _post_token_endpoint(payload)


def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    """Use a refresh token to obtain a fresh access token."""
    settings = get_settings()
    payload = {
        "client_id": settings.google_client_id or "",
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    if settings.google_client_secret:
        payload["client_secret"] = settings.google_client_secret
    return _post_token_endpoint(payload)


def load_token_cache() -> dict[str, Any] | None:
    """Load the token cache; None when absent or invalid."""
    settings = get_settings()
    try:
        with open(settings.google_token_cache_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    return dict(data) if isinstance(data, dict) else None


def save_token_cache(data: dict[str, Any]) -> None:
    """Persist tokens with file mode 0600. Never logs token contents."""
    settings = get_settings()
    path = settings.google_token_cache_path
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    payload = json.dumps(data, indent=2)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    try:
        os.chmod(path, 0o600)
    except OSError:
        logger.warning("Could not enforce 0600 on token cache")
    logger.info("Saved Google token cache (scopes=%d)", len(str(data.get("scope", ""))))


def normalize_cache(
    token_response: dict[str, Any],
    scopes: list[str],
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge a token response into the cache shape we persist."""
    refresh_token = token_response.get("refresh_token") or (
        previous or {}
    ).get("refresh_token", "")
    expires_in = int(token_response.get("expires_in", 3600))
    expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    return {
        "access_token": token_response.get("access_token", ""),
        "refresh_token": refresh_token,
        "expiry": expiry.isoformat(),
        "scopes": scopes,
    }


def cached_scopes(cache: dict[str, Any]) -> list[str]:
    """Return the scope list stored in a cache entry."""
    scopes = cache.get("scopes", [])
    if isinstance(scopes, str):
        return parse_scopes(scopes)
    return [str(scope) for scope in scopes] if isinstance(scopes, list) else []


def scopes_changed(cache: dict[str, Any]) -> bool:
    """Detect scope drift between cache and settings."""
    settings = get_settings()
    return set(cached_scopes(cache)) != set(parse_scopes(settings.google_oauth_scopes))


def access_token_valid(cache: dict[str, Any]) -> bool:
    """Check the cached access token is present and unexpired."""
    if not cache.get("access_token"):
        return False
    try:
        expiry = datetime.fromisoformat(str(cache.get("expiry", "")))
    except ValueError:
        return False
    return expiry > datetime.now(timezone.utc) + timedelta(
        seconds=EXPIRY_SKEW_SECONDS
    )


def _receive_code_via_local_server(port: int, timeout: int = 300) -> str:
    """Serve the OAuth redirect locally and capture the code parameter."""
    received: dict[str, str] = {}

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            if "code" in params:
                received["code"] = params["code"][0]
                body = b"<html><body><h1>Signed in. Return to MAKPA.</h1></body></html>"
            else:
                body = b"<html><body><h1>Missing code parameter.</h1></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: Any) -> None:
            return

    server = HTTPServer(("127.0.0.1", port), _Handler)
    server.timeout = timeout
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    server.shutdown()
    server.server_close()
    code = received.get("code", "")
    if not code:
        raise RuntimeError("Timed out waiting for the OAuth redirect")
    return code


def run_browser_flow() -> dict[str, Any]:
    """Run the interactive browser flow and return the normalized cache."""
    settings = get_settings()
    if not settings.google_client_id:
        raise ReauthRequiredError(build_authorization_url("missing-client-id"))
    verifier, challenge = generate_pkce_pair()
    auth_url = build_authorization_url(challenge)
    print("Opening browser for Google consent. If it does not open, visit:")
    print(auth_url)
    try:
        webbrowser.open(auth_url)
    except Exception:
        logger.warning("Browser launch failed; URL printed above")
    code = _receive_code_via_local_server(settings.google_oauth_redirect_port)
    tokens = exchange_code_for_tokens(code, verifier)
    cache = normalize_cache(tokens, parse_scopes(settings.google_oauth_scopes))
    save_token_cache(cache)
    return cache


def ensure_credentials() -> Any:
    """Return valid Google credentials, refreshing or prompting as needed.

    Raises:
        ReauthRequiredError: When silent refresh fails or scopes changed
            and no usable refresh token exists.
    """
    from google.oauth2.credentials import Credentials

    settings = get_settings()
    cache = load_token_cache()
    if cache is None or scopes_changed(cache):
        if cache is not None:
            logger.warning("Google OAuth scopes changed; reauthentication required")
        raise ReauthRequiredError(build_authorization_url("reauth-required"))
    if access_token_valid(cache):
        return Credentials(
            token=str(cache.get("access_token", "")),
            refresh_token=str(cache.get("refresh_token", "")),
            token_uri=_GOOGLE_TOKEN_URL,
            client_id=settings.google_client_id or "",
            client_secret=settings.google_client_secret or "",
            scopes=cached_scopes(cache),
        )
    # Silent refresh path.
    try:
        refreshed = refresh_access_token(str(cache.get("refresh_token", "")))
    except Exception as e:
        logger.warning("Google token refresh failed: %s", type(e).__name__)
        raise ReauthRequiredError(build_authorization_url("refresh-failed")) from e
    merged = normalize_cache(refreshed, cached_scopes(cache), previous=cache)
    save_token_cache(merged)
    return Credentials(
        token=str(merged.get("access_token", "")),
        refresh_token=str(merged.get("refresh_token", "")),
        token_uri=_GOOGLE_TOKEN_URL,
        client_id=settings.google_client_id or "",
        client_secret=settings.google_client_secret or "",
        scopes=cached_scopes(merged),
    )


def get_google_credentials() -> Any:
    """Service factory: credentials usable by the local MCP servers."""
    return ensure_credentials()


__all__ = [
    "REAUTH_EXIT_CODE",
    "ReauthRequiredError",
    "access_token_valid",
    "build_authorization_url",
    "cached_scopes",
    "ensure_credentials",
    "exchange_code_for_tokens",
    "generate_pkce_pair",
    "get_google_credentials",
    "load_token_cache",
    "normalize_cache",
    "parse_scopes",
    "refresh_access_token",
    "run_browser_flow",
    "save_token_cache",
    "scopes_changed",
]
