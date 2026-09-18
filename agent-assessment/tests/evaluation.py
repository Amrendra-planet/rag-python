import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent import answer_question

CASES = [
    ("name is checkout amrendrahhot ", ["RB-001"]),
    ("We're seeing 'too many connections' errors on checkout-api - what's the likely cause?", ["RB-002"]),
    ("How do I safely roll back checkout-api to a previous version?", ["RB-005"]),
    ("We had a checkout-api incident on 2026-08-10 - what was the root cause and how was it fixed?", ["RB-012"]),
    ("What's our policy for communicating an incident to customers?", ["RB-011"]),
    ("What is the recommended Python version ?", None),
]

def evaluate(expected, actual):
    cited = actual.get("cited_doc_ids", [])
    if expected is None:
        return "CORRECT_NO_MATCH" if not cited else "WRONG_DOC"
    if not cited:
        return "INCORRECT_NO_MATCH"
    return "RIGHT_DOC" if set(expected).issubset(set(cited)) else "WRONG_DOC"

def main():
    counts = {"RIGHT_DOC": 0, "WRONG_DOC": 0, "CORRECT_NO_MATCH": 0, "INCORRECT_NO_MATCH": 0}
    for i, (question, expected) in enumerate(CASES, 1):
        actual = answer_question(question)
        result = evaluate(expected, actual)
        counts[result] += 1
        print(f"\nQ{i}: {question}")
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        print(f"Result:   {result}")

    total = len(CASES)
    correct = counts["RIGHT_DOC"] + counts["CORRECT_NO_MATCH"]
    print("\n==============================")
    print(f"Score: {correct}/{total} ({correct/total:.0%})")
    print(counts)
    print("==============================")

if __name__ == "__main__":
    main()
