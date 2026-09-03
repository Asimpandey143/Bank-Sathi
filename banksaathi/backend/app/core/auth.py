"""
Authentication core — JWT tokens and password hashing.

NEVER log or expose:
- raw passwords
- JWT signing secrets
- OTP values
- PIN values

This is a prototype JWT implementation.
Production systems must use bank-provider approved authentication.
"""
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a password with bcrypt. Never store plaintext passwords."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))


def hash_phone(phone: str) -> str:
    """
    Hash a phone number for storage.
    Allows lookup without storing the raw phone.
    """
    return hashlib.sha256(f"banksaathi:{phone}".encode()).hexdigest()


def create_access_token(user_id: uuid.UUID) -> str:
    """Create a JWT access token for the given user ID."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """
    Decode a JWT token and return the user_id (sub) claim.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None
