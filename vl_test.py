import base64
import json
import time
from zai import ZhipuAiClient


class VisionAnalyzer:
    """视觉模型分析器封装"""

    def __init__(self, api_key: str, model: str = "glm-4.6v"):
        """初始化分析器

        Args:
            api_key: 智谱AI API密钥
            model: 使用的模型名称，默认为 glm-4.6v
        """
        self.client = ZhipuAiClient(api_key=api_key)
        self.model = model

    @staticmethod
    def encode_image(image_path: str) -> str:
        """将图像编码为 base64 格式

        Args:
            image_path: 图像文件路径

        Returns:
            base64 编码的字符串
        """
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image(
        self,
        image_input: str,
        prompt: str = "分析这张图片中的内容",
        use_base64: bool = True
    ):
        """分析图像内容

        Args:
            image_input: 图像路径（本地文件）或 URL
            prompt: 分析提示词
            use_base64: 是否使用 base64 编码（False 则使用 URL）

        Returns:
            完整的模型响应对象
        """
        # 准备图像 URL
        if use_base64:
            base64_image = self.encode_image(image_input)
            image_url = f"data:image/jpeg;base64,{base64_image}"
        else:
            image_url = image_input

        # 构建消息
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]

        # 调用模型
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )

        return response

    def analyze_image_structured(
        self,
        image_input: str,
        prompt: str,
        schema: dict,
        use_base64: bool = True
    ) -> dict:
        """分析图像并返回结构化结果

        Args:
            image_input: 图像路径（本地文件）或 URL
            prompt: 分析提示词
            schema: 期望的 JSON 结构 schema
            use_base64: 是否使用 base64 编码

        Returns:
            解析后的结构化数据（字典格式）

        Example:
            schema = {
                "type": "object",
                "properties": {
                    "objects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "count": {"type": "integer"}
                            }
                        }
                    }
                }
            }
        """
        # 准备图像 URL
        if use_base64:
            base64_image = self.encode_image(image_input)
            image_url = f"data:image/jpeg;base64,{base64_image}"
        else:
            image_url = image_input

        # 添加 JSON 格式要求到提示词
        json_prompt = f"""{prompt}

请严格按照以下 JSON 格式返回结果，不要包含任何其他文字说明：
```json
{json.dumps(schema, ensure_ascii=False, indent=2)}
```"""

        # 构建消息
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": json_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]

        # 调用模型（非流式）
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )

        # 解析 JSON 响应
        content = response.choices[0].message.content

        # 提取 JSON 内容（处理可能的 markdown 代码块）
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()

        return json.loads(json_str)


def main():
    """主函数示例"""
    # 初始化分析器
    analyzer = VisionAnalyzer(
        api_key="be993faeb5374db99cb1c5743d9aad6b.YjA2vQbs8hgFJjLF"
    )

    # ========== 示例 1: 普通分析输出 ==========
    print("=== 示例 1: 普通分析输出 ===")
    start_time = time.time()

    response = analyzer.analyze_image(
        image_input='trae_models.png',
        prompt="分析这张图片中的内容",
        use_base64=True
    )

    elapsed_time = time.time() - start_time
    print(response.choices[0].message.content)
    print(f"\n⏱️  耗时: {elapsed_time:.2f} 秒\n")

    # ========== 示例 2: 结构化输出（图片分类） ==========
    print("=== 示例 2: 结构化输出 - 图片分类 ===")

    # 定义期望的 JSON 结构
    classification_schema = {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "图片主要类别",
                "enum": ["人物", "风景", "动物", "建筑", "物品", "文档", "其他"]
            },
            "confidence": {
                "type": "number",
                "description": "置信度 (0-1)"
            },
            "description": {
                "type": "string",
                "description": "简要描述"
            }
        },
        "required": ["category", "confidence", "description"]
    }

    start_time = time.time()
    result = analyzer.analyze_image_structured(
        image_input='trae_models.png',
        prompt="请对这张图片进行分类",
        schema=classification_schema
    )
    elapsed_time = time.time() - start_time

    print("分类结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n⏱️  耗时: {elapsed_time:.2f} 秒\n")

    # ========== 示例 3: 结构化输出（物体检测） ==========
    print("=== 示例 3: 结构化输出 - 物体检测 ===")

    detection_schema = {
        "type": "object",
        "properties": {
            "total_objects": {
                "type": "integer",
                "description": "检测到的物体总数"
            },
            "objects": {
                "type": "array",
                "description": "检测到的物体列表",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "物体名称"
                        },
                        "count": {
                            "type": "integer",
                            "description": "数量"
                        },
                        "color": {
                            "type": "string",
                            "description": "主要颜色"
                        },
                        "position": {
                            "type": "string",
                            "description": "位置信息"
                        }
                    },
                    "required": ["name", "count"]
                }
            }
        },
        "required": ["total_objects", "objects"]
    }

    start_time = time.time()
    detection_result = analyzer.analyze_image_structured(
        image_input='yolo11.jpg',
        prompt="检测图片中的所有物体并统计数量",
        schema=detection_schema
    )
    elapsed_time = time.time() - start_time

    print("检测结果:")
    print(json.dumps(detection_result, ensure_ascii=False, indent=2))
    print(f"\n⏱️  耗时: {elapsed_time:.2f} 秒\n")

    # ========== 示例 4: 结构化输出（文字识别） ==========
    print("=== 示例 4: 结构化输出 - 文字识别 ===")

    ocr_schema = {
        "type": "object",
        "properties": {
            "has_text": {
                "type": "boolean",
                "description": "是否包含文字"
            },
            "text_regions": {
                "type": "array",
                "description": "文字区域列表",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "识别的文字内容"
                        },
                        "language": {
                            "type": "string",
                            "description": "文字语言"
                        },
                        "position": {
                            "type": "string",
                            "description": "文字位置"
                        }
                    }
                }
            },
            "total_text_count": {
                "type": "integer",
                "description": "文字总数"
            }
        },
        "required": ["has_text"]
    }

    start_time = time.time()
    ocr_result = analyzer.analyze_image_structured(
        image_input='trae_models.png',
        prompt="识别图片中的所有文字内容",
        schema=ocr_schema
    )
    elapsed_time = time.time() - start_time

    print("文字识别结果:")
    print(json.dumps(ocr_result, ensure_ascii=False, indent=2))
    print(f"\n⏱️  耗时: {elapsed_time:.2f} 秒")


if __name__ == "__main__":
    main()