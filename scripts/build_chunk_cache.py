from src.ingestion.chunking import chunk_documents
from src.ingestion.chunk_scale import save_chunks
from src.ingestion.pdf_loader import load_documents


def main():
    print("Loading documents...")
    documents = load_documents("data")
    print(f"Loaded documents: {len(documents)}")

    print("Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Created chunks: {len(chunks)}")

    save_chunks(chunks)
    print("Saved chunks to cache/chunks.json")


if __name__ == "__main__":
    main()
