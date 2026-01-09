from google import genai
from typing import List
import os
from Generative_AI_Core.Interfaces.interfaces import LLMProvider

class GeminiAdapter(LLMProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key required for GeminiAdapter")
        
        # New SDK Initialization
        self.client = genai.Client(api_key=api_key)
        self.generation_model = 'gemini-2.5-flash'
        self.embedding_model = 'text-embedding-004'

    async def generate_text(self, system_prompt: str, user_prompt: str, images: List[object] = None) -> str:
        try:
            # Construct content payload
            contents = [f"SYSTEM: {system_prompt}\n\nUSER: {user_prompt}"]
            
            if images:
                # Append images to the content list
                # google-genai SDK accepts PIL Images or raw bytes objects usually
                contents.extend(images)
            
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"Error generating text: {str(e)}"

    async def embed_text(self, text: str) -> List[float]:
        try:
            # embed_content signature in new SDK
            result = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text,
                config={'title': "Letter Sample"} # optional config if needed
            )
            # The structure of result might differ slightly, usually result.embeddings[0].values
            # Checking docs pattern: result.embeddings[0].values
            if result.embeddings:
                return result.embeddings[0].values
            return []
        except Exception as e:
            print(f"Embedding error: {str(e)}")
            return []
