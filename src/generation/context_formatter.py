from src.retrieval.hybrid_retriever import HybridResult


def format_context(results: list[HybridResult]) -> str:
    '''
      Convert retrieved chunks into citation-ready context

      Args:
        results: List of HybridResult objects

      Returns:
        Formatted context string
    '''

    context_blocks = []

    for i, result in enumerate(results, start=1):
        metadata = result.metadata
        
        document_name = metadata.get('document_name', 'Unknown Document')
        source = metadata.get('source', 'Unknown Source')
        year = metadata.get('year', 'Unknown Year')
        doc_type = metadata.get('document_type', 'Unknown Type')
        chunk_id = metadata.get('chunk_id', 'Unknown Chunk ID')
        reranker_score = result.metadata.get('reranker_score', 0.0)

        block = f"""
        [DOCUMENT {i}]
        Source: {document_name}
        Year: {year}
        Type: {doc_type}
        Chunk ID: {chunk_id}
        Reranker Score: {reranker_score:.4f}
        Content:
        {result.text}
        """

        context_blocks.append(block)

    return "\n\n\n\n\n".join(context_blocks)

def format_sources(results: list[HybridResult]) -> str:
    """
    Create readable source list for debugging or final display.
    """

    source_lines = []

    for i, result in enumerate(results, start=1):
        metadata = result.metadata

        line = (
            f"[{i}] {metadata.get('document_name')} | "
            f"{metadata.get('source')} | "
            f"{metadata.get('year')} | "
            f"{metadata.get('document_type')} | "
            f"chunk {metadata.get('chunk_id')}"
        )

        source_lines.append(line)

    return "\n".join(source_lines)

    