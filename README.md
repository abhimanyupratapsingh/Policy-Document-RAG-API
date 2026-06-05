# Policy RAG Assistant

A full-stack Retrieval-Augmented Generation (RAG) chatbot application for querying policy documents. Features a FastAPI backend with local embeddings and LLM inference, plus a React frontend with real-time chat and document management.

## Architecture

```
policy-rag/
├── app.py                 # FastAPI RAG backend
├── Requirements.txt       # Python dependencies
├── chroma_db/            # Vector store (ChromaDB)
└── frontend/             # React chatbot UI
    ├── src/
    │   ├── api.js        # API client
    │   ├── App.jsx       # Main layout
    │   ├── components/   # React components
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

## Stack

### Backend
- **FastAPI** — REST API framework
- **ChromaDB** — Vector database for semantic search
- **Ollama** — Local LLM inference (mistral, phi3, llama3.2, etc.)
- **HuggingFace Embeddings** — `all-MiniLM-L6-v2` (local embeddings)
- **LangChain** — Text splitting & orchestration

### Frontend
- **React 18** — UI framework
- **Vite** — Build tool & dev server
- **react-chatbotify** — Chat UI component
- **Plain CSS** — Styling (no frameworks)

## Prerequisites

### System Requirements
- Python 3.8+
- Node.js 16+
- Ollama (for local LLM)

### Install Ollama
Download from [ollama.ai](https://ollama.ai) and run:
```powershell
ollama serve
```

In another terminal:
```powershell
ollama pull mistral
# Or: ollama pull phi3, llama3.2, etc.
```

## Installation

### Backend Setup

```powershell
cd c:\policy-rag
pip install -r Requirements.txt
```

### Frontend Setup

```powershell
cd c:\policy-rag\frontend
npm install
```

## Running the Application

### Start Backend
```powershell
cd c:\policy-rag
uvicorn app:app --reload --port 8000
```

Server starts at: `http://localhost:8000`

Health check: `http://localhost:8000/health`

### Start Frontend
```powershell
cd c:\policy-rag\frontend
npm run dev
```

App opens at: `http://localhost:5173`

### Environment Variables (Backend)

```powershell
# Change LLM model
$env:OLLAMA_MODEL = "phi3"  # or llama3.2, etc.

# Change Ollama endpoint (if not localhost)
$env:OLLAMA_BASE_URL = "http://ollama-server:11434"
```

## API Endpoints

### Health Check
```
GET /health
```
Response:
```json
{
  "status": "ok",
  "ollama_reachable": true,
  "ollama_model": "mistral",
  "chunks_in_db": 42,
  "embedding_model": "all-MiniLM-L6-v2"
}
```

### Ingest Document
```
POST /ingest
Body: {
  "text": "Full document text...",
  "doc_id": "welfare_policy_2024"
}
```
Response:
```json
{
  "status": "success",
  "chunks_processed": 5
}
```

### Query Documents (Retrieval Only)
```
POST /query
Body: { "question": "What are eligibility requirements?" }
```
Response:
```json
{
  "results": [
    {
      "text": "Chunk text from document...",
      "source": "doc_id"
    }
  ]
}
```

### Full RAG Chat
```
POST /chat
Body: { "question": "When can I apply for benefits?" }
```
Response:
```json
{
  "question": "When can I apply for benefits?",
  "answer": "According to the policy documents, you can apply for benefits starting at age 62...",
  "model": "mistral",
  "sources": [
    {
      "source": "welfare_policy_2024",
      "excerpt": "First 250 characters of the relevant chunk..."
    }
  ]
}
```

### Get Corpus Info
```
GET /corpus
```
Response:
```json
{
  "total_chunks": 42,
  "documents": ["welfare_policy_2024", "healthcare_guide_2024"],
  "chunks_per_document": {
    "welfare_policy_2024": 25,
    "healthcare_guide_2024": 17
  }
}
```

## Frontend Features

### Chat Interface
- Real-time conversation with the RAG bot
- Typing indicators while bot processes
- Message bubbles with source citations
- Error handling & fallback messages

### Document Management
- **Ingest Panel** — Upload policy documents with custom IDs
- **Corpus Info** — View ingested documents and chunk counts
- Auto-updates after successful ingestion

### Health Monitoring
- **Status Banner** — Shows connection status to Ollama
- Displays setup instructions if Ollama is unreachable
- Auto-dismissible warnings

## Configuration

### Backend Constants (app.py)
```python
CHUNK_SIZE = 800          # Text chunk size for splitting
CHUNK_OVERLAP = 150       # Overlap between chunks
TOP_K_RESULTS = 3         # Number of chunks to retrieve
OLLAMA_MODEL = "mistral"  # Default LLM model
CHROMA_PERSIST_DIR = "./chroma_db"  # Vector DB location
```

