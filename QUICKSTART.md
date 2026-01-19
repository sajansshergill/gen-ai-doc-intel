# Quick Start Guide

## Installation

### 1. Install System Dependencies (macOS)

```bash
brew install tesseract poppler
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables (Optional - for LLM features)

```bash
export OPENAI_API_KEY="your-key-here"
# OR
export GEMINI_API_KEY="your-key-here"
export LLM_PROVIDER="gemini"  # Optional, defaults to "openai"
```

## Running the Server

### Development Mode

```bash
uvicorn apps.api.main:app --reload
```

### Production Mode

```bash
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
```

### Using Docker

```bash
# Build and run
docker-compose up --build

# Or manually
docker build -t gen-ai-doc-intel .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key gen-ai-doc-intel
```

## Testing the API

### 1. Health Check

```bash
curl http://127.0.0.1:8000/health
```

### 2. Upload a Document

```bash
curl -X POST "http://127.0.0.1:8000/v1/documents" \
  -F "file=@your-document.pdf"
```

### 3. Query Documents

```bash
curl -X POST "http://127.0.0.1:8000/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key points?",
    "top_k": 5
  }'
```

### 4. Get Document Chunks

```bash
curl "http://127.0.0.1:8000/v1/documents/{doc_id}/chunks"
```

### 5. Get Document Tables

```bash
curl "http://127.0.0.1:8000/v1/documents/{doc_id}/tables"
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Troubleshooting

### Server won't start

1. Check if port 8000 is available: `lsof -ti:8000`
2. Kill existing process: `kill $(lsof -ti:8000)`
3. Check Python version: `python --version` (requires 3.11+)

### Import errors

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check if you're in the project root directory
3. Verify Python path includes the project directory

### OCR not working

1. Install Tesseract: `brew install tesseract`
2. Verify installation: `tesseract --version`

### LLM features not working

1. Set API key: `export OPENAI_API_KEY="your-key"`
2. Check logs for initialization errors
3. Server will run in retrieval-only mode if LLM unavailable
