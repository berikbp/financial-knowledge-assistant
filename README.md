# Enterprise Financial RAG Assistant

Enterprise Financial RAG Assistant is an AI engineering project for building a retrieval-augmented assistant over financial, banking, macroeconomic, and regulatory documents.

The system combines:

- dense retrieval with BGE-M3 and Qdrant,
- BM25 lexical search,
- hybrid retrieval with Reciprocal Rank Fusion,
- BGE cross-encoder reranking,
- cited answer generation,
- retrieval and answer evaluation,
- FastAPI serving,
- a lightweight frontend demo.

The final result is a working full-stack RAG system that can answer questions over financial documents and return cited sources with retrieval scores.

Example supported questions:

```text
Какие факторы влияли на инфляцию в Казахстане в 2026 году?

What line items are included in Halyk Bank's consolidated statement of profit or loss for 2025?

Какие меры предусмотрены против отмывания доходов?
```

## Architecture

```text
User question
    |
    v
FastAPI RAG API
    |
    +--> Dense retrieval
    |       |
    |       +--> BGE-M3 embeddings
    |       +--> Qdrant vector store
    |
    +--> BM25 lexical retrieval
            |
            +--> keyword-based search over chunks
    |
    v
Hybrid retrieval with Reciprocal Rank Fusion
    |
    v
BGE cross-encoder reranker
    |
    v
Top retrieved chunks + metadata
    |
    v
Answer generator
    |
    v
Cited answer + source list
```

Runtime modules:

```text
api/main.py                         FastAPI routes and API schemas
src/retrieval/pipeline.py           End-to-end retrieval pipeline
src/retrieval/hybrid_retriever.py   Dense + BM25 hybrid retrieval with RRF
src/retrieval/dense_retriever.py    Qdrant dense retrieval
src/retrieval/bm25_retrieval.py     BM25 lexical retrieval
src/retrieval/reranker.py           BGE cross-encoder reranking
src/generation/answer_generator.py  Cited answer generation
src/generation/context_formatter.py Retrieved context formatting
```

Ingestion and indexing modules:

```text
src/ingestion/pdf_loader.py         PDF loading and text extraction
src/ingestion/chunking.py           Paragraph-aware chunking
src/ingestion/chunk_cache.py        Chunk cache saving/loading
src/metadata/extractor.py           Source, year, language, and document-type inference
src/embedding/bge_embedder.py       BGE-M3 embedding wrapper
src/vectorstore/qdrant_store.py     Qdrant collection and search logic
scripts/index_documents.py          Builds Qdrant index
scripts/build_chunk_cache.py        Builds cached chunk file
```

Evaluation modules:

```text
src/eval/evaluate_rag.py            Retrieval, answer, citation, and completeness evaluation
main.py                             Evaluation runner
```

Frontend and deployment modules:

```text
frontend/index.html                 Browser demo UI
frontend/style.css                  Frontend styling
frontend/app.js                     Frontend API calls and rendering
frontend/config.js                  Frontend API URL configuration
Dockerfile.api                      FastAPI container
Dockerfile.frontend                 Frontend container
docker-compose.yml                  Local Docker Compose setup
docker-compose.prod.yml             Production-style Docker Compose setup
deployment/ec2-setup.sh             EC2 Docker installation script
deployment/deploy.sh                Production stack startup script
deployment/stop.sh                  Production stack shutdown script
```

## Why This Project Matters

The project is not only a simple “chat with PDFs” demo. It focuses on building a retrieval system that can be inspected, evaluated, and debugged.

The main engineering idea is practical:

> In financial RAG, answer quality depends on retrieval quality, chunk quality, metadata filtering, reranking, and citation discipline. A useful system needs retrieval debugging and evaluation, not only an LLM prompt.

The project includes two important API modes:

```text
POST /retrieve
```

Retrieves and reranks chunks without generating an answer. This is used to debug retrieval.

```text
POST /query
```

Runs the full RAG pipeline and returns a cited answer with sources.

## Results

The current evaluation set contains three core cases:

| Case                          | Domain                         | Expected Behavior                                    |
| ----------------------------- | ------------------------------ | ---------------------------------------------------- |
| `inflation_kz_2026`         | National Bank monetary policy  | Retrieve inflation-related factors from 2026 reports |
| `halyk_financial_statement` | Halyk Bank financial statement | Retrieve profit/loss line items                      |
| `aml_law`                   | Banking regulation / AML law   | Retrieve anti-money-laundering measures              |

Latest aggregate evaluation summary:

```text
Total cases: 3
Retrieval source pass rate: 1.00
Retrieval type pass rate: 1.00
Retrieval keyword pass rate: 1.00
Answer not empty rate: 1.00
Citation pass rate: 1.00
Citation validity pass rate: 1.00
Answer keyword pass rate: 1.00
Completeness pass rate: 1.00
Average answer keyword coverage: 0.92
Average concept coverage: 0.92
```

