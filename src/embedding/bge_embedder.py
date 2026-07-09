import os

from sentence_transformers import SentenceTransformer


class BGEM3Embedder:
    def __init__(self, model_name: str | None = None):
        model_name = model_name or os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
        cache_folder = os.getenv("SENTENCE_TRANSFORMERS_HOME") or os.getenv("HF_HOME")

        self.model = SentenceTransformer(
            model_name,
            device=os.getenv("EMBEDDING_DEVICE", "cpu"),
            cache_folder=cache_folder,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of texts into vectors.
        """
        embeddings = self.model.encode(
            texts,
            batch_size=16,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        return embedding.tolist()
