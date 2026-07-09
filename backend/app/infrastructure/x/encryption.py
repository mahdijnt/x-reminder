"""Symmetric encryption for stored OAuth tokens."""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import Settings


def _fernet_key(settings: Settings) -> bytes:
    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_value(settings: Settings, plaintext: str) -> str:
    f = Fernet(_fernet_key(settings))
    return f.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_value(settings: Settings, ciphertext: str) -> str:
    f = Fernet(_fernet_key(settings))
    try:
        return f.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt token payload") from exc
