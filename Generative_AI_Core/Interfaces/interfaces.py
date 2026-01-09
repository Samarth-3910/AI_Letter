from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """
    Abstract interface for any AI Model (Gemini, GPT-4, Llama, etc.)
    """
    @abstractmethod
    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates text based on prompts.
        """
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """
        Converts text into a vector embedding.
        """
        pass

class VectorStore(ABC):
    """
    Abstract interface for any Vector Database (Chroma, Pinecone, FAISS)
    """
    @abstractmethod
    def add_document(self, doc_id: str, text: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """
        Saves a document and its embedding.
        """
        pass

    @abstractmethod
    def query_similar(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Returns relevant documents based on vector similarity.
        """
        pass
