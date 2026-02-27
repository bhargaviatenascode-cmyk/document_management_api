from fastapi import APIRouter

from app.routes.api_v1.auth import router as auth_router
from app.routes.api_v1.documents import router as documents_router
from app.routes.api_v1.health import router as health_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(documents_router)
api_router.include_router(health_router)
