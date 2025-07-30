"""
集数管理路由
"""

from fastapi import APIRouter
from loguru import logger

from services.pikpak import PikPakService
from database.pikpak import PikPakDatabase
from config.settings import settings
from schemas.episodes import EpisodeListRequest, FileDeleteRequest, FileRenameRequest
from exceptions import SystemException, ValidationException

router = APIRouter(prefix="/episodes", tags=["集数管理"])


@router.post("/list")
async def get_episode_list(request: EpisodeListRequest):
    """获取动漫文件夹内的所有集数"""
    try:
        if not request.folder_id:
            raise ValidationException("请指定动漫")

        anime_db = PikPakDatabase()
        result = anime_db.load_data()

        # 获取json中对应文件夹的集数
        episode_list = (
            result.get("animes", {})
            .get(settings.ANIME_CONTAINER_ID, {})
            .get(request.folder_id, {})
            .get("files", [])
        )

        logger.info("获取集数：", len(episode_list))

        if episode_list:
            return {
                "success": True,
                "data": episode_list,
                "total": len(episode_list),
                "message": "获取集数列表成功",
            }
        else:
            return {
                "success": True,
                "data": [],
                "total": 0,
                "message": "暂无集数",
            }

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="获取集数列表失败", original_error=e)


@router.post("/delete")
async def delete_episodes(request: FileDeleteRequest):
    """批量删除集数文件"""
    try:
        if not request.username or not request.password:
            raise ValidationException("请配置 pikpak 账号密码")

        if not request.file_ids or len(request.file_ids) == 0:
            raise ValidationException("请选择要删除的动漫")

        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)

        result = await pikpak_service.batch_delete_files(client, request.file_ids)

        if result["success"]:
            # 同步数据以更新本地数据库
            logger.info(f" 开始同步数据以更新本地数据库...")
            sync_result = await pikpak_service.sync_data(client, blocking_wait=True)

            return {
                "success": True,
                "message": result["message"],
                "deleted_count": result["deleted_count"],
                "failed_count": result["failed_count"],
                "synced": sync_result,
            }
        else:
            raise SystemException(
                message="删除集数失败", original_error=result["message"]
            )

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="删除集数失败", original_error=e)


@router.post("/rename")
async def rename_episode(request: FileRenameRequest):
    """重命名单个集数文件"""
    try:
        if not request.username or not request.password:
            raise ValidationException("请配置 pikpak 账号密码")

        if not request.file_id or not request.new_name:
            raise ValidationException("请指定某个动漫文件和新名称")

        try:
            pikpak_service = PikPakService()
            client = await pikpak_service.get_client(request.username, request.password)
            result = await pikpak_service.rename_single_file(
                client, request.file_id, request.new_name
            )
            if not result:
                raise SystemException(
                    message="文件重命名失败",
                    original_error=f"文件 {request.file_id} 不存在或者 pikpak 服务异常或者代码内部逻辑出错",
                )
        except SystemException:
            raise
        except Exception as e:
            raise SystemException(message="文件重命名失败", original_error=e)
        print("重命名成功，开始更新本地数据库……")
        if result:
            # 更新数据库
            anime_db = PikPakDatabase()
            res = await anime_db.rename_anime_file(
                request.file_id,
                request.new_name,
                settings.ANIME_CONTAINER_ID,
                request.folder_id,
            )

            if res:
                return {"success": True, "message": "文件重命名成功"}
            return {"success": False, "message": "文件重命名成功，但更新数据库失败"}
        else:
            raise SystemException(
                message="文件重命名失败",
                original_error="代码内部逻辑出错或者数据库没有该动漫",
            )

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="文件重命名失败", original_error=e)
