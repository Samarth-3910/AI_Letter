from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import requests

app = FastAPI()

# Enable CORS for Next.js frontend
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    samples: Optional[List[str]] = []
    sample_images: Optional[List[str]] = [] # List of Base64 strings
    target_prompt: str
    api_key: Optional[str] = None

def generate_with_llm(samples: List[str], sample_images: List[str], target_prompt: str, api_key: str):
    # Construct prompt content
    contents = []
    
    system_text = (
        "You are an expert ghostwriter. Your task is to analyze the style, tone, vocabulary, and sentence structure "
        "of the provided sample letters (text and/or images) and write a NEW letter based on the user's request. "
        "The new letter MUST sound exactly like the author of the samples."
    )

    # Add Text Samples
    if samples:
        samples_text = "\n\n---\n\n".join([f"SAMPLE {i+1}:\n{s}" for i, s in enumerate(samples)])
        contents.append({"text": f"Input Text Samples:\n{samples_text}\n\n"})
    
    # Add Image Samples (Multimodal)
    if sample_images:
        contents.append({"text": "Input Image Samples (Handwritten/Printed Letters):"})
        for img_b64 in sample_images:
            # Simple handling: assume jpeg for simplicity, or strip prefix if present
            # Gemini expects pure base64 in 'data'
            if "," in img_b64:
                img_b64 = img_b64.split(",")[1]
            contents.append({
                "inline_data": {
                    "mime_type": "image/jpeg", 
                    "data": img_b64
                }
            })

    # Task Prompt
    contents.append({"text": f"\n---\nTask:\nWrite a letter for the following scenario: \"{target_prompt}\"\n\nGuidelines:\n1. Match the emotion and sentiment.\n2. Do NOT sound like an AI.\n3. If images are provided, transcribe and analyze their style primarily."})

    if not api_key:
         return "Error: API Key is required. Please enter it in settings."

    if api_key == "mock":
        return f"[MOCK OUTPUT] I have analyzed your {len(samples)} text samples and {len(sample_images)} images. Here is a draft regarding '{target_prompt}'..."

    try:
        if api_key.startswith("AIza"):
             url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
             
             # Gemini Structure: contents: [{ parts: [ ... ] }]
             parts = []
             for item in contents:
                 parts.append(item)
                 
             data = { "contents": [{ "parts": parts }] }
             
             response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
             if response.status_code != 200:
                 return f"Error from Google API: {response.text}"
             
             result = response.json()
             try:
                 return result['candidates'][0]['content']['parts'][0]['text']
             except:
                 return "Failed to parse Google API response."
        else:
            return "Only Gemini API keys (starting with AIza) support Image Analysis in this demo."

    except Exception as e:
        return f"Backend Error: {str(e)}"

@app.post("/api/generate")
async def generate_letter(request: GenerateRequest):
    if not request.target_prompt:
        raise HTTPException(status_code=400, detail="Target prompt is required.")

    result = generate_with_llm(
        request.samples or [], 
        request.sample_images or [], 
        request.target_prompt, 
        request.api_key
    )
    return {"letter": result}

@app.get("/")
def read_root():
    return {"status": "AI Letter Writer Backend Running"}
