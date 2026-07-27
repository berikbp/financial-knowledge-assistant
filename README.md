# Financial Knowledge Assistant

Financial Knowledge Assistant is a RAG project for asking questions over financial documents.

The project uses real PDF documents from banking, macroeconomic, and regulatory sources. It extracts text from PDFs, splits the text into chunks, stores the chunks in Qdrant, and answers questions using retrieved document context.

The goal of this project was to understand how a practical RAG system works end to end:

```text
PDF documents -> chunks -> embeddings -> vector search -> answer with sources
```

## What This Project Does

The app can answer questions such as:

```text
What line items are included in Halyk Bank's consolidated statement of profit or loss for 2025?
```

```text
Какие факторы влияли на инфляцию в Казахстане в 2026 году?
```

```text
Какие меры предусмотрены против отмывания доходов?
```

The answer includes sources, so it is possible to check where the information came from.

## Main Features

- PDF loading and text extraction
- Text chunking
- Metadata extraction such as source, year, language, and document type
- Dense retrieval using BGE-M3 embeddings
- Qdrant vector database
- BM25 keyword search
- Hybrid search
- FastAPI backend
- Simple browser frontend
- Basic evaluation script
- Docker Compose deployment
- AWS EC2 deployment

## How It Works

```text
User question
    |
    v
FastAPI backend
    |
    v
Retrieve relevant chunks from Qdrant
    |
    v
Use retrieved text as context
    |
    v
Generate answer with source references
```

The frontend sends a question to the backend.
The backend searches the document chunks and sends the most relevant chunks to the answer generator.
The final answer is returned with source information.

## Project Structure

```text
api/                 FastAPI backend
data/                PDF documents
frontend/            Simple browser UI
src/                 Main RAG code
src/ingestion/       PDF loading and chunking
src/retrieval/       Dense, BM25, and hybrid retrieval
src/generation/      Answer generation
src/vectorstore/     Qdrant integration
src/eval/            Evaluation scripts
scripts/             Indexing scripts
deployment/          EC2 helper scripts
```

## Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

QDRANT_HOST=localhost
QDRANT_PORT=6333
```

Do not commit your `.env` file.

## Start Qdrant

```bash
docker compose up qdrant -d
```

Depending on your local Docker config, Qdrant may be available on port `6333` or another mapped port.

Check Qdrant:

```bash
curl http://localhost:6333/collections
```

## Build the Index

If you want to build the index directly from PDFs:

```bash
PYTHONPATH=. uv run python scripts/index_documents.py
```

If you already have `cache/chunks.json` and want to skip PDF loading/chunking:

```bash
PYTHONPATH=. uv run python scripts/index_from_cache.py
```

The second option is faster, but it still needs to create embeddings.

## Run the API

```bash
uvicorn api.main:app
```

Open:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Run the Frontend

```bash
cd frontend
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

## API Endpoints

```text
GET  /health
POST /retrieve
POST /query
```

`/retrieve` returns retrieved chunks only.

`/query` returns the final answer with sources.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What line items are included in Halyk Bank consolidated statement of profit or loss for 2025?",
    "filters": {
      "source": "HalykBank",
      "document_type": "financial_statement"
    },
    "limit": 5
  }'
```

## Evaluation

Run:

```bash
PYTHONPATH=. uv run python main.py
```

The evaluation checks whether retrieval returns the expected document sources and whether the generated answers contain expected citations and concepts.

Current small benchmark result:

```text
Total cases: 3
Retrieval source pass rate: 1.00
Retrieval type pass rate: 1.00
Retrieval keyword pass rate: 1.00
Citation validity pass rate: 1.00
Average answer keyword coverage: 0.92
Average concept coverage: 0.92
```

This is only a small test set, not a complete benchmark.

## Docker Deployment

Start the production Docker Compose stack:

```bash
docker compose -f docker-compose.prod.yml up -d
```

Check containers:

```bash
docker compose -f docker-compose.prod.yml ps
```

Check backend:

```bash
curl http://localhost:8000/health
```

Check frontend:

```bash
curl -I http://localhost:5500
```

## AWS EC2 Deployment

The project was deployed on one AWS EC2 Ubuntu instance using Docker Compose.

```text
EC2 server
    |
    +-- Qdrant container
    +-- FastAPI backend container
    +-- Frontend container
```

Public services:

```text
Frontend: http://EC2_PUBLIC_IP:5500
API:      http://EC2_PUBLIC_IP:8000
```

Qdrant should stay private inside Docker and should not be exposed publicly.

Example production environment file:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

FRONTEND_ORIGINS=http://EC2_PUBLIC_IP:5500

QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

For faster indexing, I built the Qdrant index locally on my laptop and uploaded `qdrant_storage` to EC2.

## Notes

The project currently uses:

- BGE-M3 for embeddings
- Qdrant for vector search
- BM25 for keyword search
- FastAPI for serving
- OpenAI API for answer generation

The reranker can be disabled on small CPU servers because it can make the app slower.

## Limitations

This is a learning and portfolio project, not a production financial assistant.

Current limitations:

- The evaluation set is small.
- PDF text extraction is not always perfect.
- Some retrieved chunks may contain mixed information.
- The app does not have authentication.
- The frontend is simple.
- The system is not suitable for real financial advice.

## What I Learned

This project helped me understand that RAG is not only about sending PDFs to an LLM.

The important parts are:

```text
document cleaning
chunking
metadata
embeddings
retrieval
evaluation
citations
deployment
```

A good RAG system needs to be testable and debuggable, not just functional.
