from fastapi import HTTPException, UploadFile

from app.core.config import get_settings


async def validate_upload_file(file: UploadFile) -> bytes:
    settings = get_settings()

    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(status_code=400, detail="File too large")
    return content
