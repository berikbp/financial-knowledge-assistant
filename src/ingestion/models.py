from dataclasses import dataclass

@dataclass
class Document:
    text: str
    source: str
    path: str
    metadata: dict
    

@dataclass
class Chunk:
    text: str
    source: str
    path: str
    chunk_id: int
    metadata: dict
    