from datetime import timedelta
from app.core import security

def test_password_hashing():
    password = "SuperPassword123"
    hashed = security.get_password_hash(password)
    assert hashed != password
    assert security.verify_password(password, hashed) is True
    assert security.verify_password("wrongpassword", hashed) is False

def test_jwt_creation_and_decoding():
    subject = "user-id-uuid-test"
    token = security.create_access_token(subject, expires_delta=timedelta(minutes=15))
    assert isinstance(token, str)

    decoded = security.decode_token(token)
    assert decoded.get("sub") == subject
    assert decoded.get("type") == "access"

def test_refresh_token_creation():
    subject = "user-id-uuid-test"
    token = security.create_refresh_token(subject, expires_delta=timedelta(days=1))
    assert isinstance(token, str)

    decoded = security.decode_token(token)
    assert decoded.get("sub") == subject
    assert decoded.get("type") == "refresh"
