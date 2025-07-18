"""
基础设置
"""

import os
from dotenv import load_dotenv
from typing import Optional

# 加载环境变量
load_dotenv()


class Settings:
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "Maple Anime"
    VERSION: str = "1.0.0"

    # API配置
    API_PREFIX: str = "/api"

    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # PikPak配置
    PIKPAK_USERNAME: Optional[str] = os.getenv("PIKPAK_USERNAME")
    PIKPAK_PASSWORD: Optional[str] = os.getenv("PIKPAK_PASSWORD")
    ANIME_CONTAINER_ID: str = os.getenv("ANIME_CONTAINER_ID")

    # 数据库配置
    DATABASE_PATH: str = "data/anime.json"

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8002"))

    # API限流配置
    API_RATE_LIMIT: int = 13  # 每分钟请求数
    API_BATCH_SIZE: int = 3  # 批量API调用大小
    API_DELAY: int = 8  # API调用延迟(秒)


# 创建全局配置实例
settings = Settings()