The important learning was not that the system is perfect. The evaluation revealed that retrieval can return chunks with mixed topics, and the answer generator can sometimes over-associate nearby statements. This is why the project includes retrieval-only debugging and explicit limitations.

## Setup

Install dependencies:

```bash
uv sync
```

Create a local `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

FRONTEND_ORIGINS=http://127.0.0.1:5500,http://localhost:5500

QDRANT_HOST=localhost
QDRANT_PORT=6333
```

Do not commit real `.env` files.

## Local Indexing

Start Qdrant locally:

```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

Index documents into Qdrant:

```bash
python -m scripts.index_documents
```

Build the chunk cache used by the API:

```bash
python -m scripts.build_chunk_cache
```

Expected generated folders:

```text
qdrant_storage/
cache/chunks.json
```

These folders are generated artifacts and should not be committed.

## Serve The API

Run the FastAPI backend:

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

Example response:

```json
{
  "status": "ok",
  "chunks_loaded": 3127
}
```

Do not use reload for heavy model serving if GPU memory is limited, because reload can duplicate model loading.

## API

```text
GET  /health
POST /retrieve
POST /query
```

### Retrieve Only

`POST /retrieve` runs retrieval and reranking without answer generation.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Какие факторы влияли на инфляцию в Казахстане в 2026 году?",
    "filters": {
      "source": "NationalBank",
      "year": 2026,
      "document_type": "monetary_policy_report"
    },
    "limit": 5,
    "hybrid_limit": 20,
    "dense_limit": 30,
    "bm25_limit": 30
  }'
```

The response includes retrieved chunks and scores:

```json
{
  "query": "...",
  "filters": {
    "source": "NationalBank",
    "year": 2026,
    "document_type": "monetary_policy_report"
  },
  "sources": [
    {
      "index": 1,
      "document_name": "ДоДКП май 2026 рус",
      "source": "NationalBank",
      "year": 2026,
      "document_type": "monetary_policy_report",
      "chunk_id": 19,
      "reranker_score": 0.9955,
      "rrf_score": 0.0300,
      "dense_score": 0.6776,
      "bm25_score": 13.6824,
      "text_preview": "..."
    }
  ]
}
```

### Full Query

`POST /query` runs the full RAG pipeline.

```text
query -> hybrid retrieval -> reranking -> answer generation -> cited answer
```

Example:

```bash
curl -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What line items are included in Halyk Bank'\''s consolidated statement of profit or loss for 2025?",
    "filters": {
      "source": "HalykBank",
      "year": 2025,
      "document_type": "financial_statement"
    },
    "limit": 5,
    "hybrid_limit": 20,
    "dense_limit": 30,
    "bm25_limit": 30
  }'
```

The response includes:

```json
{
  "query": "...",
  "answer": "1. Interest income calculated using the effective interest method [1]\n2. Interest expense [1]",
  "filters": {
    "source": "HalykBank",
    "year": 2025,
    "document_type": "financial_statement"
  },
  "sources": [
    {
      "index": 1,
      "document_name": "Financial-Statement",
      "source": "HalykBank",
      "year": 2025,
      "document_type": "financial_statement",
      "chunk_id": 0,
      "reranker_score": 0.9771,
      "rrf_score": 0.0310,
      "dense_score": 0.7100,
      "bm25_score": 12.4000,
      "text_preview": "..."
    }
  ]
}
```

## Demo Examples

### Inflation Factors

Input:

```text
Какие факторы влияли на инфляцию в Казахстане в 2026 году?
```

Suggested filters:

```json
{
  "source": "NationalBank",
  "year": 2026,
  "document_type": "monetary_policy_report"
}
```

Expected behavior:

```text
The system retrieves National Bank monetary policy chunks and returns cited inflation-related factors.
```

### Halyk Financial Statement

Input:

```text
What line items are included in Halyk Bank's consolidated statement of profit or loss for 2025?
```

Suggested filters:

```json
{
  "source": "HalykBank",
  "year": 2025,
  "document_type": "financial_statement"
}
```

Expected behavior:

```text
The system retrieves Halyk Bank financial statement chunks and returns cited profit/loss line items.
```

### AML Law

Input:

```text
Какие меры предусмотрены против отмывания доходов?
```

Suggested filters:

```json
{
  "source": "BankingRegulation",
  "year": 2026,
  "document_type": "aml_law"
}
```

Expected behavior:

```text
The system retrieves AML law chunks and returns cited anti-money-laundering measures.
```

## Frontend Demo

Run the frontend:

