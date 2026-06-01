# 📄 Policy Document RAG API

A **Retrieval-Augmented Generation (RAG)** API for ingesting and querying policy documents using natural language.

![Version](https://img.shields.io/badge/version-0.1.0-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![Python](https://img.shields.io/badge/Python-3.8+-yellow) ![License](https://img.shields.io/badge/license-MIT-brightgreen)

---

## 🚀 Features

- **Document Ingestion** — Store policy documents with unique IDs for later retrieval
- **Natural Language Querying** — Ask questions against ingested documents using RAG
- **Fast & Lightweight** — Built with FastAPI and served via Uvicorn
- **Auto-generated Docs** — Interactive Swagger UI available at `/docs`
- **OpenAPI 3.1** — Fully spec-compliant REST API

---

## 📦 Installation

```bash
git clone https://github.com/abhimanyupratapsingh/Policy-Document-RAG-API.git
cd Policy-Document-RAG-API
pip install -r requirements.txt
```

---

## ▶️ Running the Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

- API Base URL: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## 🔌 API Endpoints

### `POST /ingest` — Ingest a Document

Stores a policy document into the RAG system for future querying.

**Request Body:**
```json
{
  "text": "Full text content of the policy document...",
  "doc_id": "unique-document-identifier"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | ✅ Yes | The full text content of the document |
| `doc_id` | string | ✅ Yes | A unique identifier for the document |

**Responses:**

| Code | Description |
|------|-------------|
| 200 | Document successfully ingested |
| 422 | Validation Error — check request body |

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{"text": "Policy content here...", "doc_id": "policy-001"}'
```

---

### `POST /query` — Query Documents

Ask a natural language question against all ingested documents using RAG.

**Request Body:**
```json
{
  "question": "What is the mobilization process for DDUGKY?"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | ✅ Yes | Natural language question to query documents |

**Responses:**

| Code | Description |
|------|-------------|
| 200 | Returns relevant document excerpts with sources |
| 422 | Validation Error — check request body |

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the selection criteria for candidates?"}'
```

**Example Response:**
```json
[
  {
    "text": "The purpose of the selection process is to identify candidates who are best suited...",
    "source": "BatchData"
  }
]
```

---

## 📐 Data Schemas

**DocumentInput**
```json
{
  "text": "string",
  "doc_id": "string"
}
```

**QueryInput**
```json
{
  "question": "string"
}
```

**ValidationError**
```json
{
  "loc": ["string | integer"],
  "msg": "string",
  "type": "string"
}
```

---

## 📁 Project Structure

```
Policy-Document-RAG-API/
├── app.py           # Main FastAPI app & route definitions
├── requirements.txt # Python dependencies
├── .gitignore       # Python gitignore
├── LICENSE          # MIT License
└── README.md        # Project documentation
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework for building the API |
| **Uvicorn** | High-performance ASGI server |
| **RAG Pipeline** | Retrieval-Augmented Generation for Q&A |
| **OpenAPI 3.1** | API specification & documentation |
| **Pydantic** | Data validation and serialization |

---

## 🧪 Testing with Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click on **POST /ingest** → Try it out → Enter document text and ID → Execute
3. Click on **POST /query** → Try it out → Enter your question → Execute

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
