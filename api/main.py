import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.generation.answer_generator import AnswerGenerator
from src.ingestion.chunk_scale import chunks_cache_exists, load_chunks
from src.retrieval.hybrid_retriever import HybridResult
from src.retrieval.pipeline import RetrievalPipeline

logger = logging.getLogger(__name__)

load_dotenv()


def get_allowed_origins() -> list[str]:
    raw_origins = os.getenv(
        "FRONTEND_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500",
    )
    return [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

app = FastAPI(
    title="Enterprise Financial Knowledge Assistant",
    description="Hybrid RAG API for financial, banking, and macroeconomic documents.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str = Field(..., description="User question")
    filters: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata filters, e.g. source/year/document_type",
    )
    limit: int = Field(default=5, ge=1, le=10)
    hybrid_limit: int = Field(default=20, ge=5, le=50)
    dense_limit: int = Field(default=30, ge=5, le=100)
    bm25_limit: int = Field(default=30, ge=5, le=100)


class SourceItem(BaseModel):
    index: int
    document_name: str | None
    source: str | None
    year: int | None
    document_type: str | None
    chunk_id: int | None
    reranker_score: float | None
    rrf_score: float | None
    dense_score: float | None
    bm25_score: float | None
    text_preview: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    filters: dict[str, Any] | None
    sources: list[SourceItem]

class RetrieveResponse(BaseModel):
    query: str
    filters: dict[str, Any] | None
    sources: list[SourceItem]

if not chunks_cache_exists():
    raise RuntimeError(
        "Chunk cache not found. Run: uv run python -m scripts.build_chunk_cache"
    )

chunks = load_chunks()

retrieval_pipeline: RetrievalPipeline | None = None
answer_generator: AnswerGenerator | None = None



ALLOWED_FILTER_KEYS = {
    "source",
    "year",
    "document_type",
    "language",
}

ALLOWED_SOURCES = {
    "NationalBank",
    "HalykBank",
    "BankingRegulation",
}

ALLOWED_DOCUMENT_TYPES = {
    "monetary_policy_report",
    "financial_statement",
    "annual_report",
    "macro_market_overview",
    "inflation_report",
    "financial_stability_report",
    "balance_of_payments",
    "external_debt",
    "banking_law",
    "aml_law",
    "unknown",
}

ALLOWED_LANGUAGES = {
    "ru",
    "en",
}

def validate_filters(filters: dict[str, Any] | None) -> None:
    if filters is None:
        return

    for key, value in filters.items():
        if key not in ALLOWED_FILTER_KEYS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filter key: '{key}'. Allowed keys: {sorted(ALLOWED_FILTER_KEYS)}",
            )

        if key == "source" and value not in ALLOWED_SOURCES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source: '{value}'. Allowed sources: {sorted(ALLOWED_SOURCES)}",
            )

        if key == "document_type" and value not in ALLOWED_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document_type: '{value}'. Allowed document_types: {sorted(ALLOWED_DOCUMENT_TYPES)}",
            )

        if key == "language" and value not in ALLOWED_LANGUAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language: '{value}'. Allowed languages: {sorted(ALLOWED_LANGUAGES)}",
            )

        if key == "year" and not isinstance(value, int):
            raise HTTPException(
                status_code=400,
                detail="Invalid year: year must be an integer, e.g. 2026",
            )

def get_retrieval_pipeline() -> RetrievalPipeline:
    global retrieval_pipeline

    if retrieval_pipeline is None:
        retrieval_pipeline = RetrievalPipeline(chunks)

    return retrieval_pipeline


def get_answer_generator() -> AnswerGenerator:
    global answer_generator

    if answer_generator is None:
        answer_generator = AnswerGenerator()

    return answer_generator


def build_source_item(results: list[HybridResult]) -> list[SourceItem]:
    sources = []
    
    for index, result in enumerate(results, start=1):
        metadata = result.metadata

        sources.append(
            SourceItem(
                index=index,
                document_name=metadata.get("document_name"),
                source=metadata.get("source"),
                year=metadata.get("year"),
                document_type=metadata.get("document_type"),
                chunk_id=metadata.get("chunk_id"),
                reranker_score=metadata.get("reranker_score"),
                rrf_score=result.rrf_score,
                dense_score=result.dense_score,
                bm25_score=result.bm25_score,
                text_preview=result.text[:500],
            )
        )
    return sources

def retrieve_results(request: QueryRequest) -> list[HybridResult]:
    validate_filters(request.filters)
    results = get_retrieval_pipeline().retrieve(
        query=request.query,
        limit=request.limit,
        hybrid_limit=request.hybrid_limit,
        dense_limit=request.dense_limit,
        bm25_limit=request.bm25_limit,
        filters=request.filters,
    )
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="No relevant documents found for the given query and filters.",
        )

    return results

@app.get("/")
def root():
    return {
        "message": "Enterprise Financial Knowledge Assistant API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    pipeline = retrieval_pipeline

    return {
        "status": "ok",
        "chunks_loaded": len(chunks),
        "retrieval_initialized": pipeline is not None,
        "dense_retrieval_enabled": (
            pipeline is not None
            and pipeline.hybrid_retriever.dense_retriever is not None
        ),
        "dense_retrieval_error": (
            pipeline.hybrid_retriever.dense_disabled_reason
            if pipeline is not None
            else None
        ),
        "reranker_enabled": pipeline is not None and pipeline.reranker is not None,
        "reranker_error": (
            pipeline.reranker_disabled_reason if pipeline is not None else None
        ),
        "answer_generation_initialized": answer_generator is not None,
    }


@app.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {"description": "Invalid filter value"},
        404: {"description": "No relevant documents found"},
        500: {"description": "Internal query error"},
        502: {"description": "Answer generation failed"},
    },   
)
def query_rag(request: QueryRequest):
    try:
        results = retrieve_results(request)
        sources = build_source_item(results)

        try:
            answer = get_answer_generator().generate_answer(
                query=request.query,
                results=results,
            )
        except Exception as e:
            logger.exception("Answer generation failed")
            raise HTTPException(
                status_code=502,
                detail=f"Answer generation failed: {str(e)}",
            ) from e

        return QueryResponse(
            query=request.query,
            answer=answer,
            filters=request.filters,
            sources=sources,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal query error: {str(e)}",
        )


@app.post(
    '/retrieve', 
    response_model=RetrieveResponse,
    responses={
        400: {"description": "Invalid filter value"},
        404: {"description": "No relevant documents found"},
        500: {"description": "Internal retrieval error"},
    },
)
def retrieve(request: QueryRequest):
    try:
        results = retrieve_results(request)
        sources = build_source_item(results)

        return RetrieveResponse(
            query=request.query,
            filters=request.filters,
            sources=sources,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal retrieval error: {str(e)}",
        )
