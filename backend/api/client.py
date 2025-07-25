"""
客户端路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.pikpak import PikPakDatabase
from config.settings import settings

router = APIRouter(prefix="/client", tags=["客户端"])


class SearchRequest(BaseModel):
    name: str


@router.post("/search")
async def search_client(request: SearchRequest):
    """客户端搜索动漫"""
    try:
        print("开始搜索客户端动漫：", request.name)
        anime_db = PikPakDatabase()
        result = await anime_db.search_anime_by_title(request.name)

        if result["success"]:
            return {
                "success": True,
                "data": result["data"],
                "total": result["total"],
                "keyword": result["keyword"],
                "message": result["message"],
            }
        else:
            return {
                "success": False,
                "data": [],
                "total": 0,
                "keyword": request.name,
                "message": result["message"],
            }

    except Exception as e:
        print(f"❌ 客户端搜索动漫异常: {e}")
        raise HTTPException(status_code=500, detail=f"客户端搜索动漫失败: {str(e)}")


@router.get("/anime/{anime_id}")
async def get_client_anime(anime_id: str):
    """获取客户端动漫信息"""
    try:
        print("开始获取客户端动漫信息：", anime_id)
        anime_db = PikPakDatabase()
        result = await anime_db.get_anime_all(anime_id, settings.ANIME_CONTAINER_ID)

        if result:
            return {
                "success": True,
                "data": result,
                "message": "获取客户端动漫信息成功",
            }
        else:
            return {
                "success": False,
                "data": {},
                "message": "获取客户端动漫信息失败",
            }

    except Exception as e:
        print(f"获取动漫信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取动漫信息失败: {str(e)}")
