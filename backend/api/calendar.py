"""
番剧表相关路由
"""

from fastapi import APIRouter, HTTPException
from services.bangumi import BangumiApi

router = APIRouter(prefix="/calendar", tags=["番剧表"])


@router.get("")
async def get_calendar():
    """获取当季新番信息"""
    try:
        bangumi_service = BangumiApi()
        data = await bangumi_service.load_calendar_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/update")
async def update_calendar():
    """更新当季新番信息"""
    try:
        bangumi_service = BangumiApi()
        response = await bangumi_service.get_calendar()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
