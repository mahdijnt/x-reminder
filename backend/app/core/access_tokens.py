"""HMAC-signed access tokens for dashboard UI auth."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException


def _b64url_encode(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64url_decode(token_part: str) -> dict:
    padding = "=" * (-len(token_part) % 4)
    raw = base64.urlsafe_b64decode(f"{token_part}{padding}".encode("utf-8"))
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def _sign(header: str, payload: str, secret: str) -> str:
    signing_input = f"{header}.{payload}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def make_access_token(user_id: str, role: str, remember_me: bool, secret: str) -> tuple[str, int]:
    ttl = 60 * 60 * 24 * 30 if remember_me else 60 * 60 * 8
    exp = int((datetime.now(timezone.utc) + timedelta(seconds=ttl)).timestamp())
    header = _b64url_encode({"alg": "HS256", "typ": "JWT"})
    payload = _b64url_encode({"sub": user_id, "role": role, "exp": exp})
    signature = _sign(header, payload, secret)
    return f"{header}.{payload}.{signature}", exp * 1000


def parse_access_token(auth_header: str | None, secret: str) -> dict:
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")
    token = auth_header.split(" ", 1)[1].strip()
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid token")
    header, payload_part, signature = parts
    expected = _sign(header, payload_part, secret)
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid token")
    payload = _b64url_decode(payload_part)
    exp = int(payload.get("exp", 0))
    if exp <= int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=401, detail="Token expired")
    sub = str(payload.get("sub", "")).strip()
    role = str(payload.get("role", "user")).strip() or "user"
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token subject")
    return {"id": sub, "role": role}
