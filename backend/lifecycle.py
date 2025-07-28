from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
import sys
from loguru import logger

from scheduler import LinksScheduler
from config.settings import settings

# 全局调度器实例
video_scheduler: LinksScheduler = None


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """配置 Loguru 日志系统。"""
    logger.remove()
    logger.add(
        sys.stderr, level=settings.LOG_LEVEL, format=settings.LOG_FORMAT, colorize=True
    )
    log_file_path = settings.LOG_DIR / "{time:YYYY-MM-DD}.log"
    logger.add(
        log_file_path,
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    for name in logging.root.manager.loggerDict:
        if name.startswith("uvicorn"):
            logging.getLogger(name).handlers = [InterceptHandler()]
            logging.getLogger(name).propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    setup_logging()
    logger.info("Logging system initialized.")
    logger.info("Application starting up...")

    # 启动时执行
    global video_scheduler

    # 初始化调度器
    if settings.PIKPAK_USERNAME and settings.PIKPAK_PASSWORD:
        try:
            video_scheduler = LinksScheduler(
                settings.PIKPAK_USERNAME, settings.PIKPAK_PASSWORD
            )
            await video_scheduler.start()
            print("生命周期--------链接调度器已启动")
        except Exception as e:
            print(f"生命周期--------调度器启动失败: {str(e)}")
            video_scheduler = None
    else:
        print("   未配置 PikPak 账号，跳过调度器启动")
        print("   请设置环境变量: PIKPAK_USERNAME 和 PIKPAK_PASSWORD")

    yield

    # 关闭时清理
    if video_scheduler:
        await video_scheduler.stop()
        print("生命周期--------视频链接调度器已停止")


def setup_lifespan(app: FastAPI):
    """为应用设置生命周期"""
    app.router.lifespan_context = lifespan
