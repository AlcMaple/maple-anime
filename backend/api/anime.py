"""
动漫相关路由
"""

from fastapi import APIRouter

from services.anime import AnimeSearch
from services.bangumi import BangumiApi
from database.pikpak import PikPakDatabase
from config.settings import settings
from services.pikpak import PikPakService
from schemas.anime import SearchRequest, AnimeInfoRequest
from exceptions import ValidationException, SystemException, NotFoundException
from utils import success

router = APIRouter(prefix="/anime", tags=["动漫"])


@router.post("/search")
async def search(request: SearchRequest):
    """搜索动漫资源"""

    if not request.name:
        raise ValidationException("请指定动漫名称")

    anime_search = AnimeSearch()
    data = await anime_search.search_anime(request.name)

    return success(data, f"找到 {len(data)} 个 {request.name} 相关资源")


@router.get("/list")
async def get_anime_list():
    """获取动漫列表"""
    db = PikPakDatabase()
    result = db.load_data()

    # 解析成表格数据
    animes_container = result.get("animes", {}).get(settings.ANIME_CONTAINER_ID, {})

    if not animes_container:
        raise NotFoundException("动漫列表", "任何动漫")

    anime_list = []
    for anime_id, anime_info in animes_container.items():
        anime_list.append(
            {
                "id": anime_id,
                "title": anime_info.get("title", ""),
                "status": anime_info.get("status", "连载"),
                "cover_url": anime_info.get("cover_url", ""),
                "summary": anime_info.get("summary", ""),
            }
        )

    return success(anime_list, "获取动漫列表成功")


@router.post("/info")
async def get_anime_info(request: SearchRequest):
    """获取动漫信息（Bangumi）"""
    if not request.name:
        raise ValidationException("请指定动漫名称")

    bangumi_api = BangumiApi()
    result = await bangumi_api.search_anime_by_title(request.name)

    return success(result, f"找到 {len(result)} 个相关动漫")


@router.post("/info/id")
async def get_anime_info_by_id(request: AnimeInfoRequest):
    """根据ID获取动漫信息（数据库）"""
    anime_db = PikPakDatabase()
    anime_info = anime_db.get_anime_detail(request.id, settings.ANIME_CONTAINER_ID)

    if not anime_info:
        raise NotFoundException("动漫信息", f"ID: {request.id}")

    return success(anime_info, f"获取到 {request.title} 信息")


@router.post("/info/save")
async def save_anime_info(request: AnimeInfoRequest):
    """更新动漫信息"""
    try:
        # 获取更新前的动漫信息
        anime_db = PikPakDatabase()
        old_anime_info = anime_db.get_anime_detail(
            request.id, settings.ANIME_CONTAINER_ID
        )

        # 检查标题是否一致
        if old_anime_info.get("title") != request.title:
            try:
                pikpak_service = PikPakService()
                client = await pikpak_service.get_client(
                    request.username, request.password
                )
                result = await pikpak_service.rename_folder(
                    client, request.id, request.title
                )
                if not result:
                    raise SystemException(
                        message="PikPak文件夹重命名操作失败",
                        original_error=Exception(
                            f"rename_folder returned False for folder_id: {request.id}, new_name: {request.title}"
                        ),
                    )
            except SystemException:
                raise
            except Exception as e:
                raise SystemException(message="PikPak重命名服务异常", original_error=e)

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

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="动漫信息更新服务异常", original_error=e)
