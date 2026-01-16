"""图片处理服务"""
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from core.config import settings


class ImageService:
    """图片处理服务"""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_image(self, filename: str, file_size: int) -> None:
        """验证图片文件"""
        # 检查文件扩展名
        ext = Path(filename).suffix.lower()
        if ext not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的图片格式，仅支持: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
            )

        # 检查文件大小
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"图片过大，最大支持 {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
            )

    async def save_upload_file(self, file: UploadFile) -> str:
        """保存上传的文件"""
        # 读取文件内容
        content = await file.read()

        # 验证文件
        self.validate_image(file.filename or "image.jpg", len(content))

        # 生成唯一文件名
        ext = Path(file.filename or "image.jpg").suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{ext}"

        # 按日期组织目录
        date_path = datetime.now().strftime("%Y%m%d")
        date_dir = self.upload_dir / date_path
        date_dir.mkdir(exist_ok=True)

        # 保存文件
        file_path = date_dir / unique_filename
        with open(file_path, "wb") as f:
            f.write(content)

        # 返回相对路径（用于访问）
        return f"uploads/{date_path}/{unique_filename}"

    def get_full_path(self, relative_path: str) -> Path:
        """获取文件的完整路径"""
        return self.upload_dir.parent / relative_path

    def delete_file(self, relative_path: str) -> bool:
        """删除文件"""
        try:
            file_path = self.get_full_path(relative_path)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
