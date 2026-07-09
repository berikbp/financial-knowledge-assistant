from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
)
import os


from src.ingestion.models import Chunk

COLLECTION_NAME = "financial_knowledge_base"


class QdrantStore:
    def __init__(self, host: str | None = None, port: int | None = None):
        host = host or os.getenv("QDRANT_HOST", "localhost")
        port = port or int(os.getenv("QDRANT_PORT", "6333"))

        self.client = QdrantClient(host=host, port=port)
        self.collection_name = COLLECTION_NAME

    def create_collection(self):
        collections = self.client.get_collections()

        existing = {
            collection.name for collection in collections.collections
        }

        if self.collection_name in existing:
            print(f"Collection {self.collection_name} already exists")
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

        print(f"Collection {self.collection_name} created")

    def build_points(self, chunks: list[Chunk], embeddings: list[list[float]]) -> list[PointStruct]:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have the same length")

        points = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "text": chunk.text,
                    "source": chunk.source,
                    "path": chunk.path,
                    "chunk_id": chunk.chunk_id,
                    **chunk.metadata,
                },
            )
            points.append(point)

        return points

    def upload_points(self, points: list[PointStruct], batch_size: int = 128):
        total = len(points)

        for start in range(0, total, batch_size):
            batch = points[start:start + batch_size]

            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
                wait=True,
            )

            print(f"Uploaded {start + len(batch)} / {total} points")

    def search(self, query_vector: list[float], limit: int = 5, filters: dict | None = None):
        query_filter = None

        if filters:
            conditions = []

            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )
            query_filter = Filter(must=conditions)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
            query_filter=query_filter,
        )

        return results.points

    def recreate_collection(self):
        collections = self.client.get_collections()

        existing = {
            collection.name for collection in collections.collections
        }

        if self.collection_name in existing:
            self.client.delete_collection(collection_name=self.collection_name)

            print(f"Collection {self.collection_name} deleted")

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

        print(f"Collection {self.collection_name} recreated")
