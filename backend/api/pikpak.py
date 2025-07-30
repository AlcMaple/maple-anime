"""
PikPak相关路由
"""

from fastapi import APIRouter, HTTPException

from services.pikpak import PikPakService
from database.pikpak import PikPakDatabase
from config.settings import settings
from schemas.pikpak import (
    DownloadRequest,
    PikPakCredentials,
    UpdateAnimeRequest,
    VideoUrlUpdateRequest,
    DeleteAnimeRequest,
)
from exceptions import ValidationException, SystemException
from utils.responses import success

router = APIRouter(prefix="/pikpak", tags=["PikPak"])


@router.post("/batch-download")
async def batch_download_anime(request: DownloadRequest):
    """批量下载动漫"""
    try:
        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)

        # 处理单季动漫
        if request.mode == "single_season" and request.anime_list:
            result = await pikpak_service.batch_download_selected(
                client, request.anime_list, request.title
            )

            if not result["success"]:
                raise SystemException(
                    message="下载失败", original_error=result["message"]
                )

            return success(result, "批量下载动漫成功")

        # 处理多季动漫
        elif request.mode == "multi_season" and request.groups:
            result = {}
            # 遍历每一季
            for group in request.groups:
                # 调用下载 api
                result = await pikpak_service.batch_download_selected(
                    client, group.anime_list, group.title
                )

                if not result["success"]:
                    # 如果任何一个失败，立即抛出异常
                    raise SystemException(
                        message="下载失败", original_error=result["message"]
                    )

            return success(result, "批量下载动漫成功")

        else:
            raise ValidationException("请选择下载的动漫")

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="下载动漫失败", original_error=e)


@router.post("/sync")
async def sync_pikpak_data(credentials: PikPakCredentials):
    """同步PikPak数据"""
    try:
        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(
            credentials.username, credentials.password
        )

        success = await pikpak_service.sync_data(client)

        if success:
            return {"success": True, "message": "同步成功"}
        else:
            return {"success": False, "message": "同步失败"}

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="同步PikPak数据失败", original_error=e)


@router.post("/update-links")
async def update_anime_links(request: VideoUrlUpdateRequest):
    """更新指定动漫的播放链接"""
    try:
        if not request.username or not request.password:
            raise ValidationException("请配置PikPak账号密码")

        if not request.folder_id:
            raise ValidationException("请指定动漫")

        if not request.file_ids or len(request.file_ids) == 0:
            raise ValidationException("请指定要更新连接的视频")

        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)
        anime_db = PikPakDatabase()

        # 批量更新视频链接
        success_count = 0
        failed_count = 0
        results = []

        for file_id in request.file_ids:
            try:
                # 获取视频播放链接
                try:
                    play_url = await pikpak_service.get_video_play_url(file_id, client)
                except SystemException:
                    raise
                except Exception as e:
                    raise SystemException(
                        message="获取视频播放链接服务异常", original_error=e
                    )

                if play_url:
                    # 更新数据库
                    try:
                        res = await anime_db.update_anime_file_link(
                            file_id,
                            play_url,
                            settings.ANIME_CONTAINER_ID,
                            request.folder_id,
                        )
                    except SystemException:
                        raise
                    except Exception as e:
                        raise SystemException(
                            message="更新动漫文件链接数据库异常", original_error=e
                        )

                    if res["success"]:
                        results.append(
                            {
                                "file_id": file_id,
                                "success": True,
                                "play_url": res["data"]["play_url"],
                                "updated_time": res["data"]["updated_time"],
                            }
                        )
                        success_count += 1
                    else:
                        results.append(
                            {
                                "file_id": file_id,
                                "success": False,
                                "message": "获取链接成功，但更新数据库失败",
                            }
                        )
                        failed_count += 1
                else:
                    results.append(
                        {
                            "file_id": file_id,
                            "success": False,
                            "message": "获取视频链接失败",
                        }
                    )
                    failed_count += 1

            except SystemException:
                raise
            except Exception as e:
                raise SystemException(
                    message=f"处理文件{file_id}时发生系统异常", original_error=e
                )

        # 如果有成功更新的文件，更新动漫文件夹的更新时间
        if success_count > 0:
            try:
                folder_update_result = await anime_db.update_anime_info(
                    request.folder_id, {}, settings.ANIME_CONTAINER_ID
                )

                # 更新视频链接时间记录
                video_time_update_result = (
                    await anime_db.update_folder_video_links_time(
                        request.folder_id, settings.ANIME_CONTAINER_ID
                    )
                )

                if folder_update_result:
                    print(f"已更新动漫文件夹的更新时间")
                if video_time_update_result:
                    print(f"已记录视频链接更新时间")

            except Exception as e:
                raise SystemException(
                    message="更新时间记录时发生系统异常", original_error=e
                )

        return {
            "success": success_count > 0,
            "message": f"更新完成: 成功 {success_count} 个，失败 {failed_count} 个",
            "data": {
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results,
            },
        }

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="更新动漫播放链接服务异常", original_error=e)


@router.post("/update-episode")
async def update_anime_episode(request: UpdateAnimeRequest):
    """更新动漫集数"""
    try:
        if not request.username or not request.password:
            raise ValidationException("请配置PikPak账号密码")

        if not request.folder_id:
            raise ValidationException("请指定动漫")

        if not request.anime_list or len(request.anime_list) == 0:
            raise ValidationException("请指定要更新的集数")

        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)

        anime_list_dict = []
        for anime in request.anime_list:
            anime_list_dict.append(
                {"id": anime.id, "title": anime.title, "magnet": anime.magnet}
            )

        try:
            result = await pikpak_service.update_anime_episodes(
                client, anime_list_dict, request.folder_id
            )
        except SystemException:
            raise
        except Exception as e:
            raise SystemException(message="更新动漫集数服务异常", original_code=e)

        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data": {
                    "added_count": result["added_count"],
                    "failed_count": result["failed_count"],
                    "folder_id": request.folder_id,
                },
            }
        else:
            raise SystemException(
                message="更新动漫集数失败", original_error=result["message"]
            )

    except SystemException:
        raise
    except Exception as e:
        raise SystemException(message="更新动漫集数服务异常", original_error=e)


@router.post("/delete-anime")
async def delete_anime(request: DeleteAnimeRequest):
    """删除动漫"""
    try:

        if not request.username or not request.password:
            raise ValidationException("请配置PikPak账号密码")

        if not request.folder_id:
            raise ValidationException("请指定要删除的动漫")

        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)

        # 直接调用PikPak API删除文件夹
        delete_result = await client.delete_to_trash(ids=[request.folder_id])

        if delete_result:
            # 同步数据以更新本地数据库
            print(f"开始同步数据以更新本地数据库...")
            sync_result = await pikpak_service.sync_data(client, blocking_wait=True)

            return {
                "success": True,
                "message": f"成功删除动漫",
                "data": {
                    "folder_id": request.folder_id,
                    "synced": sync_result,
                },
            }
        else:
            raise HTTPException(status_code=500, detail=f"删除动漫失败")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除动漫失败: {str(e)}")
