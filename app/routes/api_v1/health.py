from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(tags=["health"])
started_at = datetime.now(timezone.utc)


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    uptime_seconds = (datetime.now(timezone.utc) - started_at).total_seconds()
    return {"status": "ok", "database": db_status, "uptime_seconds": uptime_seconds}
