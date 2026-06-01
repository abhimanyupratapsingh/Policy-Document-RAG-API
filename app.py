import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

# ── Config Constants ─────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = "./chroma_db"
CHROMA_COLLECTION = "policy_docs"
CHUNK_SIZE = 800                 
CHUNK_OVERLAP = 150              
TOP_K_RESULTS = 5                

app = FastAPI(title="Policy Document RAG API")

print("Loading Embedding Model...")
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

class DocumentInput(BaseModel):
    text: str
    doc_id: str

class QueryInput(BaseModel):
    question: str

@app.post("/ingest")
async def ingest_document(doc: DocumentInput):
    try:
        chunks = text_splitter.split_text(doc.text)
        chunk_embeddings = embeddings_model.embed_documents(chunks)
        ids = [f"{doc.doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": doc.doc_id} for _ in chunks]
        
        collection.upsert(
            ids=ids,
            embeddings=chunk_embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        return {"status": "success", "chunks_processed": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_documents(query: QueryInput):
    try:
        query_embedding = embeddings_model.embed_query(query.question)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K_RESULTS
        )
        formatted_results = []
        if results['documents']:
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                formatted_results.append({"text": doc, "source": meta.get("source")})
        return {"results": formatted_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
