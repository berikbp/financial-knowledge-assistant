from src.ingestion.pdf_loader import load_documents
from src.ingestion.chunking import chunk_documents
from src.ingestion.chunk_scale import save_chunks


def main():
    documents = load_documents("data")
    print(f"Loaded documents: {len(documents)}")

    chunks = chunk_documents(documents)
    print(f"Created chunks: {len(chunks)}")

    save_chunks(chunks)
    print("Saved chunks to cache/chunks.json")


if __name__ == "__main__":
    main()
