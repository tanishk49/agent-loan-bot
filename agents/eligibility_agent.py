def check_eligibility(income, employment_type, existing_emi):
    """
    Simple loan eligibility logic for personal loan.
    """

    income = float(income)
    existing_emi = float(existing_emi)

    # Eligibility rules
    max_emi_allowed = 0.4 * income  # 40% rule
    available_emi = max_emi_allowed - existing_emi

    if available_emi <= 0:
        return {
            "status": "rejected",
            "reason": "High existing EMI burden"
        }

    # Loan multiplier
    if employment_type.lower() == "salaried":
        multiplier = 15
    else:
        multiplier = 10  # self-employed

    eligible_amount = income * multiplier

    return {
        "status": "approved",
        "eligible_amount": int(eligible_amount),
        "available_emi": int(available_emi)
    }
