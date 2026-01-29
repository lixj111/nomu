"""后端配置管理"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "智账-基于AI的自动记账系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API密钥
    ZHIPU_API_KEY: Optional[str] = None
    VISION_MODEL: str = "glm-4.6v"

    # 数据库配置
    DB_PATH: str = "accounting.db"

    # JWT配置
    SECRET_KEY: str = "cxx_zhizhang"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # 文件上传配置
    UPLOAD_DIR: str = "backend/static/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = [".jpg", ".jpeg", ".png", ".webp"]

    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # 识别配置
    CONFIDENCE_THRESHOLD: float = 0.7
    AUTO_SAVE: bool = True

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "accounting.log"

    # HTTP 超时配置
    API_TIMEOUT: int = 300  # API 请求超时时间（秒），默认 5 分钟

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# 全局配置实例
settings = Settings()

# 确保上传目录存在
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
