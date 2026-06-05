import sys

try:
    import chromadb
except ImportError:
    raise ImportError(
        "chromadb is required to run this script. Install it with `pip install chromadb`."
    ) from None

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("policy_docs")

# Total chunks stored
print(f"Total chunks: {collection.count()}")

# See all unique document sources
all_items = collection.get(include=["metadatas"])
sources = set(m["source"] for m in all_items["metadatas"])
print(f"Documents ingested: {sources}")

# Preview first 5 chunks with text + metadata
preview = collection.get(limit=5, include=["documents", "metadatas"])
for i, (doc, meta) in enumerate(zip(preview["documents"], preview["metadatas"])):
    print(f"\n--- Chunk {i+1} | Source: {meta['source']} ---")
    print(doc[:300])