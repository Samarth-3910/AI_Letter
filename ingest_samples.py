import asyncio
import os
import glob
import uuid
import sys
sys.path.append(os.getcwd())
import pypdf
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

from Generative_AI_Core.Model_Adapters.gemini_adapter import GeminiAdapter
from Generative_AI_Core.Model_Adapters.chroma_adapter import ChromaAdapter

BRONZE_PATH = os.path.join("Data_Engineering", "Bronze_Raw")
GOLD_PATH = os.path.join("Data_Engineering", "Gold_VectorStore")

async def main():
    print("--- Bulk Data Ingestion Engine ---")
    
    # 0. Ensure directories exist
    if not os.path.exists(BRONZE_PATH):
        os.makedirs(BRONZE_PATH)
        print(f"Created directory: {BRONZE_PATH}")
        print(f"Please put your .txt files in there and run this script again.")
        return

    # 1. Setup
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = input("Enter your Gemini API Key (or set in .env): ").strip()
    
    if not api_key:
        print("API Key is required to generate embeddings.")
        return

    try:
        print("Initializing Adapters...")
        llm = GeminiAdapter(api_key)
        vector_store = ChromaAdapter(persistence_path=GOLD_PATH)
    except Exception as e:
        print(f"Initialization Failed: {e}")
        return

    # 2. Find Files
    # We look for .txt, .pdf, .jpg, .jpeg, .png files.
    txt_files = glob.glob(os.path.join(BRONZE_PATH, "*.txt"))
    pdf_files = glob.glob(os.path.join(BRONZE_PATH, "*.pdf"))
    img_files = glob.glob(os.path.join(BRONZE_PATH, "*.jpg")) + \
                glob.glob(os.path.join(BRONZE_PATH, "*.jpeg")) + \
                glob.glob(os.path.join(BRONZE_PATH, "*.png"))
    
    files = txt_files + pdf_files + img_files
    
    if not files:
        print(f"No documents (txt/pdf/images) found in {BRONZE_PATH}")
        print("Please add your sample letters (as text or pdf) to that folder.")
        return

    print(f"Found {len(files)} samples. Starting ingestion...")

    # 3. Process Loop
    success_count = 0
    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}...", end=" ")
        
        try:
            content = ""
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                 try:
                     image = Image.open(file_path)
                     print("(Image OCR)...", end=" ")
                     # Ask Gemini to transribe
                     content = await llm.generate_text(
                         system_prompt="You are an expert transcriber. Transcribe the text in this image exactly as written. Do not add commentary.",
                         user_prompt="Transcribe this letter.",
                         images=[image]
                     )
                 except Exception as e:
                     print(f"FAILED (Image Error: {e})")
                     continue

            elif filename.endswith(".pdf"):
                try:
                    reader = pypdf.PdfReader(file_path)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
                except Exception as e:
                    print(f"FAILED (PDF Error: {e})")
                    continue
            else:
                # Text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            if len(content.strip()) < 10:
                print("SKIPPED (Too short)")
                continue

            # Embed
            embedding = await llm.embed_text(content)
            
            if not embedding:
                print("FAILED (Embedding error)")
                continue

            # Save
            doc_id = str(uuid.uuid4())
            vector_store.add_document(
                doc_id=doc_id,
                text=content,
                embedding=embedding,
                metadata={
                    "source": filename,
                    "ingest_method": "bulk_script",
                    "original_path": file_path
                }
            )
            print("DONE")
            success_count += 1
            
        except Exception as e:
            print(f"ERROR: {e}")

    print("-" * 30)
    print(f"Ingestion Complete. Successfully added {success_count}/{len(files)} documents to Knowledge Base.")
    print("Restart your specific server to verify the new knowledge is active.")

if __name__ == "__main__":
    asyncio.run(main())
