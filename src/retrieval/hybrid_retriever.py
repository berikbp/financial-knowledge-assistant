from dataclasses import dataclass
import logging

from src.ingestion.models import Chunk
from src.retrieval.bm25_retrieval import BM25Retriever
from src.retrieval.dense_retriever import DenseRetriever

logger = logging.getLogger(__name__)


@dataclass
class HybridResult:
    text: str
    metadata: dict
    rrf_score: float
    dense_score: float | None = None
    bm25_score: float | None = None


class HybridRetriever:
    def __init__(
        self,
        chunks: list[Chunk],
        dense_retriever: DenseRetriever | None = None,
        bm25_retriever: BM25Retriever | None = None,
    ):
        self.chunks = chunks
        self.dense_disabled_reason: str | None = None
        try:
            self.dense_retriever = dense_retriever or DenseRetriever()
        except Exception as exc:
            self.dense_disabled_reason = str(exc)
            logger.exception("Dense retrieval disabled")
            self.dense_retriever = None
        self.bm25_retriever = bm25_retriever or BM25Retriever(chunks)

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        dense_limit: int = 20,
        bm25_limit: int = 20,
        filters: dict | None = None,
        rrf_k: int = 60,
    ) -> list[HybridResult]:
        dense_results = []
        if self.dense_retriever is not None:
            try:
                dense_results = self.dense_retriever.retrieve(
                    query=query,
                    limit=dense_limit,
                    filters=filters,
                )
            except Exception as exc:
                self.dense_disabled_reason = str(exc)
                logger.exception("Dense retrieval failed; continuing with BM25 only")

        bm25_results = self.bm25_retriever.retrieve(
            query=query,
            limit=bm25_limit,
            filters=filters,
        )

        fused_results = {}

        # Dense results: Qdrant result objects
        for rank, result in enumerate(dense_results, start=1):
            payload = result.payload
            key = self._make_key(payload)

            if key not in fused_results:
                fused_results[key] = {
                    "text": payload.get("text", ""),
                    "metadata": payload,
                    "rrf_score": 0.0,
                    "dense_score": None,
                    "bm25_score": None,
                }

            fused_results[key]["rrf_score"] += self._rrf_score(rank, rrf_k)
            fused_results[key]["dense_score"] = float(result.score)

        # BM25 results: (Chunk, score)
        for rank, (chunk, score) in enumerate(bm25_results, start=1):
            metadata = chunk.metadata
            key = self._make_key(metadata)

            if key not in fused_results:
                fused_results[key] = {
                    "text": chunk.text,
                    "metadata": metadata,
                    "rrf_score": 0.0,
                    "dense_score": None,
                    "bm25_score": None,
                }

            fused_results[key]["rrf_score"] += self._rrf_score(rank, rrf_k)
            fused_results[key]["bm25_score"] = float(score)

        ranked_results = sorted(
            fused_results.values(),
            key=lambda item: item["rrf_score"],
            reverse=True,
        )

        final_results = []

        for item in ranked_results[:limit]:
            final_results.append(
                HybridResult(
                    text=item["text"],
                    metadata=item["metadata"],
                    rrf_score=item["rrf_score"],
                    dense_score=item["dense_score"],
                    bm25_score=item["bm25_score"],
                )
            )

        return final_results

    def _rrf_score(self, rank: int, k: int = 60) -> float:
        return 1.0 / (rank + k)

    def _make_key(self, metadata: dict) -> str:
        return f"{metadata.get('path')}::{metadata.get('chunk_id')}"
