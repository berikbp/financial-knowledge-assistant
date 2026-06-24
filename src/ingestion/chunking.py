from src.ingestion.models import Document, Chunk


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    Removes empty lines and very short PDF artifacts.
    """

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if len(line) < 2:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 250,
) -> list[str]:
    """
    Split text into chunks while preserving paragraph boundaries.
    """

    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be greater than chunk_overlap")

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        candidate = (
            current_chunk + "\n" + paragraph
            if current_chunk
            else paragraph
        )

        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            if len(paragraph) > chunk_size:
                start = 0

                while start < len(paragraph):
                    end = start + chunk_size
                    piece = paragraph[start:end].strip()

                    if piece:
                        chunks.append(piece)

                    start += chunk_size - chunk_overlap

                current_chunk = ""
            else:
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def chunk_document(
    document: Document,
    chunk_size: int = 1200,
    chunk_overlap: int = 250,
) -> list[Chunk]:
    """
    Clean and chunk one Document into multiple Chunks.
    """

    cleaned_text = clean_text(document.text)

    text_chunks = chunk_text(
        cleaned_text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = []

    for i, text in enumerate(text_chunks):
        metadata = {
            **document.metadata,
            "chunk_id": i,
        }

        chunk = Chunk(
            text=text,
            source=document.source,
            path=document.path,
            chunk_id=i,
            metadata=metadata,
        )

        chunks.append(chunk)

    return chunks


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1200,
    chunk_overlap: int = 250,
) -> list[Chunk]:
    """
    Clean and chunk multiple Documents into multiple Chunks.
    """

    all_chunks = []

    for document in documents:
        chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        all_chunks.extend(chunks)

    return all_chunks