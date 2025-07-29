"""
日志模块
"""

import queue, sys
from collections import deque
from loguru import logger
from fastapi import WebSocket


class LogBuffer:
    """日志缓冲区"""

    def __init__(self):
        self.buffer = deque(maxlen=300)
        self.connections = set()
        self.message_queue = queue.Queue()

    def add_log(self, message):
        """添加日志"""
        formatted_message = message.strip()
        self.buffer.append(formatted_message)
        self.message_queue.put(formatted_message)

    def get_logs(self):
        """获取日志"""
        return list(self.buffer)

    def add_connection(self, connection: WebSocket):
        """添加 websocket 链接"""
        self.connections.add(connection)

    def remove_connection(self, connection: WebSocket):
        """移除 websocket 链接"""
        self.connections.discard(connection)

    def get_connetcion_count(self):
        """获取链接数量"""
        return len(self.connections)


# 日志缓冲实例
logs = LogBuffer()


def websocket_sink(message):
    """websocket 日志接收器"""
    logs.add_log(message)


def setup_logging(settings=None):
    """设置日志"""
    # 移除默认的 stderr 处理器
    logger.remove()

    # 添加控制台输出
    logger.add(sys.stderr, format=settings.CONSOLE_LOG_FORMAT, level=settings.LOG_LEVEL)

    # 是否启用WebSocket日志推送
    if settings.ENABLE_WEBSOCKET_LOGS:
        logger.add(
            websocket_sink,
            format=settings.WEBSOCKET_LOG_FORMAT,
            level=settings.LOG_LEVEL,
        )
        logger.info("WebSocket日志推送已启用")
    else:
        logger.info("WebSocket日志推送已禁用（本地开发模式）")

    # 添加文件日志
    log_file_path = settings.LOG_DIR / "{time:YYYY-MM-DD}.log"
    logger.add(
        log_file_path,
        level=settings.LOG_LEVEL,
        format=settings.CONSOLE_LOG_FORMAT,
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
