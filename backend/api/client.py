"""
客户端路由
"""

from fastapi import APIRouter
from loguru import logger

from database.pikpak import PikPakDatabase
from config.settings import settings
from schemas.client import SearchRequest
from exceptions import SystemException
from utils.responses import success

router = APIRouter(prefix="/client", tags=["客户端"])


@router.post("/search")
async def search_client(request: SearchRequest):
    """客户端搜索动漫"""
    try:
        logger.debug(f"客户端开始搜索动漫：{request.name}")
        anime_db = PikPakDatabase()
        result = await anime_db.search_anime_by_title(request.name)

        return success(result, msg="搜索客户端动漫成功")

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="搜索客户端动漫失败", original_error=e)


@router.get("/anime/{anime_id}")
async def get_client_anime(anime_id: str):
    """获取客户端动漫信息"""
    try:
        logger.debug(f"获取客户端动漫信息：{anime_id}")
        anime_db = PikPakDatabase()
        result = await anime_db.get_anime_all(anime_id, settings.ANIME_CONTAINER_ID)

        return success(result, msg="获取客户端动漫信息成功")

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="获取客户端动漫信息失败", original_error=e)
