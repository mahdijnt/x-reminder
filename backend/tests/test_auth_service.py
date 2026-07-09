import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.services.auth_service import AuthService


class _MemorySessionStore:
  def __init__(self) -> None:
    self._data: dict[str, dict] = {}

  async def save(self, session_id: str, data: dict, *, ttl: int | None = None) -> bool:
    self._data[session_id] = data
    return True

  async def get(self, session_id: str, *, sliding: bool = True):
    return self._data.get(session_id)

  async def delete(self, session_id: str) -> int:
    return 1 if self._data.pop(session_id, None) else 0

  async def create_session(self, session_id: str, data: dict, *, ttl: int | None = None) -> bool:
    return await self.save(session_id, data, ttl=ttl)


class _MemoryTokenStore:
  async def get_tokens(self, app_user_id: str):
    return None


@pytest.mark.asyncio
async def test_auth_register_and_login_round_trip():
  settings = Settings(SECRET_KEY="test-secret-key-32-characters!!", REDIS_ENABLED=False)
  auth = AuthService(settings, _MemorySessionStore(), _MemoryTokenStore())

  registered = await auth.register("Test User", "user@example.com", "password123")
  assert registered["user"]["email"] == "user@example.com"
  assert registered["accessToken"]

  session = await auth.login("user@example.com", "password123", remember_me=True)
  assert session["user"]["name"] == "Test User"

  me = await auth.get_me(f"Bearer {session['accessToken']}")
  assert me["id"] == "user@example.com".replace("@", "_")


@pytest.mark.asyncio
async def test_auth_login_rejects_invalid_password():
  settings = Settings(SECRET_KEY="test-secret-key-32-characters!!", REDIS_ENABLED=False)
  auth = AuthService(settings, _MemorySessionStore(), _MemoryTokenStore())
  await auth.register("Test User", "user@example.com", "password123")

  with pytest.raises(HTTPException) as exc:
    await auth.login("user@example.com", "wrong-password")
  assert exc.value.status_code == 401
