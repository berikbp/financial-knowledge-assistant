# 60-Second Demo Script

## 0–10 seconds — Introduce the problem

“This is an enterprise financial knowledge assistant for English and Russian
banking, macroeconomic, and regulatory documents.”

Show the project title, the 3,127-chunk index, and the backend-online indicator.

## 10–25 seconds — Run a query

Select **Inflation factors** and click **Ask**.

“The request applies document metadata filters and runs dense BGE-M3 retrieval
and BM25 search in parallel.”

## 25–40 seconds — Explain the retrieval pipeline

Point to the pipeline panel while the request runs.

“The candidate lists are combined with Reciprocal Rank Fusion, reranked with a
cross-encoder, and passed to the answer model.”

## 40–52 seconds — Show evidence

Scroll from the cited answer to the source cards.

“Every answer includes citations. Each source exposes its document metadata,
text preview, and dense, BM25, fusion, and reranker scores.”

## 52–60 seconds — Close with engineering scope

“The system also has retrieval-only debugging, evaluation, FastAPI endpoints,
Docker Compose packaging, and an AWS EC2 deployment.”

End on the architecture diagram or GitHub repository page.
