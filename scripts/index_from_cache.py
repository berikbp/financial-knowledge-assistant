import json

from src.ingestion.models import Chunk
from src.embedding.bge_embedder import BGEM3Embedder
from src.vectorstore.qdrant_store import QdrantStore


def load_chunks_from_cache(path: str = "cache/chunks.json") -> list[Chunk]:
    with open(path, "r", encoding="utf-8") as file:
        items = json.load(file)

    chunks = []
    for item in items:
        chunks.append(
            Chunk(
                text=item["text"],
                source=item["source"],
                path=item["path"],
                chunk_id=item["chunk_id"],
                metadata=item["metadata"],
            )
        )

    return chunks


def main():
    print("Loading chunks from cache/chunks.json...")
    chunks = load_chunks_from_cache()
    print(f"Loaded chunks: {len(chunks)}")

    print("Embedding chunks with BGE-M3...")
    embedder = BGEM3Embedder()
    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed_texts(texts)

    print(f"Created embeddings: {len(embeddings)}")
    print(f"Embedding dimension: {len(embeddings[0])}")

    print("Recreating Qdrant collection...")
    store = QdrantStore()
    store.recreate_collection()

    print("Uploading points to Qdrant...")
    points = store.build_points(chunks, embeddings)
    store.upload_points(points=points, batch_size=128)

    print("Indexing from cache finished successfully")


if __name__ == "__main__":
    main()
