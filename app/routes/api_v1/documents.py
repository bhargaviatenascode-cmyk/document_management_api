from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.document import Document, DocumentStatusHistory
from app.models.user import User
from app.schemas.document import DocumentOut, DocumentStatusUpdate
from app.services.cache import CacheService
from app.services.storage import LocalStorageService
from app.utils.file_validation import validate_upload_file

settings = get_settings()
router = APIRouter(prefix="/documents", tags=["documents"])
storage = LocalStorageService(settings.upload_dir)
cache = CacheService()


def _is_admin(user: User) -> bool:
    return (user.role or "").strip().lower() == "admin"


def log_approval(document_id: int, admin_email: str):
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Document %s approved by %s", document_id, admin_email)


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = await validate_upload_file(file)
    path = storage.upload(content, file.filename)

    doc = Document(
        filename=file.filename,
        file_path=path,
        content_type=file.content_type,
        status="pending",
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    history = DocumentStatusHistory(
        document_id=doc.id,
        old_status=None,
        new_status="pending",
        changed_by=current_user.id,
        reason="Initial upload",
    )
    db.add(history)
    db.commit()

    cache.delete("approved_documents")
    cache.delete("admin_stats")
    return doc


@router.get("/me", response_model=list[DocumentOut])
def my_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Document)
        .filter(Document.uploaded_by == current_user.id, Document.is_deleted.is_(False))
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("", response_model=list[DocumentOut])
def list_documents(
    status: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = _is_admin(current_user)

    # Admin can use global cache for simple approved listing
    if (
        is_admin
        and status == "approved"
        and not any([start_date, end_date, search])
        and page == 1
        and page_size == 10
    ):
        cached = cache.get("approved_documents")
        if cached:
            return cached

    query = db.query(Document).filter(Document.is_deleted.is_(False))

    # Non-admin users can only see their own documents
    if not is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    if status:
        query = query.filter(Document.status == status)
    if start_date:
        query = query.filter(Document.created_at >= start_date)
    if end_date:
        query = query.filter(Document.created_at <= end_date)
    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))

    docs = query.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    if (
        is_admin
        and status == "approved"
        and not any([start_date, end_date, search])
        and page == 1
        and page_size == 10
    ):
        cache.set("approved_documents", [DocumentOut.model_validate(d).model_dump(mode="json") for d in docs])

    return docs


@router.patch("/{document_id}/status", response_model=DocumentOut)
def update_document_status(
    document_id: int,
    payload: DocumentStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Robust admin check (avoids role case/space issues)
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")

    new_status = payload.status
    reason = payload.reason
    if new_status not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status")

    doc = db.query(Document).filter(Document.id == document_id, Document.is_deleted.is_(False)).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    old_status = doc.status
    doc.status = new_status
    db.add(doc)

    history = DocumentStatusHistory(
        document_id=doc.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=current_user.id,
        reason=reason,
    )
    db.add(history)
    db.commit()
    db.refresh(doc)

    if new_status == "approved":
        background_tasks.add_task(log_approval, doc.id, current_user.email)

    cache.delete("approved_documents")
    cache.delete("admin_stats")
    return doc


@router.delete("/{document_id}")
def soft_delete_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.is_deleted.is_(False)).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not _is_admin(current_user) and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    doc.is_deleted = True
    doc.deleted_at = datetime.now(timezone.utc)
    db.commit()
    cache.delete("approved_documents")
    cache.delete("admin_stats")
    return {"message": "Document deleted"}


@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.is_deleted.is_(False)).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status != "approved":
        raise HTTPException(status_code=403, detail="Document not approved")

    if not _is_admin(current_user) and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return FileResponse(path=doc.file_path, media_type=doc.content_type, filename=doc.filename)


@router.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Robust admin check (avoids role case/space issues)
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")

    cached = cache.get("admin_stats")
    if cached:
        return cached

    data = {
        "total": db.query(Document).filter(Document.is_deleted.is_(False)).count(),
        "pending": db.query(Document).filter(Document.status == "pending", Document.is_deleted.is_(False)).count(),
        "approved": db.query(Document).filter(Document.status == "approved", Document.is_deleted.is_(False)).count(),
        "rejected": db.query(Document).filter(Document.status == "rejected", Document.is_deleted.is_(False)).count(),
    }
    cache.set("admin_stats", data)
    return data