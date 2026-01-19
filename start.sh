#!/bin/bash
# Quick start script for local development

echo "🚀 Starting GenAI Document Intelligence Platform..."
echo ""

# Check Python version
python3 --version

# Create data directories
mkdir -p data/uploads data/index

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Start the server
echo "🌐 Starting FastAPI server on http://127.0.0.1:8000"
echo "📚 API docs: http://127.0.0.1:8000/docs"
echo ""
uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --reload
