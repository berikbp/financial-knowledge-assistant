import re
from rank_bm25 import BM25Okapi

from src.ingestion.models import Chunk


def tokenize(text: str) -> list[str]:
    text = text.lower()


    tokens = re.findall(
        r"[a-zа-яәіңғүұқөһ0-9+]+",
        text
    )

    return tokens


class BM25Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunk = chunks

        self.tokenized_chunks = [
            tokenize(chunk.text) for chunk in chunks
        ]

        self.bm25 = BM25Okapi(self.tokenized_chunks)

    def retrieve(self, query: str, limit: int = 5, filters: dict | None = None):
        tokenized_query = tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        scored_chunks = []

        for chunk, score in zip(self.chunk, scores):
            if filters and not self._match_filters(chunk, filters):
                continue
            
            scored_chunks.append((chunk, score))

        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        return scored_chunks[:limit]
    

    def _match_filters(self, chunk: Chunk, filters: dict) -> bool:
        for key, value in filters.items():
            if chunk.metadata.get(key) != value:
                return False
        return True