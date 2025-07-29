"""
番剧表相关路由
"""

from fastapi import APIRouter
from loguru import logger

from services.bangumi import BangumiApi
from exceptions import SystemException
from utils.responses import success

router = APIRouter(prefix="/calendar", tags=["番剧表"])


@router.get("")
async def get_calendar():
    """获取当季新番信息"""
    try:
        bangumi_service = BangumiApi()
        data = await bangumi_service.load_calendar_data()
        return success(data, msg="获取番剧表成功")

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="获取番剧表失败", original_error=e)


@router.get("/update")
async def update_calendar():
    """更新当季新番信息"""
    try:
        bangumi_service = BangumiApi()
        response = await bangumi_service.get_calendar()
        return success(response, msg="更新番剧表成功")
    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="更新番剧表失败", original_error=e)
