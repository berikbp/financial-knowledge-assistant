import os

from sentence_transformers import CrossEncoder

from src.retrieval.hybrid_retriever import HybridResult


# Reranker class 
class BGERanker:
    def __init__(self, model_name: str | None = None):
        model_name = model_name or os.getenv("RERANKER_MODEL_NAME", "BAAI/bge-reranker-v2-m3")
        cache_dir = os.getenv("SENTENCE_TRANSFORMERS_HOME") or os.getenv("HF_HOME")

        self.model = CrossEncoder(
            model_name,
            device=os.getenv("RERANKER_DEVICE", "cpu"),
            cache_dir=cache_dir,
        )

    def rerank(self, query: str, results: list[HybridResult], limit: int = 5) -> list[HybridResult]:
        if not results:
            return []

        # Create pairs of (query, document) for reranking
        pairs =[(query, result.text) for result in results]


        # Predict scores using the reranker model
        scores = self.model.predict(pairs)
        reranked_results = []

        # Add reranker scores to results
        for result, score in zip(results, scores):
            result.metadata['reranker_score'] = float(score)
            reranked_results.append(result)


        reranked_results.sort(
            key = lambda x: x.metadata['reranker_score'],
            reverse = True
        )
        return reranked_results[:limit]