### Frontend Settings (vite.config.js)
```js
proxy: {
  '/chat':   'http://localhost:8000',
  '/ingest': 'http://localhost:8000',
  '/health': 'http://localhost:8000',
  '/corpus': 'http://localhost:8000',
}
```

## Testing the Application

### 1. Health Check
```powershell
curl http://localhost:8000/health
```

### 2. Ingest a Sample Document
```powershell
$body = @{
    text = "Eligibility: You must be 62 or older. You need 40 work credits earned over your lifetime."
    doc_id = "test_policy"
} | ConvertTo-Json

curl -X POST http://localhost:8000/ingest `
  -H "Content-Type: application/json" `
  -d $body
```

### 3. Query the Document
```powershell
$query = @{ question = "What is the minimum age?" } | ConvertTo-Json

curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d $query
```

### 4. Use the Web UI
- Open `http://localhost:5173`
- Upload a document in the sidebar
- Ask questions in the chat window
- View source citations below responses

## Troubleshooting

### "Ollama is not reachable"
```powershell
# Start Ollama server (new terminal)
ollama serve

# Ensure the model is downloaded
ollama pull mistral
```

### CORS errors in browser console
- ✅ Already fixed — CORS middleware is configured in `app.py`
- Ensure frontend is at `http://localhost:5173`
- Ensure backend is at `http://localhost:8000`

### "No documents ingested yet" error
- Use the **Add Document** form in the sidebar
- Paste policy text + give it a document ID
- Click **Ingest Document**

### Slow LLM responses
- Normal on first run — Ollama loads the model into memory
- Subsequent requests are faster
- Consider a faster model like `phi3` if `mistral` is slow

### ChromaDB errors
```powershell
# Reset the vector database
Remove-Item -Path c:\policy-rag\chroma_db -Recurse -Force

# Restart the backend
uvicorn app:app --reload
```

## Project Structure

### Backend Files
- **app.py** — FastAPI application with all endpoints
- **Requirements.txt** — Python package dependencies
- **cleanup.py** — Utility to delete documents from ChromaDB
- **inspect_corpus.py** — View chunks in the database
- **find_collection.py** — List ChromaDB collections

### Frontend Files
- **src/api.js** — API client (all fetch calls)
- **src/App.jsx** — Main layout & state management
- **src/main.jsx** — React entry point
- **src/components/ChatBot/** — Chat interface
- **src/components/SourcePanel/** — Citation display
- **src/components/UploadForm/** — Document ingestion
- **src/components/HealthBanner/** — Status indicator
- **src/components/CorpusInfo/** — Corpus statistics

## Development Workflow

### Running Both Backend & Frontend

Open two terminals:

**Terminal 1 (Backend):**
```powershell
cd c:\policy-rag
uvicorn app:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```powershell
cd c:\policy-rag\frontend
npm run dev
```

### Making Changes

- **Backend changes** — Uvicorn auto-reloads with `--reload`
- **Frontend changes** — Vite dev server hot-reloads

### Building for Production

```powershell
cd c:\policy-rag\frontend
npm run build
# Output in: frontend/dist/
```

## Environment Customization

### Use Different LLM Models

```powershell
# Check available models
ollama list

# Download a model
ollama pull llama3.2

# Run with the model
$env:OLLAMA_MODEL = "llama3.2"
uvicorn app:app --reload
```

### Adjust Chunk Size for Better Retrieval

Edit `app.py`:
```python
CHUNK_SIZE = 1024        # Larger chunks = broader context
CHUNK_OVERLAP = 200      # More overlap = better connections
TOP_K_RESULTS = 5        # Return more results
```

### Change Embedding Model

Edit `app.py` line 24:
```python
embeddings_model = HuggingFaceEmbeddings(
    model_name="all-mpnet-base-v2"  # More powerful, slower
)
```

## Performance Notes

- **First chat query** — 2-5 seconds (LLM loads model)
- **Subsequent queries** — 1-2 seconds
- **Document ingestion** — ~1-2 seconds per 1000 words
- **Vector search** — <50ms (ChromaDB in-memory)

## Future Enhancements

- [ ] Streaming responses (SSE)
- [ ] Multi-user sessions
- [ ] Chat history persistence
- [ ] Advanced query expansion (NLP)
- [ ] Entity extraction for better filtering
- [ ] Custom prompt templates
- [ ] Support for PDF/DOC file uploads
- [ ] Dark mode toggle

## License

MIT

## Contributing

Pull requests welcome! Please ensure:
- Backend changes are tested with the health endpoint
- Frontend builds without errors (`npm run build`)
- No hardcoded URLs (use env variables)

## Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Verify Ollama is running (`ollama serve`)
3. Check backend logs for errors
4. Review browser DevTools Network tab for API errors
