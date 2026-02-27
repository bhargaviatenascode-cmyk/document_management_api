from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RefreshRequest, TokenResponse, UserLogin, UserRegister
from app.schemas.user import UserOut
from app.services.rate_limiter import SimpleRateLimiter

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])
limiter = SimpleRateLimiter(limit=settings.rate_limit_login_per_minute)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def normalize_role(role: str | None) -> str:
    return (role or "").strip().lower()


@router.post("/register", response_model=UserOut)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Ensure at least one admin exists in system
    has_admin = db.query(User).filter(User.role.ilike("admin")).first() is not None
    role = "user" if has_admin else "admin"

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        hashed_password=get_password_hash(payload.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# OAuth2-compatible login (used by Swagger "Authorize" button)
@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    key = request.client.host if request.client else "unknown"
    if not limiter.allow(key):
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")

    email = normalize_email(form_data.username)
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


# Optional: keep JSON-based login for Postman/custom clients
@router.post("/login-json", response_model=TokenResponse)
def login_json(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    key = request.client.host if request.client else "unknown"
    if not limiter.allow(key):
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")

    email = normalize_email(payload.email)
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        decoded = jwt.decode(payload.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        email = decoded.get("sub")
        token_type = decoded.get("type")
        exp = decoded.get("exp")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if not email or not exp:
        raise HTTPException(status_code=401, detail="Invalid refresh token payload")

    if token_type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    if datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(User).filter(User.email == normalize_email(email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )