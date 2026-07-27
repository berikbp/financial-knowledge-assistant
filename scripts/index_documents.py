from src.ingestion.pdf_loader import load_documents
from src.ingestion.chunking import chunk_documents
from src.embedding.bge_embedder import BGEM3Embedder
from src.vectorstore.qdrant_store import QdrantStore


def main():
    print("Loading documents...")
    documents = load_documents("data")
    print(f"Loaded documents: {len(documents)}")

    print("Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Created chunks: {len(chunks)}")

    print("Embedding chunks...")
    embedder = BGEM3Embedder()
    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed_texts(texts)

    print(f"Created embeddings: {len(embeddings)}")
    print(f"Embedding dimension: {len(embeddings[0])}")

    print("Recreating Qdrant collection...")
    store = QdrantStore()
    store.recreate_collection()

    print("Uploading points...")
    points = store.build_points(chunks, embeddings)
    store.upload_points(points=points, batch_size=128)

    print("Indexing finished successfully")


if __name__ == "__main__":
    main()
