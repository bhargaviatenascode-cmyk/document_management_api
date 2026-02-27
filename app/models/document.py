from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    content_type = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    uploader = relationship("User", back_populates="documents")
    status_history = relationship("DocumentStatusHistory", back_populates="document", cascade="all, delete-orphan")


class DocumentStatusHistory(Base):
    __tablename__ = "document_status_history"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="status_history")
    changed_by_user = relationship("User", back_populates="history_changes")
