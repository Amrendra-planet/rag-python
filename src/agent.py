import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from .retrieval import load_runbooks, HybridRetriever

load_dotenv()

SYSTEM_PROMPT_TEMPLATE = """You answer operational questions using only the supplied runbook excerpts.

Rules:
- Cite only documents that actually support the answer.
- Do not choose a document merely because it is semantically similar.
- If the excerpts do not contain enough evidence, return no_match.
- cited_doc_ids must contain only supported RB ids.
- confidence must be high, medium, low, or no_match.
- Return valid JSON with exactly: answer, cited_doc_ids, confidence.
"""


def answer_question(question: str) -> dict:
    docs = load_runbooks()

    retriever = HybridRetriever(docs)

    candidates = retriever.retrieve(
        question,
        top_k=4
    )

    # HybridRetriever returns dictionaries:
    # {
    #     "id": "...",
    #     "content": "...",
    #     "score": ...,
    #     ...
    # }
    context = "\n\n".join(
        f"DOCUMENT {doc['id']}:\n{doc['content']}"
        for doc in candidates
    )

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        # Offline fallback
        best_doc = candidates[0] if candidates else None

        if not best_doc or best_doc["score"] < 0.3:
            return {
                "answer": "No supplied runbook contains enough information to answer this question.",
                "cited_doc_ids": [],
                "confidence": "no_match",
            }

        return {
            "answer": best_doc["content"],
            "cited_doc_ids": [best_doc["id"]],
            "confidence": "medium",
        }

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_TEMPLATE
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\n"
                    f"Runbook excerpts:\n{context}"
                )
            },
        ],
    )

    result = json.loads(response.choices[0].message.content)

    valid_ids = {doc["id"] for doc in candidates}

    result["cited_doc_ids"] = [
        x
        for x in result.get("cited_doc_ids", [])
        if x in valid_ids
    ]

    if not result["cited_doc_ids"]:
        result["confidence"] = "no_match"

    return result