from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingRetriever:
    def __init__(self):
        
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str):
        return self.model.encode(text, normalize_embeddings=True)

    def similarity(self, query_embedding, document_embedding):
        
        return float(np.dot(query_embedding, document_embedding))

    def retrieve(self, query: str, documents: list, top_k: int = 4):
        query_embedding = self.embed(query)

        results = []

        for document in documents:
            document_embedding = self.embed(document["content"])

            similarity = self.similarity(
                query_embedding,
                document_embedding
            )

            results.append({
                "id": document["id"],
                "content": document["content"],
                "score": similarity
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]