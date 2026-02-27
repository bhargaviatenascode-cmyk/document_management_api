from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging_config import setup_logging
from app.middleware.request_logging import log_requests
from app.routes.api_v1 import api_router

settings = get_settings()
setup_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.middleware("http")(log_requests)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.now(timezone.utc).isoformat()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "timestamp": datetime.now(timezone.utc).isoformat()},
    )
