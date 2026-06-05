import chromadb

# Initialize the client pointing to your existing database folder
client = chromadb.PersistentClient(path="C:\\policy-rag\\chroma_db")

# List all collections
collections = client.list_collections()

# Print their names
for col in collections:
    print(f"Collection found: {col.name}")