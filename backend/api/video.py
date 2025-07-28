"""
视频代理相关路由
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.response import StreamingResponse
import httpx
import asyncio
from typing import Optional

from services.pikpak import PikPakService
from database.pikpak import PikPakDatabase
from config.settings import Settings
from exceptions import ValidationException, SystemException, NotFoundException
from utils.responses import success, server_error, not_found, bad_request
from schemas.video import ProxyVideo

router = APIRouter(prefix="/video", tags=["视频代理"])


@router.post("/proxy")
async def proxy_video(request: ProxyVideo):
    """
    视频代理 - 将 pikpak 视频流转发给客户端
    """
    if not request.file_id:
        return bad_request("需要指定播放的动漫视频")
    
    anime_db = PikPakDatabase()
    cached_url = anime_db.get_anime_file_link(request.file_id)

    if cached_url:
        pass
