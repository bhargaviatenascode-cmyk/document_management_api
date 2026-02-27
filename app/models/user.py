from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship, validates

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    documents = relationship("Document", back_populates="uploader")
    history_changes = relationship("DocumentStatusHistory", back_populates="changed_by_user")

    @validates("email")
    def _normalize_email(self, _key: str, value: str) -> str:
        return value.strip().lower()

    @validates("full_name")
    def _normalize_full_name(self, _key: str, value: str) -> str:
        return value.strip()

    @validates("role")
    def _normalize_role(self, _key: str, value: str) -> str:
        normalized = value.strip().lower()
        return normalized or "user"