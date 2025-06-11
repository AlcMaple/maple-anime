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


@app.post("/api/anime/list")
async def get_anime_list(request: PikPakCredentialsRequest):
    """
    获取动漫列表
    """
    try:
        # 验证请求数据
        if not request.username or not request.password:
            raise HTTPException(status_code=400, detail="请配置PikPak账号密码")

        # 获取 PikPak 文件夹列表
        pikpak_service = PikPakService()
        client = await pikpak_service.get_client(request.username, request.password)
        pikpak_folders = await pikpak_service.get_mypack_folder_list(client)

        # 同步数据
        anime_db = PikPakDatabase()
        anime_list = anime_db.sync_with_pikpak_folders(pikpak_folders)

        return {
            "success": True,
            "data": anime_list,
            "total": len(anime_list),
            "message": f"获取到 {len(anime_list)} 个动漫",
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
        anime_info = anime_db.get_anime_detail(request.id)
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
        # 获取更新前的动漫信息
        anime_db = PikPakDatabase()
        old_anime_info = anime_db.get_anime_detail(request.id)

        # 检查标题是否一致，不一致就调用 pikpak api 重命名文件夹
        if old_anime_info.get("title") != request.title:
            pikpak_service = PikPakService()
            client = await pikpak_service.get_client(request.username, request.password)
            result = await pikpak_service.rename_folder(
                client, request["id"], request.title
            )
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])

        # 更新数据库
        result = anime_db.update_anime_info(
            request.id,
            {
                request.title,
                request.status,
                request.summary or "",
                request.cover_url or "",
            },
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


def main():
    uvicorn.run(app, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    main()
