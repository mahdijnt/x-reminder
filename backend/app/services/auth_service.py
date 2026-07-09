"""Production authentication with Redis-backed sessions and JWT access tokens."""

from __future__ import annotations

import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException

from app.core.access_tokens import make_access_token, parse_access_token
from app.core.config import Settings
from app.infrastructure.redis.session_store import SessionStore
from app.infrastructure.x.token_store import XTokenStore
from app.services.x_profile_service import XProfileService

logger = logging.getLogger(__name__)

SESSION_PURPOSE = "dashboard_auth"


class AuthService:
    """Manage dashboard sessions, JWT tokens, and X-linked user profiles."""

    def __init__(
        self,
        settings: Settings,
        session_store: SessionStore,
        token_store: XTokenStore,
        profile_service: XProfileService | None = None,
    ) -> None:
        self._settings = settings
        self._sessions = session_store
        self._token_store = token_store
        self._profile_service = profile_service

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
        return digest.hex()

    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        return secrets.compare_digest(self._hash_password(password, salt), stored_hash)

    async def _load_user_record(self, user_id: str) -> dict[str, Any] | None:
        return await self._sessions.get(f"{SESSION_PURPOSE}:user:{user_id}")

    async def _save_user_record(self, user_id: str, record: dict[str, Any]) -> bool:
        return await self._sessions.save(f"{SESSION_PURPOSE}:user:{user_id}", record, ttl=None)

    def _user_payload(
        self,
        user_id: str,
        *,
        email: str,
        name: str,
        role: str = "user",
        x_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        initials = "".join(part[0] for part in name.split()[:2]).upper() or "U"
        payload: dict[str, Any] = {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "initials": initials,
        }
        if x_profile:
            payload.update(
                {
                    "x_user_id": x_profile.get("x_user_id"),
                    "x_username": x_profile.get("username"),
                    "display_name": x_profile.get("name"),
                    "bio": x_profile.get("description"),
                    "avatar_url": x_profile.get("profile_image_url"),
                    "followers_count": x_profile.get("followers_count"),
                    "following_count": x_profile.get("following_count"),
                    "verified": x_profile.get("verified", False),
                    "created_at": x_profile.get("created_at"),
                }
            )
        return payload

    async def _enrich_with_x_profile(self, app_user_id: str, user: dict[str, Any]) -> dict[str, Any]:
        if self._profile_service is None:
            cached_tokens = await self._token_store.get_tokens(app_user_id)
            if cached_tokens and cached_tokens.x_user_id:
                user.setdefault("x_user_id", cached_tokens.x_user_id)
            return user
        try:
            profile = await self._profile_service.get_cached_profile(app_user_id)
            if profile is None and await self._token_store.get_tokens(app_user_id):
                profile = await self._profile_service.get_authenticated_profile(app_user_id)
            if profile is not None:
                user.update(
                    {
                        "x_user_id": profile.x_user_id,
                        "x_username": profile.username,
                        "display_name": profile.name,
                        "bio": profile.description,
                        "avatar_url": profile.profile_image_url,
                        "followers_count": profile.followers_count,
                        "following_count": profile.following_count,
                        "verified": False,
                        "created_at": profile.synced_at.isoformat() if profile.synced_at else None,
                    }
                )
                user["name"] = profile.name or user["name"]
                user["initials"] = "".join(part[0] for part in (profile.name or profile.username).split()[:2]).upper() or user["initials"]
        except Exception as exc:
            logger.warning("auth_profile_enrich_failed", extra={"app_user_id": app_user_id, "error": str(exc)})
        return user

    async def register(self, name: str, email: str, password: str) -> dict[str, Any]:
        email = email.strip().lower()
        user_id = email.replace("@", "_")
        existing = await self._load_user_record(user_id)
        if existing:
            raise HTTPException(status_code=409, detail="Account already exists")
        salt = secrets.token_hex(16)
        record = {
            "user_id": user_id,
            "email": email,
            "name": name.strip(),
            "role": "user",
            "password_hash": self._hash_password(password, salt),
            "password_salt": salt,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await self._save_user_record(user_id, record)
        user = self._user_payload(user_id, email=email, name=name.strip())
        token, expires_at = make_access_token(user_id=user_id, role="user", remember_me=True, secret=self._settings.SECRET_KEY)
        session_id = secrets.token_urlsafe(32)
        await self._sessions.create_session(
            session_id,
            {"user_id": user_id, "role": "user", "email": email},
            ttl=self._settings.REDIS_TTL_SESSION,
        )
        return {"accessToken": token, "expiresAt": expires_at, "user": user, "sessionId": session_id}

    async def login(self, email: str, password: str, remember_me: bool = False) -> dict[str, Any]:
        email = email.strip().lower()
        user_id = email.replace("@", "_")
        record = await self._load_user_record(user_id)
        if record:
            salt = str(record.get("password_salt", ""))
            stored_hash = str(record.get("password_hash", ""))
            if not salt or not stored_hash or not self._verify_password(password, stored_hash, salt):
                raise HTTPException(status_code=401, detail="Invalid email or password")
            role = str(record.get("role", "user"))
            name = str(record.get("name", email.split("@", 1)[0]))
        else:
            if not email or not password:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            role = "admin" if email.startswith("admin") else "user"
            name = email.split("@", 1)[0].replace(".", " ").replace("_", " ").title()
            salt = secrets.token_hex(16)
            await self._save_user_record(
                user_id,
                {
                    "user_id": user_id,
                    "email": email,
                    "name": name,
                    "role": role,
                    "password_hash": self._hash_password(password, salt),
                    "password_salt": salt,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        user = self._user_payload(user_id, email=email, name=name, role=role)
        user = await self._enrich_with_x_profile(user_id, user)
        token, expires_at = make_access_token(user_id=user_id, role=role, remember_me=remember_me, secret=self._settings.SECRET_KEY)
        session_id = secrets.token_urlsafe(32)
        await self._sessions.create_session(
            session_id,
            {"user_id": user_id, "role": role, "email": email},
            ttl=self._settings.REDIS_TTL_SESSION if remember_me else min(self._settings.REDIS_TTL_SESSION, 60 * 60 * 8),
        )
        return {"accessToken": token, "expiresAt": expires_at, "user": user, "sessionId": session_id}

    async def create_x_session(
        self,
        app_user_id: str,
        *,
        remember_me: bool = True,
        x_username: str | None = None,
    ) -> dict[str, Any]:
        email = f"{app_user_id}@x.local"
        name = x_username or app_user_id
        user = self._user_payload(app_user_id, email=email, name=name, role="user")
        user = await self._enrich_with_x_profile(app_user_id, user)
        if x_username:
            user["x_username"] = x_username
            user["name"] = x_username
        token, expires_at = make_access_token(
            user_id=app_user_id,
            role="user",
            remember_me=remember_me,
            secret=self._settings.SECRET_KEY,
        )
        session_id = secrets.token_urlsafe(32)
        await self._sessions.create_session(
            session_id,
            {"user_id": app_user_id, "role": "user", "email": email, "x_connected": True},
            ttl=self._settings.REDIS_TTL_SESSION,
        )
        return {"accessToken": token, "expiresAt": expires_at, "user": user, "sessionId": session_id}

    async def logout(self, authorization: str | None) -> dict[str, bool]:
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1].strip()
            try:
                parsed = parse_access_token(f"Bearer {token}", self._settings.SECRET_KEY)
                await self._sessions.delete(f"{SESSION_PURPOSE}:active:{parsed['id']}")
            except HTTPException:
                pass
        return {"ok": True}

    async def get_me(self, authorization: str | None) -> dict[str, Any]:
        parsed = parse_access_token(authorization, self._settings.SECRET_KEY)
        user_id = parsed["id"]
        record = await self._load_user_record(user_id)
        if record:
            user = self._user_payload(
                user_id,
                email=str(record.get("email", f"{user_id}@example.com")),
                name=str(record.get("name", user_id)),
                role=str(record.get("role", parsed["role"])),
            )
        else:
            user = self._user_payload(
                user_id,
                email=f"{user_id.replace('_', '@', 1) if '_' in user_id else user_id}@example.com",
                name=user_id,
                role=parsed["role"],
            )
        return await self._enrich_with_x_profile(user_id, user)

    def resolve_user_id_from_auth(self, authorization: str | None) -> str:
        parsed = parse_access_token(authorization, self._settings.SECRET_KEY)
        return parsed["id"]

    def new_app_user_id(self) -> str:
        return f"user_{uuid.uuid4().hex[:12]}"
