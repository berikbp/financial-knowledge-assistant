from sentence_transformers import SentenceTransformer

class BGEM3Embedder:
    def __init__(self):
        self.model = SentenceTransformer('BAAI/bge-m3')

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of texts into vectors.
        """
        embeddings = self.model.encode(
            texts,
            batch_size=16,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )

        return embedding.tolist()