import json
import os
from pathlib import Path

from src.ingestion.models import Chunk

CACHE_PATH = Path("cache/chunks.json")


def save_chunks(chunks: list[Chunk], cache_path: Path = CACHE_PATH) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    serialized_chunks = [
        {
            "text": chunk.text,
            "source": chunk.source,
            "path": chunk.path,
            "chunk_id": chunk.chunk_id,
            "metadata": chunk.metadata,
        }
        for chunk in chunks
    ]

    temp_path = cache_path.with_suffix(f"{cache_path.suffix}.tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(serialized_chunks, file, ensure_ascii=False, indent=2)

    os.replace(temp_path, cache_path)


def load_chunks(cache_path: Path = CACHE_PATH) -> list[Chunk]:
    with cache_path.open("r", encoding="utf-8") as file:
        serialized_chunks = json.load(file)

    chunks = []

    for item in serialized_chunks:
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


def chunks_cache_exists(cache_path: Path = CACHE_PATH) -> bool:
    return cache_path.exists()
