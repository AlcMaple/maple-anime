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


def main():
    uvicorn.run(app, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    main()
