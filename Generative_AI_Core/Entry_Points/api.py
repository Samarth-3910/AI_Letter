from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Domain Imports
from Generative_AI_Core.Interfaces.interfaces import LLMProvider, VectorStore
from Generative_AI_Core.Model_Adapters.gemini_adapter import GeminiAdapter
from Generative_AI_Core.Model_Adapters.chroma_adapter import ChromaAdapter
from Generative_AI_Core.Orchestration.rag_pipeline import RAGPipeline

app = FastAPI(title="AI Letter Engine API")

# Enable CORS for Next.js
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency Injection Setup ---
class AppState:
    def __init__(self):
        self.rag_pipeline: Optional[RAGPipeline] = None
        self.is_ready = False

state = AppState()

# Auto-Initialize if Key exists
env_api_key = os.getenv("GEMINI_API_KEY")
if env_api_key and len(env_api_key) > 5:
    print("Found API Key in .env, checking connection...")
    try:
        llm = GeminiAdapter(api_key=env_api_key)
        vector_store = ChromaAdapter(persistence_path="Data_Engineering/Gold_VectorStore")
        state.rag_pipeline = RAGPipeline(llm, vector_store)
        state.is_ready = True
        print(">>> ENGINE AUTO-INITIALIZED <<<")
    except Exception as e:
        print(f"Auto-Init Failed: {e}")

class InitRequest(BaseModel):
    gemini_api_key: str

@app.post("/api/init")
async def initialize_engine(request: InitRequest):
    """
    Initializes the adapters (Manual Fallback).
    """
    try:
        api_key = request.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
             raise HTTPException(status_code=400, detail="No API Key provided and none in .env")
             
        llm = GeminiAdapter(api_key=api_key)
        vector_store = ChromaAdapter(persistence_path="Data_Engineering/Gold_VectorStore")
        
        state.rag_pipeline = RAGPipeline(llm, vector_store)
        state.is_ready = True
        return {"status": "initialized", "message": "Engine is ready."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateRequest(BaseModel):
    user_prompt: str
    auto_learn: bool = True

@app.post("/api/generate")
async def generate_letter(request: GenerateRequest):
    if not state.is_ready:
        raise HTTPException(status_code=400, detail="Engine not initialized. Call /api/init first.")
    
    try:
        result = await state.rag_pipeline.generate_letter(request.user_prompt, request.auto_learn)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest/text")
async def ingest_manual_sample(text: str, source: str = "manual"):
    if not state.is_ready:
        raise HTTPException(status_code=400, detail="Engine not initialized.")
    
    doc_id = await state.rag_pipeline.ingest_sample(text, metadata={"source": source})
    return {"status": "success", "doc_id": doc_id}

@app.get("/")
def health_check():
    return {"system": "Generative AI Core", "status": "running", "ready": state.is_ready}
