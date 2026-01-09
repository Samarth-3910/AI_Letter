import uuid
from typing import List, Dict, Optional
from Generative_AI_Core.Interfaces.interfaces import LLMProvider, VectorStore

class RAGPipeline:
    def __init__(self, llm: LLMProvider, vector_store: VectorStore):
        self.llm = llm
        self.vector_store = vector_store

    async def ingest_sample(self, text: str, metadata: Dict = None):
        """
        Ingests a new text sample into the knowledge base (Vector Encoded).
        """
        if not text or len(text.strip()) < 10:
            return # Too short
        
        # 1. Generate Embedding
        embedding = await self.llm.embed_text(text)
        
        # 2. Store in Vector DB
        doc_id = str(uuid.uuid4())
        self.vector_store.add_document(
            doc_id=doc_id, 
            text=text, 
            embedding=embedding, 
            metadata=metadata or {"source": "manual_upload"}
        )
        return doc_id

    async def generate_letter(self, user_prompt: str, auto_learn: bool = True) -> Dict:
        """
        Generates a letter using RAG.
        If auto_learn is True, saves the result back to memory.
        """
        # 1. Embed the query to find relevant context
        query_embedding = await self.llm.embed_text(user_prompt)
        
        # 2. Retrieve Context (Top 3 similar letters)
        similar_docs = self.vector_store.query_similar(query_embedding, top_k=3)
        
        context_str = ""
        for i, doc in enumerate(similar_docs):
            context_str += f"\n--- SAMPLE {i+1} ---\n{doc['text']}\n"

        # 3. Construct Prompt
        system_instruction = (
            "You are an expert ghostwriter. "
            "I will provide you with several SAMPLES of my previous writing style. "
            "Your task is to answer the USER REQUEST by strictly mimicking the tone, structure, and vocabulary of the samples. "
            "If the samples contain the answer, use it. If not, extrapolate the style to the new topic."
        )
        
        full_user_prompt = f"RELEVANT SAMPLES:\n{context_str}\n\nUSER REQUEST:\n{user_prompt}"

        # 4. Generate
        generated_text = await self.llm.generate_text(system_instruction, full_user_prompt)

        # 5. Feedback Loop (The "Self-Learning" bit)
        if auto_learn and generated_text and "Error" not in generated_text:
            # We ingest what we just wrote, so next time we remember it.
            await self.ingest_sample(generated_text, metadata={"source": "ai_generated", "trigger_prompt": user_prompt})

        return {
            "result": generated_text,
            "context_used": [d['text'][:50]+"..." for d in similar_docs]
        }
