from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import base64
import json

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "sk-dwI0wRUeibzNWZYMDeA400D567354d85BdF3A8BfCeBc0aD3"
API_URL = "https://api.laozhang.ai/v1beta/models/gemini-3-pro-image-preview:generateContent"

@app.post("/generate")
async def generate_photo(
    lat: float = Form(...),
    lon: float = Form(...),
    aspect_ratio: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Read and encode image
        image_content = await file.read()
        image_data = base64.b64encode(image_content).decode("utf-8")

        # Construct prompt
        prompt_text = f"请根据纬度和经度 【{lat}, {lon}】 的实际地点，生成符合该地点当前时间氛围与实时天气的真实照片。让指定的角色穿上合适的衣服和配饰自然融入场景，看起来像正在当地旅游。"

        parts = [
            {"text": prompt_text},
            {
                "inline_data": {
                    "mime_type": file.content_type or "image/jpeg",
                    "data": image_data
                }
            }
        ]

        # Prepare request payload
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio,
                    "imageSize": "1K" # As per gen.py
                }
            }
        }

        # Send request
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract image data from response
        # The response format depends on the API. 
        # Usually Gemini returns candidates -> content -> parts -> inline_data (or similar)
        # But since the script uses `responseModalities: ["IMAGE"]`, it might return the image directly or a different structure.
        # Let's inspect the structure if possible, but for now I'll assume standard Gemini structure or similar.
        # However, looking at the URL `gemini-3-pro-image-preview`, it might return a base64 string in the JSON.
        
        # If I can't be sure, I should log the response. 
        # But for now I'll return the whole JSON to the frontend and let the frontend parse it, 
        # OR I can try to parse it here.
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
