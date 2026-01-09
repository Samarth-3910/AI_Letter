import chromadb
from typing import List, Dict, Any
import os
from Generative_AI_Core.Interfaces.interfaces import VectorStore

class ChromaAdapter(VectorStore):
    def __init__(self, persistence_path: str = "data/gold"):
        # Ensure directory exists
        os.makedirs(persistence_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persistence_path)
        self.collection = self.client.get_or_create_collection(name="letter_knowledge_base")

    def add_document(self, doc_id: str, text: str, embedding: List[float], metadata: Dict[str, Any] = None):
        if not embedding:
            print(f"Skipping document {doc_id} due to empty embedding")
            return

        self.collection.upsert(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata or {}]
        )

    def query_similar(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        if not query_embedding:
            return []
            
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Chroma returns lists of lists (batch format), needing flattening for single query
        structured_results = []
        if results['ids']:
            count = len(results['ids'][0])
            for i in range(count):
                structured_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0.0
                })
                
        return structured_results
