from src.ingestion.pdf_loader import load_documents
from src.ingestion.chunking import chunk_documents
from src.embeddins.bge_m3 import BGEM3Embedder
from src.vectorstore.qdrant_store import QdrantStore

def main():
    # documents = load_documents("data")
    # print(f"Loaded {len(documents)} documents")

    # chunks = chunk_documents(documents)
    # print(f"Chunked {len(chunks)} chunks")
    
    # embedder = BGEM3Embedder()

    # sample_chunks = [chunk.text for chunk in chunks]
    # embeddings = embedder.embed_texts(sample_chunks)

    # print(f"Embeddings shape: {len(embeddings)} x {len(embeddings[0])}")
    # print(f"Embedding dimension: {len(embeddings[0])}")


    # store = QdrantStore()
    # # full chunks
    # store.recreate_collection()

    # points = store.build_points(chunks, embeddings)
    # print(f"Built {len(points)} points")
    # store.upload_points(
    #     points,
    #     batch_size=128
    # )
    # print('All chunks uploaded successfully')





    embedder =BGEM3Embedder()
    store = QdrantStore()
    
    query = "Какие факторы влияли на инфляцию в Казахстане в 2026 году?"

    query_embedding = embedder.embed_query(query)

    results = store.search(query_vector=query_embedding, limit=5)

    print(f"Query: {query}")
    print("=" * 60)
    for result in results:

        print(f"Score: {result.score}")
        print(f"Text: {result.payload['text']}")
        print(f"Source: {result.payload['source']}")
        print(f"Path: {result.payload['path']}")
        print(f"Chunk ID: {result.payload['chunk_id']}")
        print("-" * 60)
if __name__ == "__main__":
    main()
