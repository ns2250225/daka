# 多图参考示例（Python）
import requests
import base64

API_KEY = "sk-dwI0wRUeibzNWZYMDeA400D567354d85BdF3A8BfCeBc0aD3"
API_URL = "https://api.laozhang.ai/v1beta/models/gemini-3-pro-image-preview:generateContent"

# 准备多张参考图片
image_paths = ["上传的图片"]
parts = [{"text": "请根据纬度和经度 【纬度, 经度】 的实际地点，生成符合该地点当前时间氛围与实时天气的真实照片。让指定的角色穿上合适的衣服和配饰自然融入场景，看起来像正在当地旅游。"}]

for path in image_paths:
    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    parts.append({
        "inline_data": {
            "mime_type": "image/jpeg",
            "data": image_data
        }
    })

# 发送请求
response = requests.post(
    API_URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "选择的图片比例",
                "imageSize": "1K"
            }
        }
    }
)