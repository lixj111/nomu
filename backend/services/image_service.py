"""图片处理服务"""
import os
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

    def _get_next_file_number(self, date_dir: Path, ext: str) -> int:
        """获取下一个可用的文件编号"""
        # 获取该日期目录下所有相同扩展名的文件
        existing_files = list(date_dir.glob(f"*{ext}"))

        if not existing_files:
            return 1

        # 提取所有文件名中的数字编号
        numbers = []
        for f in existing_files:
            # 文件名格式: 1.png, 2.png, 等
            try:
                num = int(f.stem)
                numbers.append(num)
            except ValueError:
                # 如果文件名不是数字，跳过
                continue

        # 返回最大编号 + 1
        return max(numbers) + 1 if numbers else 1

    async def save_upload_file(self, file: UploadFile) -> str:
        """保存上传的文件"""
        # 读取文件内容
        content = await file.read()

        # 验证文件
        self.validate_image(file.filename or "image.jpg", len(content))

        # 获取文件扩展名
        ext = Path(file.filename or "image.jpg").suffix.lower()

        # 按日期组织目录
        date_path = datetime.now().strftime("%Y%m%d")
        date_dir = self.upload_dir / date_path
        date_dir.mkdir(exist_ok=True)

        # 获取下一个递增编号
        file_number = self._get_next_file_number(date_dir, ext)
        unique_filename = f"{file_number}{ext}"

        # 保存文件
        file_path = date_dir / unique_filename
        with open(file_path, "wb") as f:
            f.write(content)

        # 返回相对于 static 目录的路径（用于访问）
        # 例如: uploads/20260119/1.png
        return f"uploads/{date_path}/{unique_filename}"

    def get_full_path(self, relative_path: str) -> str:
        """获取文件的完整路径"""
        # relative_path 格式: uploads/20260119/xxx.png
        # self.upload_dir 是 backend/static/uploads
        # 需要回到 backend/static，然后拼接 relative_path
        static_dir = self.upload_dir.parent  # backend/static
        return str(static_dir / relative_path)

    def delete_file(self, relative_path: str) -> bool:
        """删除文件"""
        try:
            file_path = Path(self.get_full_path(relative_path))
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
