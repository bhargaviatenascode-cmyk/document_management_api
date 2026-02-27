from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    status: Literal["pending", "approved", "rejected"]
    uploaded_by: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentStatusUpdate(BaseModel):
    status: Literal["approved", "rejected"]
    reason: Optional[str] = Field(default=None, max_length=500)


class DocumentFilterParams(BaseModel):
    status: Optional[Literal["pending", "approved", "rejected"]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)