"""
日志服务层
"""

import asyncio
import queue
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from utils.logs import logs
from config.settings import settings
from exceptions.base import SystemException


class LogsService:
    """日志服务类"""

    @staticmethod
    def get_historical_logs() -> List[str]:
        """获取历史日志"""
        try:
            log = logs.get_logs()
            logger.info("Historical logs requested via API")
            return log
        except Exception as e:
            logger.error(f"Failed to get historical logs: {e}")
            raise SystemException(f"获取历史日志失败: {str(e)}")

    @staticmethod
    def check_websocket_enabled() -> bool:
        """检查WebSocket日志功能是否启用"""
        return settings.ENABLE_WEBSOCKET_LOGS

    @staticmethod
    async def handle_websocket_connection(websocket: WebSocket):
        """处理WebSocket连接的完整生命周期"""
        await websocket.accept()

        # 检查功能是否启用
        if not LogsService.check_websocket_enabled():
            await websocket.send_text("本地开发模式禁用WebSocket日志推送功能")
            await websocket.close(code=1000, reason="WebSocket logs disabled")
            return

        # 添加连接
        logs.add_connection(websocket)

        try:
            # 发送历史日志
            await LogsService._send_historical_logs(websocket)

            logger.info(
                f"New WebSocket connection established. Total connections: {logs.get_connection_count()}"
            )

            # 启动消息循环
            await LogsService._message_loop(websocket)

        except WebSocketDisconnect:
            LogsService._handle_disconnect(websocket)
        except Exception as e:
            LogsService._handle_error(websocket, e)

    @staticmethod
    async def _send_historical_logs(websocket: WebSocket):
        """发送历史日志"""
        try:
            for log_entry in logs.get_logs():
                await websocket.send_text(log_entry)
        except Exception as e:
            logger.error(f"Failed to send historical logs: {e}")
            raise SystemException(f"发送历史日志失败: {str(e)}")

    @staticmethod
    async def _message_loop(websocket: WebSocket):
        """WebSocket消息循环"""
        while True:
            try:
                # 检查新的日志消息
                await LogsService._process_new_messages(websocket)

                # 检查客户端消息
                await LogsService._check_client_messages(websocket)

                # 避免CPU占用过高
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"WebSocket message loop error: {e}")
                break

    @staticmethod
    async def _process_new_messages(websocket: WebSocket):
        """处理新的日志消息"""
        try:
            message = logs.message_queue.get_nowait()
            await websocket.send_text(message)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Failed to process new message: {e}")

    @staticmethod
    async def _check_client_messages(websocket: WebSocket):
        """检查客户端消息"""
        try:
            await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logger.error(f"Client message check error: {e}")

    @staticmethod
    def _handle_disconnect(websocket: WebSocket):
        """处理连接断开"""
        logs.remove_connection(websocket)
        logger.info(
            f"WebSocket connection closed. Remaining connections: {logs.get_connection_count()}"
        )

    @staticmethod
    def _handle_error(websocket: WebSocket, error: Exception):
        """处理连接错误"""
        logs.remove_connection(websocket)
        logger.error(f"WebSocket connection error: {error}")

    @staticmethod
    def get_connection_status() -> dict:
        """获取连接状态信息"""
        try:
            return {
                "websocket_enabled": LogsService.check_websocket_enabled(),
                "active_connections": logs.get_connection_count(),
                "log_buffer_size": len(logs.buffer),
            }
        except Exception as e:
            logger.error(f"Failed to get connection status: {e}")
            raise SystemException(f"获取连接状态失败: {str(e)}")
