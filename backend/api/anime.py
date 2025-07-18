"""
动漫相关路由
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

from services.anime import AnimeSearch
from services.bangumi import BangumiApi
from database.pikpak import PikPakDatabase
from config.settings import settings

router = APIRouter(prefix="/anime", tags=["动漫"])


class SearchRequest(BaseModel):
    name: str


class AnimeInfoRequest(BaseModel):
    id: str
    title: str
    status: str
    summary: Optional[str] = None
    cover_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class AnimeItem(BaseModel):
    id: int
    title: str
    magnet: str


class SeasonGroup(BaseModel):
    title: str
    anime_list: List[AnimeItem]


@router.post("/search")
async def search(request: SearchRequest):
    """搜索动漫资源"""
    try:
        if not request.name:
            raise HTTPException(status_code=400, detail="请输入动漫名称")

        anime_search = AnimeSearch()
        data = await anime_search.search_anime(request.name)

        if not data:
            return {
                "success": False,
                "data": [],
                "total": 0,
                "message": f"未找到 {request.name} 相关资源",
            }
        return data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/list")
async def get_anime_list():
    """获取动漫列表"""
    try:
        db = PikPakDatabase()
        result = db.load_data()

        # 解析成表格需要的数据
        animes_container = result.get("animes", {}).get(settings.ANIME_CONTAINER_ID, {})

        anime_list = []
        for anime_id, anime_info in animes_container.items():
            anime_list.append(
                {
                    "id": anime_id,
                    "title": anime_info.get("title", ""),
                    "status": anime_info.get("status", "连载"),
                    "cover_url": anime_info.get("cover_url", ""),
                }
            )

        return {
            "success": True,
            "data": anime_list,
            "total": len(anime_list),
            "message": "获取动漫列表成功",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取动漫列表失败: {str(e)}")


@router.post("/info")
async def get_anime_info(request: SearchRequest):
    """获取动漫信息（从Bangumi）"""
    try:
        if not request.name:
            raise HTTPException(status_code=400, detail="请指定动漫名称")

        bangumi_api = BangumiApi()
        result = await bangumi_api.search_anime_by_title(request.name)

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
        print(f"❌ Bangumi获取动漫信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取动漫信息失败: {str(e)}")


@router.post("/info/id")
async def get_anime_info_by_id(request: AnimeInfoRequest):
    """根据ID获取动漫信息（从本地数据库）"""
    try:
        anime_db = PikPakDatabase()
        anime_info = anime_db.get_anime_detail(request.id, settings.ANIME_CONTAINER_ID)

        if anime_info:
            return {
                "success": True,
                "data": anime_info,
                "message": f"获取到 {request.title} 信息",
            }
        else:
            return {
                "success": False,
                "data": {},
                "message": f"未找到 {request.title} 信息",
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取动漫信息失败: {str(e)}")


@router.post("/info/save")
async def save_anime_info(request: AnimeInfoRequest):
    """更新动漫信息"""
    try:
        from services.pikpak import PikPakService

        # 获取更新前的动漫信息
        anime_db = PikPakDatabase()
        old_anime_info = anime_db.get_anime_detail(
            request.id, settings.ANIME_CONTAINER_ID
        )

        # 检查标题是否一致
        if old_anime_info.get("title") != request.title:
            pikpak_service = PikPakService()
            client = await pikpak_service.get_client(request.username, request.password)
            result = await pikpak_service.rename_folder(
                client, request.id, request.title
            )
            if not result:
                raise HTTPException(status_code=500, detail=f"重命名失败: {result}")

        # 更新数据库
        result = await anime_db.update_anime_info(
            request.id,
            {
                "title": request.title,
                "status": request.status,
                "summary": request.summary or "",
                "cover_url": request.cover_url or "",
            },
            settings.ANIME_CONTAINER_ID,
        )

        if result:
            return {
                "success": True,
                "data": result,
                "message": f"更新 {request.title} 成功",
            }
        else:
            return {
                "success": False,
                "data": {},
                "message": f"更新 {request.title} 失败",
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新动漫信息失败: {str(e)}")
