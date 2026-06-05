import os
import httpx
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
import ollama
from concurrent.futures import ThreadPoolExecutor

# ── Config Constants ──────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = "./chroma_db"
CHROMA_COLLECTION  = "policy_docs"
CHUNK_SIZE         = 800
CHUNK_OVERLAP      = 150
TOP_K_RESULTS      = 3
OLLAMA_MODEL       = os.getenv("OLLAMA_MODEL", "mistral")   # change to phi3, llama3.2, etc.
OLLAMA_BASE_URL    = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

app = FastAPI(title="Policy Document RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

print("Loading Embedding Model...")
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection    = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

# ── Prompt Template ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a helpful assistant for government policy documents.
Answer ONLY using the context provided below. Do not use any prior knowledge.
If the answer is not in the context, say: "This information was not found in the provided documents."
When answering, mention which source document the information comes from.
For eligibility criteria or multi-step processes, use a numbered list."""

def build_prompt(context: str, question: str) -> str:
    return f"""CONTEXT FROM POLICY DOCUMENTS:
{context}

QUESTION: {question}

ANSWER:"""


def retrieve_chunks(question: str) -> list[dict]:
    """Embed the question and fetch top-K relevant chunks from ChromaDB."""
    query_embedding = embeddings_model.embed_query(question)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K_RESULTS
    )
    chunks = []
    if results["documents"]:
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            chunks.append({"text": doc, "source": meta.get("source", "unknown")})
    return chunks


async def generate_answer(context: str, question: str) -> str:
    """
    Pass retrieved context + question to Ollama and return the generated answer.
    Runs fully locally — no data leaves the machine.
    """
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=1)

    def call_ollama():
        return ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_prompt(context, question)},
            ],
            options={
                "temperature": 0.1,
                "num_ctx":     4096,
            }
        )

    response = await loop.run_in_executor(executor, call_ollama)
    return response["message"]["content"].strip()


# ── Schemas ───────────────────────────────────────────────────────────────────
class DocumentInput(BaseModel):
    text:   str
    doc_id: str

class QueryInput(BaseModel):
    question: str

# ── Routes ────────────────────────────────────────────────────────────────────
@app.post("/ingest")
async def ingest_document(doc: DocumentInput):
    try:
        chunks           = text_splitter.split_text(doc.text)
        chunk_embeddings = embeddings_model.embed_documents(chunks)
        ids              = [f"{doc.doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas        = [{"source": doc.doc_id} for _ in chunks]
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
        chunks = retrieve_chunks(query.question)
        return {"results": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(query: QueryInput):
    """
    Full RAG pipeline — retrieves chunks AND generates an LLM answer with citations.

    Flow:
      1. Embed question (MiniLM, local)
      2. Vector search ChromaDB -> top-5 chunks
      3. Build grounded prompt (context + question)
      4. Ollama LLM generates answer (local)
      5. Return answer + source document citations

    """
    try:
        if collection.count() == 0:
            raise HTTPException(
                status_code=400,
                detail="No documents ingested yet. POST to /ingest first."
            )

        # Retrieve relevant chunks
        chunks = retrieve_chunks(query.question)
        if not chunks:
            return {
                "question": query.question,
                "answer":   "No relevant content found in the document store.",
                "sources":  []
            }

        # Build context string with source labels
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Source {i} - {chunk['source']}]\n{chunk['text']}")
        context = "\n\n".join(context_parts)

        # Generate answer with LLM
        answer = await generate_answer(context, query.question)

        # Deduplicated source citations
        seen = set()
        sources = []
        for chunk in chunks:
            src = chunk["source"]
            if src not in seen:
                seen.add(src)
                sources.append({"source": src, "excerpt": chunk["text"][:250] + "..."})

        return {
            "question": query.question,
            "answer":   answer,
            "model":    OLLAMA_MODEL,
            "sources":  sources,
        }

    except HTTPException:
        raise
    except Exception as e:
        err = str(e)
        if "connection" in err.lower() or "refused" in err.lower():
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Cannot reach Ollama. Run: ollama serve "
                    f"and: ollama pull {OLLAMA_MODEL}"
                )
            )
        raise HTTPException(status_code=500, detail=err)


@app.get("/health")
async def health():
    """Check server and Ollama status."""
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            ollama_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "status":           "ok",
        "ollama_reachable": ollama_ok,
        "ollama_model":     OLLAMA_MODEL,
        "chunks_in_db":     collection.count(),
        "embedding_model":  "all-MiniLM-L6-v2",
    }


@app.get("/corpus")
async def inspect_corpus():
    try:
        total    = collection.count()
        all_meta = collection.get(include=["metadatas"])
        sources  = list(set(m["source"] for m in all_meta["metadatas"]))

        chunk_counts = {}
        for m in all_meta["metadatas"]:
            src = m["source"]
            chunk_counts[src] = chunk_counts.get(src, 0) + 1

        return {
            "total_chunks":        total,
            "documents":           sources,
            "chunks_per_document": chunk_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
