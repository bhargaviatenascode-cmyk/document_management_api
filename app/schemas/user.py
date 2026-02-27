from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
