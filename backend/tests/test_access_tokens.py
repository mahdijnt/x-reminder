from app.core.access_tokens import make_access_token, parse_access_token


def test_access_token_round_trip():
    secret = "test-secret-key-32-characters!!"
    token, _expires = make_access_token("user_1", "user", remember_me=False, secret=secret)
    parsed = parse_access_token(f"Bearer {token}", secret=secret)
    assert parsed["id"] == "user_1"
    assert parsed["role"] == "user"


def test_access_token_rejects_tampered_signature():
    secret = "test-secret-key-32-characters!!"
    token, _expires = make_access_token("user_1", "user", remember_me=False, secret=secret)
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    try:
        parse_access_token(f"Bearer {tampered}", secret=secret)
        assert False, "expected invalid token"
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401
