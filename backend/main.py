import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional
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
    id: str
    title: str
    magnet: str

class DownloadRequest(BaseModel):
    username: str
    password: str
    anime_list: List[AnimeItem]

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
            raise HTTPException(status_code=400, detail="PikPak账号信息不能为空")

        if not request.anime_list:
            raise HTTPException(status_code=400, detail="动漫列表不能为空")
        
        pikpak_service = PikPakService()
        print("anime_list: ", request.anime_list)

        # # 转换数据格式
        # anime_list = []
        # for anime in request.anime_list:
        #     anime_list.append(
        #         {"id": anime.id, "title": anime.title, "magnet": anime.magnet}
        #     )

        # # 批量下载
        # result = await pikpak_service.batch_download_anime(
        #     username=request.username, password=request.password, anime_list=anime_list
        # )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
