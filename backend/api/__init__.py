from fastapi import APIRouter
from .anime import router as anime_router
from .calendar import router as calendar_router
from .pikpak import router as pikpak_router
from .client import router as client_router
from .episodes import router as episodes_router

# 创建主路由
from config.settings import settings
api_router = APIRouter(prefix=settings.API_PREFIX)

# 注册子路由
api_router.include_router(anime_router)
api_router.include_router(calendar_router)
api_router.include_router(pikpak_router)
api_router.include_router(client_router)
api_router.include_router(episodes_router)

__all__ = ["api_router"]