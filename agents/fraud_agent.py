# agents/fraud_agent.py
import csv
import os
from datetime import datetime


FRAUD_LOG_PATH = "data/fraud_cases.csv"


def assess_fraud(memory):
    """
    Simple rule-based fraud detection (demo purpose)
    Returns:
        {
            "is_fraud": bool,
            "reason": str
        }
    """

    reasons = []

    # Rule 1: Very low credit score
    if memory.get("credit_score", 0) < 650:
        reasons.append("Low credit score")

    # Rule 2: Very high loan request vs income proxy (preapproved limit)
    if memory.get("requested_amount", 0) > 3 * memory.get("preapproved_limit", 1):
        reasons.append("Requested amount unusually high")

    # Rule 3: High EMI burden
    if memory.get("current_loan_emi", 0) > 0.6 * memory.get("preapproved_limit", 1):
        reasons.append("High existing EMI burden")

    is_fraud = len(reasons) > 0

    return {
        "is_fraud": is_fraud,
        "reason": "; ".join(reasons)
    }


def log_fraud_case(memory, fraud_reason):
    """
    Logs fraud cases for developer / analytics review
    """
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.exists(FRAUD_LOG_PATH)

    with open(FRAUD_LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "name",
                "city",
                "credit_score",
                "requested_amount",
                "preapproved_limit",
                "employment_type",
                "reason"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            memory.get("name"),
            memory.get("city"),
            memory.get("credit_score"),
            memory.get("requested_amount"),
            memory.get("preapproved_limit"),
            memory.get("employment_type"),
            fraud_reason
        ])
