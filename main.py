from src.ingestion.pdf_loader import load_documents
from src.ingestion.chunking import chunk_documents

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



    documents = load_documents("data")

    print(f"Loaded {len(documents)} documents")

    for doc in documents:
        print("=" * 80)
        print(doc.source)
        print(doc.metadata)

    chunks = chunk_documents(documents)

    print(f"\nChunked {len(chunks)} chunks")
    print("\nFirst chunk metadata:")
    print(chunks[0].metadata)



    # embedder =BGEM3Embedder()
    # store = QdrantStore()
    
    # query = "Какие факторы влияли на инфляцию в Казахстане в 2026 году?"

    # query_embedding = embedder.embed_query(query)

    # results = store.search(query_vector=query_embedding, limit=5)

    # print(f"Query: {query}")
    # print("=" * 60)
    # for result in results:

    #     print(result.payload)
if __name__ == "__main__":
    main()
