import re
from pathlib import Path
from .embeddings import EmbeddingRetriever

STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "to", "of",
    "for", "on", "in", "with", "what", "how", "our",
    "we", "are", "was", "were", "be", "should", "i"
}


def tokenize(text: str):
    words = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
    return {
        word for word in words
        if word not in STOPWORDS
    }


def load_runbooks(directory="runbooks"):
    documents = []

    for path in sorted(Path(directory).glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()

        match = re.search(r"\bRB-\d{3}\b", content)

        if not match:
            match = re.search(r"\bRB-\d{3}\b", path.name)

        if not match:
            continue

        documents.append({
            "id": match.group(0),
            "content": content
        })

    return documents


def lexical_score(query: str, document: dict):
    query_tokens = tokenize(query)
    document_tokens = tokenize(document["content"])

    overlap = query_tokens.intersection(document_tokens)

    score = len(overlap)

    query_lower = query.lower()
    document_lower = document["content"].lower()

    if query_lower in document_lower:
        score += 5

    return score


class HybridRetriever:

    def __init__(self, documents):
        self.documents = documents
        self.semantic_retriever = EmbeddingRetriever()

    def retrieve(self, query: str, top_k: int = 4):

        # -----------------------------
        # 1. Lexical retrieval
        # -----------------------------
        lexical_results = []

        for document in self.documents:
            score = lexical_score(query, document)

            lexical_results.append({
                "id": document["id"],
                "content": document["content"],
                "lexical_score": score
            })

        lexical_results.sort(
            key=lambda item: item["lexical_score"],
            reverse=True
        )

        # -----------------------------
        # 2. Semantic retrieval
        # -----------------------------
        semantic_results = self.semantic_retriever.retrieve(
            query,
            self.documents,
            top_k=len(self.documents)
        )

        semantic_by_id = {
            item["id"]: item
            for item in semantic_results
        }

        # -----------------------------
        # 3. Combine scores
        # -----------------------------
        combined = []

        max_lexical = max(
            [item["lexical_score"] for item in lexical_results],
            default=1
        )

        if max_lexical == 0:
            max_lexical = 1

        for item in lexical_results:

            semantic_score = semantic_by_id[item["id"]]["score"]

            # Normalize lexical score to approximately 0-1.
            lexical_normalized = (
                item["lexical_score"] / max_lexical
            )

            # Hybrid weighting:
            # 40% lexical
            # 60% semantic
            final_score = (
                0.4 * lexical_normalized
                + 0.6 * semantic_score
            )

            combined.append({
                "id": item["id"],
                "content": item["content"],
                "lexical_score": item["lexical_score"],
                "semantic_score": semantic_score,
                "score": final_score
            })

        combined.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return combined[:top_k]


if __name__ == "__main__":

    documents = load_runbooks()

    retriever = HybridRetriever(documents)

    query = "checkout-api is running hot on CPU"

    results = retriever.retrieve(query)

    print("\nQuery:", query)
    print("\nHybrid retrieval results:\n")

    for result in results:
        print(
            f"{result['id']} "
            f"| final={result['score']:.3f} "
            f"| lexical={result['lexical_score']} "
            f"| semantic={result['semantic_score']:.3f}"
        )