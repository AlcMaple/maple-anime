from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from scheduler import LinksScheduler
from config.settings import settings
from utils.logs import setup_logging as setup_log_config

# 全局调度器实例
video_scheduler: LinksScheduler = None


def setup_logging():
    """配置 Loguru 日志系统。"""
    setup_log_config(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    setup_logging()

    # 启动时执行
    global video_scheduler

    # # 初始化调度器
    # if settings.PIKPAK_USERNAME and settings.PIKPAK_PASSWORD:
    #     try:
    #         video_scheduler = LinksScheduler(
    #             settings.PIKPAK_USERNAME, settings.PIKPAK_PASSWORD
    #         )
    #         await video_scheduler.start()
    #         logger.info("生命周期--------链接调度器已启动")
    #     except Exception as e:
    #         logger.error(f"生命周期--------调度器启动失败: {str(e)}")
    #         video_scheduler = None
    # else:
    #     logger.warning("未配置 PikPak 账号，跳过调度器启动")
    #     logger.warning("请设置环境变量: PIKPAK_USERNAME 和 PIKPAK_PASSWORD")

    yield

    # 关闭时清理
    if video_scheduler:
        await video_scheduler.stop()
        logger.info("生命周期--------视频链接调度器已停止")


def setup_lifespan(app: FastAPI):
    """为应用设置生命周期"""
    app.router.lifespan_context = lifespan