```bash
cd frontend
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

The frontend includes:

- example question buttons,
- metadata filters,
- advanced retrieval settings,
- full RAG answer mode,
- retrieve-only debug mode,
- backend health check,
- loading and error states,
- request duration,
- answer cards,
- citation badges,
- collapsible source cards,
- retrieval score display.

The frontend API URL is configured in:

```text
frontend/config.js
```

Local version:

```javascript
window.APP_CONFIG = {
  API_BASE_URL: "http://127.0.0.1:8000"
};
```

For EC2 deployment, change it to:

```javascript
window.APP_CONFIG = {
  API_BASE_URL: "http://YOUR_EC2_PUBLIC_IP:8000"
};
```

## Evaluation

Run the evaluation pipeline:

```bash
python main.py
```

The evaluator checks:

- retrieved source correctness,
- retrieved document type correctness,
- expected keyword coverage in retrieved chunks,
- answer non-empty status,
- citation presence,
- citation validity,
- answer keyword coverage,
- concept completeness,
- aggregate summary metrics.

Example output:

```text
Retrieval source pass rate: 1.00
Retrieval type pass rate: 1.00
Retrieval keyword pass rate: 1.00
Citation validity pass rate: 1.00
Average answer keyword coverage: 0.92
Average concept coverage: 0.92
```

## Docker

Build and run the production-style local stack:

```bash
docker compose -f docker-compose.prod.yml up --build
```

Stop:

```bash
docker compose -f docker-compose.prod.yml down
```

Services:

```text
Qdrant:   http://127.0.0.1:6333
API:      http://127.0.0.1:8000
Frontend: http://127.0.0.1:5500
```

The production compose file expects:

```text
.env.production
cache/chunks.json
qdrant_storage/
```

## AWS EC2 Deployment

This project is prepared for a simple AWS EC2 deployment using Docker Compose.

Architecture:

```text
AWS EC2 Ubuntu Server
    |
    +--> Qdrant container
    |
    +--> FastAPI backend container
    |
    +--> Frontend container
```

Deployment files:

```text
deployment/ec2-setup.sh    Install Docker and Docker Compose plugin
deployment/deploy.sh       Start production Docker Compose stack
deployment/stop.sh         Stop production Docker Compose stack
```

On EC2, create `.env.production`:

```env
OPENAI_API_KEY=your_real_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

FRONTEND_ORIGINS=http://YOUR_EC2_PUBLIC_IP:5500

QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

Update `frontend/config.js`:

```javascript
window.APP_CONFIG = {
  API_BASE_URL: "http://YOUR_EC2_PUBLIC_IP:8000"
};
```

Start:

```bash
bash deployment/deploy.sh
```

Stop:

```bash
bash deployment/stop.sh
```

## Repository Layout

```text
api/                       FastAPI app
data/                      Financial, macroeconomic, and regulatory PDFs
deployment/                EC2 deployment helper scripts
frontend/                  Browser demo UI
scripts/                   Indexing and cache-building scripts
src/embedding/             BGE-M3 embedding wrapper
src/eval/                  RAG evaluation pipeline
src/generation/            Context formatting and answer generation
src/ingestion/             PDF loading, chunking, and chunk cache
src/metadata/              Metadata extraction
src/retrieval/             Dense, BM25, hybrid retrieval, and reranking
src/vectorstore/           Qdrant integration
Dockerfile.api             Backend Dockerfile
Dockerfile.frontend        Frontend Dockerfile
docker-compose.prod.yml    Production-style compose file
```

## Limitations

This project is an engineering prototype, not a production financial assistant.

Current limitations:

- The evaluation set is small and should be expanded.
- The evaluator is rule-based and does not fully measure factual faithfulness.
- Retrieved chunks can contain mixed topics, which can cause answer-generation errors.
- Some PDF extraction artifacts remain, especially spacing issues in Russian documents.
- The system does not yet use sentence-level context filtering.
- The frontend is a lightweight demo UI, not a production web application.
- EC2 deployment is simple Docker Compose deployment, not a fully managed cloud-native setup.
- The system is not suitable for real financial customer use without compliance review, monitoring, access control, and human escalation flows.

## Future Improvements

- Add claim-level faithfulness evaluation
- Add sentence-level context filtering before answer generation
- Improve PDF text cleaning
- Add more evaluation cases
- Add streaming responses
- Add authentication
- Add Nginx reverse proxy
- Add HTTPS with Certbot
- Move frontend to S3 + CloudFront
- Move backend to ECS, App Runner, or Fargate
- Move Qdrant to Qdrant Cloud
- Add LangSmith tracing
- Add LangGraph workflow orchestration
- Add CI/CD with GitHub Actions

## Final Takeaway

For financial RAG systems, retrieval quality and evaluation matter as much as answer generation.

The most useful architecture here is:

```text
metadata-aware document ingestion
+ dense retrieval
+ BM25 lexical search
+ hybrid fusion
+ reranking
+ cited generation
+ retrieval-only debugging
+ evaluation
```

This makes the system easier to inspect, debug, and improve than a simple prompt-based PDF chatbot.
