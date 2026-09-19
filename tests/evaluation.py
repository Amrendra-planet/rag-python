import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agent import answer_question

CASES = [

    # ============================================================
    # 1. DIRECT / EXACT QUESTIONS
    # ============================================================

    ("checkout-api is running hot on CPU - what should I check first?", ["RB-001"]),

    ("We're seeing 'too many connections' errors on checkout-api - what's the likely cause?", ["RB-002"]),

    ("How do I safely roll back checkout-api to a previous version?", ["RB-005"]),

    ("What's our policy for communicating an incident to customers?", ["RB-011"]),

    ("What happened during the checkout-api incident on 2026-08-10?", ["RB-012"]),


    # ============================================================
    # 2. PARAPHRASED / SEMANTIC QUESTIONS
    # Tests whether embeddings understand meaning
    # ============================================================

    ("Why is the checkout service consuming so much processor power?", ["RB-001"]),

    ("The checkout service is using excessive CPU. What are my first troubleshooting steps?", ["RB-001"]),

    ("The database connection pool for checkout seems exhausted. What could be causing it?", ["RB-002"]),

    ("The latest checkout deployment is causing problems. How can I revert it?", ["RB-005"]),

    ("How should customers be informed when there is a production outage?", ["RB-011"]),

    ("Can you explain the root cause of the checkout problem from August 10?", ["RB-012"]),


    # ============================================================
    # 3. SHORT QUERIES
    # Tests retrieval with very little context
    # ============================================================

    ("checkout CPU", ["RB-001"]),

    ("database connections", ["RB-002"]),

    ("checkout rollback", ["RB-005"]),

    ("customer incident communication", ["RB-011"]),

    ("August checkout incident", ["RB-012"]),


    # ============================================================
    # 4. NATURAL / CONVERSATIONAL QUESTIONS
    # ============================================================

    ("Hey, checkout-api is suddenly running really hot. What do I look at first?", ["RB-001"]),

    ("I'm getting a bunch of too many connections errors from checkout-api. Any idea what's going on?", ["RB-002"]),

    ("We pushed a bad checkout release. What's the safe way to undo it?", ["RB-005"]),

    ("We have a customer-facing outage. What does our incident communication process say?", ["RB-011"]),

    ("Can you remind me what caused that checkout incident back on August 10?", ["RB-012"]),


    # ============================================================
    # 5. TECHNICAL KEYWORD / EXACT TERM QUESTIONS
    # Tests lexical retrieval
    # ============================================================

    ("checkout-api CPU utilization is above 85%", ["RB-001"]),

    ("checkout-api is reporting too many connections", ["RB-002"]),

    ("previous stable version of checkout-api", ["RB-005"]),

    ("customer-facing incident updates", ["RB-011"]),

    ("2026-08-10 checkout-api root cause", ["RB-012"]),


    # ============================================================
    # 6. NOISY / TYPOS
    # Tests robustness
    # ============================================================

    ("checkout api cpu is going crazy what do i check", ["RB-001"]),

    ("too many db connctions on checkout api", ["RB-002"]),

    ("checkout deployment went bad how do i rever it", ["RB-005"]),

    ("customer outage comms policy?", ["RB-011"]),

    ("what caused checkout incident on 10 aug?", ["RB-012"]),


    # ============================================================
    # 7. MULTI-DOCUMENT / RELATED QUESTIONS
    # Depending on your evaluation logic, more than one
    # relevant document may be acceptable.
    # ============================================================

    ("checkout-api has a problem after a recent deployment. What should I investigate and how could I rollback?", 
     ["RB-001", "RB-005"]),

    ("The checkout service is failing and I need to investigate the issue and possibly revert the deployment.", 
     ["RB-001", "RB-005"]),

    ("What should I do if checkout-api is unhealthy and the current release needs to be reverted?", 
     ["RB-001", "RB-005"]),


    # ============================================================
    # 8. HISTORICAL / DATE-SPECIFIC QUESTIONS
    # ============================================================

    ("What was the root cause of the incident on 2026-08-10?", ["RB-012"]),

    ("How was the August 10 checkout incident resolved?", ["RB-012"]),

    ("What fix was applied during the 2026-08-10 checkout outage?", ["RB-012"]),

    ("What happened to checkout-api on August 10, 2026?", ["RB-012"]),


    # ============================================================
    # 9. UNANSWERABLE QUESTIONS
    # Correct behavior = no_match
    # ============================================================

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


    # ============================================================
    # 10. FALSE-PREMISE QUESTIONS
    # The question assumes information that isn't in the KB.
    # Correct behavior = no_match
    # ============================================================

    ("Why did Redis cause the checkout-api incident?", None),

    ("How did Kafka cause the August 10 checkout outage?", None),

    ("Why did the PostgreSQL migration cause the incident?", None),

    ("How did Kubernetes restart fix the checkout incident?", None),

    ("Why did the AWS region failure cause checkout-api to go down?", None),

    ("Why did the frontend React application cause the checkout outage?", None),


    # ============================================================
    # 11. RELATED BUT OUT-OF-DOMAIN QUESTIONS
    # Tests semantic false positives
    # ============================================================

    ("How do I monitor CPU usage on my personal laptop?", None),

    ("How do I create a React application?", None),

    ("What is the latest Python version?", None),

    ("How do I create a MongoDB index?", None),

    ("Explain the JavaScript event loop.", None),

    ("How do I deploy an Angular application?", None),

    ("What is the best database for an ecommerce application?", None),


    # ============================================================
    # 12. PARTIAL INFORMATION / EVIDENCE TESTS
    # The runbook may be related, but doesn't contain the
    # requested specific fact.
    # ============================================================

    ("Who discovered the root cause of the August 10 incident?", None),

    ("Who wrote the fix for the August 10 incident?", None),

    ("Which engineer performed the rollback?", None),

    ("What was the exact time the incident started?", None),

    ("What was the exact time the incident ended?", None),

    ("How many engineers participated in resolving the incident?", None),


    # ============================================================
    # 13. POTENTIALLY AMBIGUOUS QUESTIONS
    # Useful for testing retrieval quality
    # ============================================================

    ("checkout-api is having problems. What should I do?", ["RB-001"]),

    ("There is an issue with checkout-api. How can I fix it?", ["RB-001"]),

    ("Something went wrong with checkout-api after deployment.", ["RB-005"]),

    ("There was a checkout incident. What happened?", ["RB-012"]),

    ("Customers are affected by an incident. What should we communicate?", ["RB-011"]),
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
