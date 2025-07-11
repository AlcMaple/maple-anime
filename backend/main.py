import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import traceback
import logging
import asyncio
import time
from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import httpx
from pikpakapi import PikPakApi
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from scheduler import LinksScheduler
from apis.anime_garden_api import AnimeSearch
from apis.pikpak_api import PikPakService
from apis.bangumi_api import BangumiApi
from database.pikpak import PikPakDatabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 应用生命周期管理"""
    global video_scheduler

    # 加载 .env 文件
    load_dotenv()

    # 初始化调度器
    pikpak_username = os.getenv("PIKPAK_USERNAME")
    pikpak_password = os.getenv("PIKPAK_PASSWORD")

    if pikpak_username and pikpak_password:
        try:
            video_scheduler = LinksScheduler(pikpak_username, pikpak_password)
            await video_scheduler.start()
            print("链接调度器已启动")
        except Exception as e:
            print(f"调度器启动失败: {str(e)}")
            video_scheduler = None
    else:
        print("未配置 PikPak 账号，跳过调度器启动")
        print("   请设置环境变量: PIKPAK_USERNAME 和 PIKPAK_PASSWORD")

    yield

    # 关闭时清理
    if video_scheduler:
        await video_scheduler.stop()
        print("动态视频链接调度器已停止")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

ANIME_CONTAINER_ID = "VOQqzYAEiKo3JmMhSvj6UYvto2"

# 调度器实例
video_scheduler: LinksScheduler = None


class SearchRequest(BaseModel):
    name: str


class SearchIdRequest(BaseModel):
    id: str


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


class DownloadRequest(BaseModel):
    username: str
    password: str
    mode: str
    title: Optional[str] = None
    anime_list: Optional[List[AnimeItem]] = None
    groups: Optional[List[SeasonGroup]] = None


class PikPakCredentialsRequest(BaseModel):
    username: str
    password: str
    file_ids: Optional[List[str]] = None
    folder_id: Optional[str] = None


class EpisodeListRequest(BaseModel):
    folder_id: str


class FileDeleteRequest(BaseModel):
    username: str
    password: str
    file_ids: List[str]
    folder_id: str


class FileRenameRequest(BaseModel):
    username: str
    password: str
    file_id: str
    new_name: str
    folder_id: str


class UpdateAnimeRequest(BaseModel):
    username: str
    password: str
    folder_id: str
    anime_list: List[AnimeItem]


class DeleteAnimeRequest(BaseModel):
    username: str
    password: str
    folder_id: str


@app.post("/api/search")
async def search_anime(request: SearchRequest):
    try:
        anime_search = AnimeSearch()
        data = await anime_search.search_anime(request.name)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/download")
async def download_anime(request: DownloadRequest):
    """
    下载动漫到PikPak
    """
    try:
        # 验证请求数据
        if not request.username or not request.password:
            raise HTTPException(status_code=400, detail="请配置pikpak账号密码")

        if request.groups is None and request.anime_list is None:
            raise HTTPException(status_code=400, detail="请选择下载的动漫")

        pikpak_service = PikPakService()
        # 获取pikpak客户端
        client = await pikpak_service.get_client(request.username, request.password)
        result = {}

        if request.mode == "single_season":
            # 单季动漫下载
            anime_list = []
            for anime in request.anime_list:
                anime_list.append(
                    {"id": anime.id, "title": anime.title, "magnet": anime.magnet}
                )

            # 调用下载 api
            result = await pikpak_service.batch_download_selected(
                client, anime_list, request.title
            )

            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])

        else:
            # 多季动漫下载
            for group in request.groups:
                anime_list = []
                for anime in group.anime_list:
                    anime_list.append(
                        {"id": anime.id, "title": anime.title, "magnet": anime.magnet}
                    )

                # 调用下载 api
                result = await pikpak_service.batch_download_selected(
                    client, anime_list, group.title
                )

                if not result["success"]:
                    raise HTTPException(status_code=500, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@app.get("/api/calendar")
async def get_calendar():
    """
    获取当季新番信息
    """
    try:
        bangumi_servers = BangumiApi()
        data = await bangumi_servers.load_calendar_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calendar/update")
async def update_calendar():
    """
    更新当季新番信息
    """
    try:
        bangumi_servers = BangumiApi()
        response = await bangumi_servers.get_calendar()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/anime/list")
async def get_anime_list():
    """
    获取动漫列表
    """
    try:
        db = PikPakDatabase()
        result = db.load_data()
        # 解析成表格需要的数据
        anime_list = []

        # 遍历所有动漫数据
        animes_container = result.get("animes", {}).get(ANIME_CONTAINER_ID, {})

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


@app.post("/api/anime/info")
async def get_anime_info(request: SearchRequest):
    """
    获取动漫信息
    """
    try:
        if not request.name:
            raise HTTPException(status_code=400, detail="请指定动漫名称")

        banguimi_api = BangumiApi()
        result = await banguimi_api.search_anime_by_title(request.name)
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


@app.post("/api/anime/info/id")
async def get_anime_info_by_id(request: AnimeInfoRequest):
    """
    根据id从 data/anime.json中获取动漫信息
    """
    try:
        anime_db = PikPakDatabase()
        anime_info = anime_db.get_anime_detail(request.id, ANIME_CONTAINER_ID)
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


@app.post("/api/anime/info/save")
async def save_anime_info(request: AnimeInfoRequest):
    """
    更新动漫信息
    """
    try:
        # print("获取前端数据", request.dict())
        # 获取更新前的动漫信息
        anime_db = PikPakDatabase()
        old_anime_info = anime_db.get_anime_detail(request.id, ANIME_CONTAINER_ID)

        # 检查标题是否一致，不一致就调用 pikpak api 重命名文件夹
        print("判断是否需要重命名文件夹", old_anime_info.get("title") == request.title)
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
            ANIME_CONTAINER_ID,
        )
        if result:
            return {
                "success": True,
                "message": f"更新 {request.title} 信息成功",
            }
        else:
            return {
                "success": False,
                "message": f"更新 {request.title} 信息失败",
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新动漫信息失败: {str(e)}")


@app.post("/api/episodes/list")
async def get_episode_list(request: EpisodeListRequest):
    """
    获取动漫文件夹内的所有集数
    """
    try:
        if not request.folder_id:
            raise HTTPException(status_code=400, detail="请指定文件夹ID")

        anime_db = PikPakDatabase()
        result = anime_db.load_data()
        # 获取 json 中对应文件夹的集数
        episode_list = (
            result.get("animes", {})
            .get(ANIME_CONTAINER_ID, {})
            .get(request.folder_id, {})
            .get("files", [])
        )

        print("获取集数：", len(episode_list))

        if episode_list:
            return {
                "success": True,
                "data": episode_list,
                "total": len(episode_list),
                "message": "获取集数列表成功",
            }
        else:
            raise HTTPException(status_code=500, detail="获取集数列表失败")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取集数列表失败: {str(e)}")


@app.post("/api/episodes/delete")
async def delete_episodes(request: FileDeleteRequest):
    """
    批量删除集数文件
    """
    try:
        if not request.username or not request.password:
            raise HTTPException(status_code=400, detail="请配置PikPak账号密码")

        if not request.file_ids or len(request.file_ids) == 0:
            raise HTTPException(status_code=400, detail="请选择要删除的文件")

        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)

        result = await pikpak_service.batch_delete_files(client, request.file_ids)

        if result["success"]:

            # 更新数据库
            anime_db = PikPakDatabase()
            res = await anime_db.del_anime_files(
                request.folder_id, {"files": []}, ANIME_CONTAINER_ID
            )

            if res:
                return {
                    "success": True,
                    "message": result["message"],
                    "deleted_count": result["deleted_count"],
                    "failed_count": result["failed_count"],
                }
            else:
                return {
                    "success": False,
                    "message": "删除文件成功，但更新数据库失败",
                    "deleted_count": result["deleted_count"],
                    "failed_count": result["failed_count"],
                }
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")


@app.post("/api/episodes/rename")
async def rename_episode(request: FileRenameRequest):
    """
    重命名单个集数文件
    """
    try:
        if not request.username or not request.password:
            raise HTTPException(status_code=400, detail="请配置PikPak账号密码")

        if not request.file_id or not request.new_name:
            raise HTTPException(status_code=400, detail="请指定文件ID和新文件名")

        # pikpak_service = PikPakService()
        # client = await pikpak_service.get_client(request.username, request.password)

        # result = await pikpak_service.rename_single_file(
        #     client, request.file_id, request.new_name
        # )
        result = True

        print("重命名成功，开始更新本地数据库……")
        if result:
            # 更新数据库
            anime_db = PikPakDatabase()
            res = await anime_db.rename_anime_file(
                request.file_id, request.new_name, ANIME_CONTAINER_ID, request.folder_id
            )

            if res:
                return {"success": True, "message": "文件重命名成功"}
            return {"success": False, "message": "文件重命名成功，但更新数据库失败"}
        else:
            raise HTTPException(status_code=500, detail="文件重命名失败")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重命名文件失败: {str(e)}")


@app.post("/api/sync")
async def syn_data(request: PikPakCredentialsRequest):
    """
    同步数据
    """
    try:
        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)
        await pikpak_service.sync_data(client, blocking_wait=True)

        # 同步后重新初始化调度器
        if video_scheduler:
            try:
                await video_scheduler.reinitialize()
                print("同步后已重新初始化调度任务")
            except Exception as scheduler_error:
                print(f"重新初始化调度失败: {str(scheduler_error)}")

        return {"success": True, "message": "同步数据成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步数据失败: {str(e)}")


@app.post("/api/video/url")
async def update_link(request: PikPakCredentialsRequest):
    """
    更新链接
    """
    try:
        if not request.file_ids or len(request.file_ids) == 0:
            raise HTTPException(status_code=400, detail="请指定要更新连接的文件")
        if not request.folder_id:
            raise HTTPException(status_code=400, detail="请指定文件夹ID")
        if not request.username or not request.password:
            raise HTTPException(status_code=400, detail="请配置PikPak账号密码")

        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)
        anime_db = PikPakDatabase()

        api_call_count = 0
        api_batch_size = 3  # 每3个请求延时一次
        api_delay = 8  # 延时8秒

        # 批量更新视频链接
        results = []
        success_count = 0
        failed_count = 0

        for file_id in request.file_ids:
            try:
                # 获取视频播放链接
                play_url = await pikpak_service.get_video_play_url(file_id, client)
                api_call_count += 1

                if play_url:
                    # 更新数据库
                    res = await anime_db.update_anime_file_link(
                        file_id, play_url, ANIME_CONTAINER_ID, request.folder_id
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

                if api_call_count % api_batch_size == 0:
                    print(
                        f"    ⏱️  已调用 {api_call_count} 次API，延时 {api_delay} 秒..."
                    )
                    time.sleep(api_delay)

            except Exception as e:
                results.append(
                    {"file_id": file_id, "success": False, "message": str(e)}
                )
                failed_count += 1

        # 如果有成功更新的文件，更新动漫文件夹的更新时间
        if success_count > 0:
            try:
                folder_update_result = await anime_db.update_anime_info(
                    request.folder_id, {}, ANIME_CONTAINER_ID
                )

                # 更新视频链接时间记录
                video_time_update_result = (
                    await anime_db.update_folder_video_links_time(
                        request.folder_id, ANIME_CONTAINER_ID
                    )
                )

                if video_scheduler:
                    try:
                        # 重新安排该文件夹的下次更新（20小时后）
                        from datetime import datetime, timedelta

                        next_update_time = datetime.now() + timedelta(hours=20)

                        job_id = f"update_folder_{request.folder_id}"

                        # 移除旧任务
                        if video_scheduler.scheduler.get_job(job_id):
                            video_scheduler.scheduler.remove_job(job_id)

                        # 添加新任务
                        video_scheduler.scheduler.add_job(
                            func=video_scheduler._update_folder,
                            trigger="date",
                            run_date=next_update_time,
                            args=[request.folder_id],
                            id=job_id,
                            name=f"更新文件夹 {request.folder_id}",
                            replace_existing=True,
                        )

                        # 重新计算下次检查时间
                        await video_scheduler._schedule_next_check()

                        print(f"已重新安排文件夹 {request.folder_id} 的调度")
                    except Exception as scheduler_error:
                        print(f"重新安排调度失败: {str(scheduler_error)}")

                if folder_update_result:
                    print(f"已更新动漫文件夹的更新时间")
                if video_time_update_result:
                    print(f"✅ 已记录视频链接更新时间")

            except Exception as e:
                print(f"更新时间记录时发生错误:: {str(e)}")

        # 返回批量操作结果
        message = f"更新完成: 成功 {success_count} 个，失败 {failed_count} 个"

        return {
            "success": success_count > 0,
            "message": message,
            "data": {
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新链接失败: {str(e)}")


@app.post("/api/anime/update")
async def update_anime(request: UpdateAnimeRequest):
    """
    更新动漫
    """
    try:
        if not request.username or not request.password:
            raise HTTPException(status_code=400, detail="请配置PikPak账号密码")

        if not request.folder_id:
            raise HTTPException(status_code=400, detail="请指定要更新的动漫文件夹ID")

        if not request.anime_list or len(request.anime_list) == 0:
            raise HTTPException(status_code=400, detail="请选择要添加的集数")

        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)

        # 调用更新动漫方法
        result = await pikpak_service.update_anime_episodes(
            client, request.anime_list, request.folder_id
        )

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
            raise HTTPException(status_code=500, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新动漫失败: {str(e)}")


@app.post("/api/anime/delete")
async def delete_anime(request: DeleteAnimeRequest):
    """
    删除动漫
    """
    try:
        if not request.username or not request.password:
            raise HTTPException(status_code=400, detail="请配置PikPak账号密码")

        if not request.folder_id:
            raise HTTPException(status_code=400, detail="请指定要删除的动漫ID")

        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)

        delete_result = await client.delete_file(request.folder_id)

        if delete_result:
            # 同步数据以更新本地数据库
            print(f"🔄 开始同步数据以更新本地数据库...")
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


@app.post("/api/client/search")
async def search_client(request: SearchRequest):
    """
    客户端搜索动漫
    """
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
        print(f"❌ Bangumi客户端搜索动漫异常: {e}")
        raise HTTPException(status_code=500, detail=f"客户端搜索动漫失败: {str(e)}")


@app.get("/api/client/anime/{anime_id}")
async def get_client_anime(anime_id: str):
    """
    获取客户端动漫信息
    """
    try:
        print("开始获取客户端动漫信息：", anime_id)
        anime_db = PikPakDatabase()
        result = await anime_db.get_anime_all(anime_id, ANIME_CONTAINER_ID)
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


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)


if __name__ == "__main__":
    main()
