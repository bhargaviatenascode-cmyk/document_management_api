from datetime import datetime
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    timestamp: datetime
