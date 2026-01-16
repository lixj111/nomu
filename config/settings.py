"""配置管理"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """应用配置"""
    # API配置
    ZHIPU_API_KEY: str
    VISION_MODEL: str = "glm-4.6v"

    # 数据库配置
    DB_PATH: str = "accounting.db"

    # 识别配置
    CONFIDENCE_THRESHOLD: float = 0.7
    AUTO_SAVE: bool = True

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "accounting.log"

    # 分类配置
    DEFAULT_CATEGORIES = [
        "餐饮", "交通", "购物", "娱乐",
        "医疗", "教育", "住房", "通讯", "其他"
    ]

    @classmethod
    def from_env(cls) -> "Settings":
        """从环境变量加载配置"""
        return cls(
            ZHIPU_API_KEY=os.getenv("ZHIPU_API_KEY", ""),
            VISION_MODEL=os.getenv("VISION_MODEL", "glm-4.6v"),
            DB_PATH=os.getenv("DB_PATH", "accounting.db"),
            CONFIDENCE_THRESHOLD=float(os.getenv("CONFIDENCE_THRESHOLD", "0.7")),
            AUTO_SAVE=os.getenv("AUTO_SAVE", "true").lower() == "true"
        )
