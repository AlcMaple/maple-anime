"""
日志路由
"""

from fastapi import APIRouter, WebSocket
from loguru import logger

from services.logs import LogsService
from utils.responses import success

router = APIRouter(prefix="/log", tags=["日志管理"])


@router.websocket("/ws")
async def websocket_logs(websocket: WebSocket):
    """WebSocket日志实时推送"""
    await LogsService.handle_websocket_connection(websocket)


@router.get("")
async def get_logs():
    """获取历史日志"""
    logs = LogsService.get_historical_logs()
    return success(logs, "获取日志成功")


@router.get("/status")
async def get_log_status():
    """获取日志系统状态"""
    status = LogsService.get_connection_status()
    return success(status, "获取日志系统状态成功")
