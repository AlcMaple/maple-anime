"""
Maple Anime 后端服务入口
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from config.settings import settings
from middleware.cors import setup_cors
from api import api_router
from scheduler import LinksScheduler


# 全局调度器实例
video_scheduler: LinksScheduler = None


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """FastAPI 应用生命周期管理"""
#     global video_scheduler

#     # 初始化调度器
#     if settings.PIKPAK_USERNAME and settings.PIKPAK_PASSWORD:
#         try:
#             video_scheduler = LinksScheduler(
#                 settings.PIKPAK_USERNAME, settings.PIKPAK_PASSWORD
#             )
#             await video_scheduler.start()
#             print("✅ 链接调度器已启动")
#         except Exception as e:
#             print(f"❌ 调度器启动失败: {str(e)}")
#             video_scheduler = None
#     else:
#         print("⚠️  未配置 PikPak 账号，跳过调度器启动")
#         print("   请设置环境变量: PIKPAK_USERNAME 和 PIKPAK_PASSWORD")

#     yield

#     # 关闭时清理
#     if video_scheduler:
#         await video_scheduler.stop()
#         print("✅ 动态视频链接调度器已停止")


# 创建应用实例
# app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)
app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# 配置中间件
setup_cors(app)

# 注册路由
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
