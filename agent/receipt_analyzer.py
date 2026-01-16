"""账单分析器"""
import os
from typing import Optional, Dict

from vl_test import VisionAnalyzer
from .schemas import RECEIPT_SCHEMA, RECEIPT_ANALYSIS_PROMPT


class ReceiptAnalyzer:
    """账单分析器"""

    def __init__(self, api_key: str, model: str = "glm-4.6v"):
        """
        初始化账单分析器

        Args:
            api_key: 智谱AI API密钥
            model: 使用的模型名称
        """
        self.vision_analyzer = VisionAnalyzer(api_key=api_key, model=model)

    def analyze_receipt(
        self,
        image_path: str,
        use_base64: bool = True
    ) -> Optional[Dict]:
        """
        分析账单图片

        Args:
            image_path: 账单图片路径
            use_base64: 是否使用base64编码

        Returns:
            识别结果字典，如果识别失败返回None
        """
        try:
            # 验证图片存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")

            # 调用视觉模型进行结构化识别
            result = self.vision_analyzer.analyze_image_structured(
                image_input=image_path,
                prompt=RECEIPT_ANALYSIS_PROMPT,
                schema=RECEIPT_SCHEMA,
                use_base64=use_base64
            )

            # 验证必需字段
            if not result.get("success"):
                return None

            # 置信度检查
            if result.get("confidence", 0) < 0.5:
                print(f"警告: 识别置信度较低 ({result.get('confidence')})，请人工核对")

            return result

        except Exception as e:
            print(f"账单分析失败: {str(e)}")
            return None

    def batch_analyze_receipts(
        self,
        image_paths: list,
        use_base64: bool = True
    ) -> Dict[str, Optional[Dict]]:
        """
        批量分析账单

        Args:
            image_paths: 图片路径列表
            use_base64: 是否使用base64编码

        Returns:
            字典，键为图片路径，值为识别结果
        """
        results = {}
        for image_path in image_paths:
            results[image_path] = self.analyze_receipt(image_path, use_base64)
        return results
