from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": subject, "type": token_type, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str) -> str:
    return create_token(subject, "access", timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(subject: str) -> str:
    return create_token(subject, "refresh", timedelta(minutes=settings.refresh_token_expire_minutes))
