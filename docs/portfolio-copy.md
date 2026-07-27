# Portfolio Copy

Ready-to-use copy for a CV, LinkedIn, or personal portfolio. The claims below
reflect the current implementation and three-case evaluation set.

## CV project entry

**Enterprise Financial RAG Assistant** — Python, FastAPI, Qdrant, BGE-M3,
BM25, OpenAI, Docker, AWS EC2

- Built and deployed an end-to-end financial RAG system over English and
  Russian banking, macroeconomic, and regulatory documents.
- Combined BGE-M3 dense retrieval and BM25 lexical search with Reciprocal Rank
  Fusion and cross-encoder reranking across a 3,127-chunk index.
- Added metadata filtering, retrieval-only debugging, cited answer generation,
  and an evaluation pipeline covering source accuracy, citation validity, and
  concept completeness.
- Containerized the API, frontend, and Qdrant services with Docker Compose and
  deployed the stack to AWS EC2.

## Short project description

An inspectable financial RAG assistant that combines dense and lexical search,
reranking, metadata filters, and cited answer generation. It supports English
and Russian financial documents, exposes retrieval and query APIs through
FastAPI, and runs as a Docker Compose stack on AWS EC2.

## LinkedIn post

I recently finished building and deploying an end-to-end financial RAG
assistant.

The project answers questions over English and Russian banking,
macroeconomic, and regulatory documents. Its retrieval pipeline combines
BGE-M3 embeddings in Qdrant, BM25 search, Reciprocal Rank Fusion, and
cross-encoder reranking before generating a cited answer.

I also built a retrieval-only debugging endpoint and an evaluation pipeline for
source accuracy, citation validity, keyword coverage, and concept
completeness. The current index contains 3,127 chunks, and the full stack runs
with FastAPI, a browser frontend, Qdrant, Docker Compose, and AWS EC2.

The most useful lesson was that RAG quality is not only a prompting problem.
Chunking, metadata, retrieval diagnostics, reranking, and evaluation determine
whether the final answer can be trusted.

Repository: https://github.com/berikbp/financial-knowledge-assistant

## Suggested LinkedIn tags

`#AIEngineering` `#RAG` `#LLM` `#FastAPI` `#VectorSearch` `#AWS`
