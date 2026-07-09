"""OAuth 2.0 PKCE helpers for X."""

from __future__ import annotations

import base64
import hashlib
import secrets
from urllib.parse import urlencode

from app.core.config import Settings
from app.integrations.x.endpoints import oauth_authorize_url


def generate_pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest())
        .decode("utf-8")
        .rstrip("=")
    )
    return verifier, challenge


def generate_state() -> str:
    return secrets.token_urlsafe(32)


def build_authorization_url(
    settings: Settings,
    *,
    state: str,
    code_challenge: str,
    scopes: list[str] | None = None,
) -> str:
    scope_values = scopes or settings.X_OAUTH_SCOPES
    params = {
        "response_type": "code",
        "client_id": settings.X_CLIENT_ID,
        "redirect_uri": settings.X_CALLBACK_URL,
        "scope": " ".join(scope_values),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{oauth_authorize_url()}?{urlencode(params)}"
