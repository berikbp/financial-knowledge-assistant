from src.embedding.bge_embedder import BGEM3Embedder
from src.vectorstore.qdrant_store import QdrantStore

class DenseRetriever:
    def __init__(self):
        self.embedder = BGEM3Embedder()
        self.store = QdrantStore()

    def retrieve(self,
        query: str,
        limit: int = 5,
        filters: dict | None = None):

        query_vector = self.embedder.embed_query(query)

        return self.store.search(query_vector, limit, filters)
