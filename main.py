from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid

app = FastAPI(
    title="Policy Document RAG API",
    description="A Retrieval-Augmented Generation (RAG) API for ingesting and querying policy documents using natural language.",
    version="0.1.0"
)

# In-memory document store
document_store: Dict[str, str] = {}


class DocumentInput(BaseModel):
    text: str
    doc_id: str


class QueryInput(BaseModel):
    question: str


def simple_retriever(question: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Simple keyword-based retriever.
    In production, replace with a vector DB (e.g., FAISS, Chroma, Pinecone).
    """
    results = []
    question_lower = question.lower()
    keywords = question_lower.split()

    for doc_id, text in document_store.items():
        text_lower = text.lower()
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            # Extract a relevant snippet
            sentences = text.split('.')
            relevant_sentences = [s.strip() for s in sentences if any(kw in s.lower() for kw in keywords)]
            snippet = '. '.join(relevant_sentences[:2]) + '.' if relevant_sentences else text[:500]
            results.append({
                "text": snippet,
                "source": doc_id,
                "score": score
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


@app.post("/ingest", summary="Ingest Document")
def ingest_document(doc: DocumentInput):
    """
    Ingest a policy document into the RAG system.

    - **text**: Full text content of the document
    - **doc_id**: Unique identifier for the document
    """
    document_store[doc.doc_id] = doc.text
    return {"message": f"Document '{doc.doc_id}' ingested successfully.", "total_documents": len(document_store)}


@app.post("/query", summary="Query Documents")
def query_documents(query: QueryInput):
    """
    Query the ingested documents using natural language.

    - **question**: The natural language question to query against documents
    """
    if not document_store:
        return {"answer": "No documents have been ingested yet.", "sources": []}

    results = simple_retriever(query.question)

    if not results:
        return {"answer": "No relevant documents found for your question.", "sources": []}

    return results


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Policy Document RAG API is running. Visit /docs for API documentation."}


@app.get("/health", summary="Health Check")
def health_check():
    """Check if the API is running and return stats."""
    return {
        "status": "healthy",
        "total_documents": len(document_store),
        "document_ids": list(document_store.keys())
    }
