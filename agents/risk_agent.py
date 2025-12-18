def assess_risk(income, employment_type, existing_emi):
    """
    Simple risk assessment logic (CIBIL-like simulation)
    """

    income = int(income)
    existing_emi = int(existing_emi)
    emi_ratio = existing_emi / income

    # Base score
    credit_score = 750

    # Penalize high EMI burden
    if emi_ratio > 0.5:
        credit_score -= 150
    elif emi_ratio > 0.35:
        credit_score -= 80

    # Penalize employment risk
    if employment_type.lower() == "self employed":
        credit_score -= 50

    # Risk decision
    if credit_score >= 720:
        return {
            "risk_level": "Low",
            "credit_score": credit_score,
            "decision": "approved",
            "interest_rate": "10.5%"
        }

    elif credit_score >= 650:
        return {
            "risk_level": "Medium",
            "credit_score": credit_score,
            "decision": "approved",
            "interest_rate": "14.5%"
        }

    else:
        return {
            "risk_level": "High",
            "credit_score": credit_score,
            "decision": "rejected",
            "reason": "Low creditworthiness based on risk assessment"
        }
