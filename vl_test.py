import base64
from zai import ZhipuAiClient

def encode_image(image_path):
    """将图像编码为 base64 格式"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

client = ZhipuAiClient(api_key="be993faeb5374db99cb1c5743d9aad6b.YjA2vQbs8hgFJjLF")

# 方式1：使用图像URL
# response = client.chat.completions.create(
#     model="glm-4.6v",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "这张图片里有什么？请详细描述。"
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "https://example.com/image.jpg"
#                     }
#                 }
#             ]
#         }
#     ]
# )

# print(response.choices[0].message.content)

# 方式2：使用base64编码的图像
base64_image = encode_image('trae_models.png')

stream = client.chat.completions.create(
    model="glm-4.6v",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "分析这张图片中的内容"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                        # "url": "https://example.com/image.jpg" # 使用URL方式
                    }
                }
            ]
        }
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='', flush=True)

print()  # 换行