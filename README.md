# GenAI Document Intelligence Platform

A production-grade GenAI system that ingests PDFs, images, and tables, understands them using multimodal LLMs, and exposes structured data via APIs.

## Features

✅ **Document Ingestion**
- PDF upload and processing
- Image upload (PNG, JPG, TIFF) with OCR
- Scanned document support via Tesseract OCR

✅ **Extraction Capabilities**
- Text extraction (native + OCR fallback)
- Table extraction from PDFs
- Entity extraction (via LLM)
- Document summarization

✅ **Multimodal Understanding**
- Text embeddings (sentence-transformers)
- Vector search (FAISS)
- LLM reasoning layer (OpenAI/Gemini)

✅ **Structured Outputs**
- Schema-validated JSON responses
- Citations and evidence tracking
- Confidence scores

✅ **Production Infrastructure**
- FastAPI REST API
- Docker containerization
- Evaluation tooling (hallucination checks, schema validation)

## Tech Stack

- **Python 3.11+**
- **FastAPI** - REST API framework
- **FAISS** - Vector database
- **Tesseract OCR** - Image text extraction
- **pdfplumber** - Table extraction
- **sentence-transformers** - Embeddings
- **OpenAI/Gemini** - LLM reasoning
- **Docker** - Containerization

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Tesseract OCR (for image/OCR features)
- Poppler (for PDF processing)

### 1. Install Dependencies

```bash
# System dependencies (macOS)
brew install tesseract poppler

# Python dependencies
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-key-here"  # For LLM reasoning
# OR
export GEMINI_API_KEY="your-key-here"
export LLM_PROVIDER="gemini"  # Optional, defaults to "openai"
```

### 3. Run the Server

```bash
# Development
uvicorn apps.api.main:app --reload

# Production
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
```

### 4. Using Docker

```bash
# Build and run
docker-compose up --build

# Or manually
docker build -t gen-ai-doc-intel .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key gen-ai-doc-intel
```

## API Endpoints

### `POST /v1/documents`
Upload and process a document.

**Request:** Multipart form data with PDF/image file

**Response:**
```json
{
  "doc_id": "uuid",
  "filename": "document.pdf",
  "pages": 10,
  "text_chunks": 45,
  "tables": [...],
  "extraction_method": "text"
}
```

### `POST /v1/query`
Query documents with semantic search + LLM reasoning.

**Request:**
```json
{
  "question": "What are the key financial risks?",
  "top_k": 5,
  "doc_ids": ["optional-filter"],
  "use_llm": true
}
```

**Response:**
```json
{
  "question": "...",
  "answer": "Generated answer with citations...",
  "citations": [...],
  "evidence": [...],
  "confidence": 0.85
}
```

### `POST /v1/documents/{doc_id}/extract`
Extract additional features (tables, entities, summary).

### `GET /v1/documents`
List all uploaded documents.

### `GET /health`
Health check endpoint.

## Architecture

```
PDF/Image Upload
   ↓
OCR (Tesseract) [if scanned]
   ↓
Text Extraction + Table Extraction
   ↓
Chunking + Embeddings
   ↓
Vector DB (FAISS)
   ↓
Semantic Search
   ↓
LLM Reasoning Layer
   ↓
Structured Output API (JSON)
```

## Project Structure

```
gen-ai-doc-intel/
├── apps/
│   └── api/
│       └── main.py          # FastAPI application
├── core/
│   ├── extract/
│   │   ├── ocr.py           # OCR functionality
│   │   └── tables.py        # Table extraction
│   ├── ingest/
│   │   └── chunk.py         # Text chunking
│   ├── embeddings/
│   │   └── local_embedder.py # Embedding generation
│   ├── vectorstore/
│   │   └── faiss_store.py   # FAISS vector DB
│   ├── llm/
│   │   └── reasoning.py     # LLM reasoning layer
│   ├── schemas/
│   │   └── outputs.py       # Pydantic schemas
│   └── eval/
│       └── validation.py   # Evaluation tooling
├── data/
│   ├── uploads/             # Uploaded documents
│   └── index/                # FAISS index
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Evaluation

The platform includes evaluation tooling:

- **Hallucination Detection**: Checks if LLM answers contain claims not in source documents
- **Schema Validation**: Ensures outputs conform to expected JSON schemas

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .
```

## Resume Bullet Points

- Built an end-to-end multimodal GenAI document intelligence system using Python, vector databases, and LLMs
- Implemented ingestion pipelines for PDFs and images with OCR fallback
- Developed inference APIs with structured JSON outputs and citation tracking
- Created evaluation tooling for hallucination detection and schema validation
- Containerized application with Docker for production deployment

## License

MIT
