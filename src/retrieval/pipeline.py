import logging
import os

from src.ingestion.models import Chunk
from src.retrieval.hybrid_retriever import HybridRetriever, HybridResult
from src.retrieval.reranker import BGERanker

logger = logging.getLogger(__name__)


class RetrievalPipeline:
    def __init__(self, chunks: list[Chunk]):
        self.hybrid_retriever = HybridRetriever(chunks)
        self.reranker_disabled_reason: str | None = None
        if os.getenv("ENABLE_RERANKER", "true").lower() in {"0", "false", "no"}:
            self.reranker_disabled_reason = "Disabled by ENABLE_RERANKER"
            self.reranker = None
            return

        try:
            self.reranker = BGERanker()
        except Exception as exc:
            self.reranker_disabled_reason = str(exc)
            logger.exception("Reranker disabled")
            self.reranker = None

    
    def retrieve(self, query: str, limit: int = 5,
        hybrid_limit: int = 20,
        dense_limit: int = 30,
        bm25_limit: int = 30,
        filters: dict | None = None,
        rrf_k: int = 60,
    ) -> list[HybridResult]:
        hybrid_results = self.hybrid_retriever.retrieve(
            query = query,
            limit = hybrid_limit,
            dense_limit = dense_limit,
            bm25_limit = bm25_limit,
            filters = filters,
        )

        if self.reranker is None:
            return hybrid_results[:limit]

        final_results = self.reranker.rerank(
            query = query,
            results = hybrid_results,
            limit = limit
        )

        return final_results
        
