from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def _normalize_role(role: str | None) -> str:
    return (role or "").strip().lower()


def _normalize_email(email: str | None) -> str:
    return (email or "").strip().lower()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if email is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    normalized_email = _normalize_email(email)
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user:
        raise credentials_exception
    return user


def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if _normalize_role(current_user.role) != _normalize_role(required_role):
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user

    return role_checker


def admin_only(current_user: User = Depends(get_current_user)):
    if _normalize_role(current_user.role) != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user