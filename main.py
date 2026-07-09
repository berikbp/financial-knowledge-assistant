from src.ingestion.pdf_loader import load_documents
from src.ingestion.chunking import chunk_documents
from src.retrieval.pipeline import RetrievalPipeline
from src.generation.answer_generator import AnswerGenerator

from src.eval.evaluate_rag import (
    EVAL_CASES,
    evaluate_retrieval_case,
    print_retrieval_report,
    evaluate_answer_case,
    print_answer_report,
    summarize_reports,
    print_summary_report,
)


def main():
    documents = load_documents("data")
    chunks = chunk_documents(documents)

    retrieval_pipeline = RetrievalPipeline(chunks)
    answer_generator = AnswerGenerator()
    all_reports = []

    for case in EVAL_CASES:
        retrieval_report = evaluate_retrieval_case(
            case=case,
            pipeline=retrieval_pipeline,
        )

        print_retrieval_report(retrieval_report)

        answer_report = evaluate_answer_case(
            case=case,
            results=retrieval_report["results"],
            answer_generator=answer_generator,
        )

        print_answer_report(answer_report)

        all_reports.append({
            'case_id': case['id'],
            'retrieval': retrieval_report,
            'answer': answer_report,
        })

    summary = summarize_reports(all_reports)
    print_summary_report(summary)


    # test_answer = "Hello [1]. Another claim [2]."
    # print(check_citations(test_answer))



    # retriever = DenseRetriever()

    # query = 'Какие факторы влияли на инфляцию в Казахстане в 2026 году?',

    # results = retriever.retrieve(
    #     query = query,
    #     limit = 5,
    #     filters={
    #         'source': 'NationalBank',
    #         'year': 2026,
    #         'document_type': 'monetary_policy_report'
    #     }
    # )

    # documents = load_documents("data")
    # print(f"Loaded {len(documents)} documents")

    # chunks = chunk_documents(documents)
    # print(f"Chunked {len(chunks)} chunks")
    
    # embedder = BGEM3Embedder()

    # chunk_texts = [chunk.text for chunk in chunks]
    # embeddings = embedder.embed_texts(chunk_texts)

    # print(f"Embeddings shape: {len(embeddings)} x {len(embeddings[0])}")
    # print(f"Embedding dimension: {len(embeddings[0])}")

    # store = QdrantStore()
    # store.recreate_collection()

    # points = store.build_points(chunks, embeddings)
    # print(f"Built {len(points)} points")
    # store.upload_points(
    #     points,
    #     batch_size=128
    # )
    # print("All chunks uploaded successfully")










    # embedder = BGEM3Embedder()
    # store = QdrantStore()
    
    # query = "Какие факторы влияли на инфляцию в Казахстане в 2026 году?"

    # query_embedding = embedder.embed_query(query)

    # results = store.search(
    #     query_vector=query_embedding, 
    #     limit=5,
    #     filters={
    #         "source": "NationalBank",
    #         'year': 2026,
    #         'document_type': 'monetary_policy_report'
    #     }
    # )

    # print(f"Query: {query}")
    # print("=" * 60)

    # for result in results:
    #     payload = result.payload

    #     print(f"Score: {result.score:.4f}")
    #     print(f"Source: {payload.get('source')}")
    #     print(f"Document: {payload.get('document_name')}")
    #     print(f"Year: {payload.get('year')}")
    #     print(f"Type: {payload.get('document_type')}")
    #     print(f"Chunk ID: {payload.get('chunk_id')}")
    #     print("-" * 60)
    #     print(payload.get("text", "")[:1000])
    #     print("=" * 60)

if __name__ == "__main__":
    main()
