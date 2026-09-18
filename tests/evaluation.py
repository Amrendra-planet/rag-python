import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agent import answer_question

CASES = [

    # Information not present in runbooks
    ("Who was the engineer who fixed the checkout incident?", None),

    ("What was the exact salary of the engineer involved in the incident?", None),

    ("What Python version does the payroll system use?", None),

    ("What was the customer's compensation after the checkout outage?", None),

    ("Who approved the checkout-api rollback?", None),

    ("What Slack channel was used during the incident?", None),

    ("What was the exact number of users affected by the incident?", None),

    ("What was the name of the database server involved?", None),

    ("When will the next checkout-api deployment happen?", None),

    ("What is the database password for checkout-api?", None),
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
    print("\n==================")
    print(f"Score: {correct}/{total} ({correct/total:.0%})")
    print(counts)
    print("====================")

if __name__ == "__main__":
    main()
