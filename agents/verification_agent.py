import pandas as pd

# Path to the KYC CSV file
KYC_DB_PATH = "data/kyc_data.csv"


def verify_kyc(name, pan, phone):
    """
    Verifies a user against the KYC database using PAN and phone number.

    Args:
        name (str): Name of the user (for reference only)
        pan (str): PAN number of the user
        phone (str/int): Phone number of the user

    Returns:
        dict: Verification result with customer profile if verified
    """

    # Load KYC data
    df = pd.read_csv(KYC_DB_PATH)

    # Normalize inputs
    pan = str(pan).strip().upper()
    phone = str(phone).strip()

    # Match PAN and phone
    match = df[
        (df["pan"].str.upper() == pan) &
        (df["phone"].astype(str) == phone)
    ]

    if match.empty:
        return {
            "status": "failed",
            "reason": "PAN or phone number not found in KYC records"
        }

    customer = match.iloc[0]

    return {
        "status": "verified",
        "name": customer["name"],
        "city": customer["city"],
        "address": customer["address"],
        "credit_score": int(customer["credit_score"]),
        "preapproved_limit": int(customer["preapproved_limit"]),
        "current_loan_emi": int(customer["current_loan_emi"]),
        "employment_type": customer["employment_type"]
    }
