import chromadb

# 1. Initialize the client (ensure this path matches your actual database folder)
client = chromadb.PersistentClient(path="./chroma_db")

# 2. Get your collection (replace 'your_collection_name' with your actual name)
collection = client.get_collection(name="your_collection_name")

# 3. Define the ID(s) to remove
# Replace the string below with the EXACT ID found in your database
target_id = "questions till chapter 6" 

# 4. Perform the deletion
collection.delete(ids=[target_id])

print(f"Successfully deleted document with ID: {target_id}")