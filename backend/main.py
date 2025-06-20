import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import traceback
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import httpx
from pikpakapi import PikPakApi
from apis.anime_garden_api import AnimeSearch
from apis.pikpak_api import PikPakService
from apis.bangumi_api import BangumiApi
from database.pikpak import PikPakDatabase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

ANIME_CONTAINER_ID = "VOQqzYAEiKo3JmMhSvj6UYvto2"


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

        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)

        result = await pikpak_service.rename_single_file(
            client, request.file_id, request.new_name, request.folder_id
        )

        if result:
            # 更新数据库
            anime_db = PikPakDatabase()
            res = await anime_db.rename_anime_file(
                request.file_id, request.new_name, ANIME_CONTAINER_ID
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
        return {"success": True, "message": "同步数据成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步数据失败: {str(e)}")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    main()
