"""
Maple Anime 后端服务入口
"""

import uvicorn
from fastapi import FastAPI

from config import settings
from middleware import setup_cors
from api import api_router
from lifecycle import setup_lifespan
from middleware import exception_middleware

# 创建应用实例
app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# 配置生命周期管理器
setup_lifespan(app)

# 配置中间件
setup_cors(app)

# 异常处理器中间件
exception_middleware(app)

# 注册路由
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
