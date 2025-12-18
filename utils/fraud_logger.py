import csv
import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "fraud_logs.csv")


def log_fraud_event(data: dict):
    """
    Append fraud assessment details to CSV for analytics & audit
    """

    os.makedirs(LOG_DIR, exist_ok=True)

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "customer_name",
                "credit_score",
                "requested_amount",
                "preapproved_limit",
                "employment_type",
                "fraud_flag",
                "reason"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "customer_name": data.get("customer_name"),
            "credit_score": data.get("credit_score"),
            "requested_amount": data.get("requested_amount"),
            "preapproved_limit": data.get("preapproved_limit"),
            "employment_type": data.get("employment_type"),
            "fraud_flag": data.get("fraud_flag"),
            "reason": data.get("reason")
        })
