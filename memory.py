def init_memory():
    return {
        "stage": "start",

        # Customer identity
        "name": None,
        "city": None,

        # KYC
        "pan": None,
        "phone": None,

        # CRM / Bureau data
        "credit_score": None,
        "preapproved_limit": None,
        "employment_type": None,
        "current_loan_emi": None,

        # Sales agent
        "loan_purpose": None,
        "requested_amount": None,

        # Underwriting / Risk
        "eligible_amount": None,
        "risk_result": None,
        "risk_completed": False 
    }


def reset_memory():
    return init_memory()
