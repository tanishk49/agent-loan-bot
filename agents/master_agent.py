import ollama
from prompts import SYSTEM_PROMPT
from .verification_agent import verify_kyc
from .risk_agent import assess_risk
from .sanction_agent import generate_sanction
from .fraud_agent import assess_fraud, log_fraud_case


def master_agent_response(user_input, chat_history, memory):

    user_input_lower = user_input.lower().strip()

    # =================================================
    # RESET
    # =================================================
    if "reset" in user_input_lower or "start again" in user_input_lower:
        memory.clear()
        memory.update({
            "stage": "start",
            "name": None,
            "risk_completed": False
        })
        return "Sure, let's start fresh. How can I help you with a personal loan today?"

    # =================================================
    # NAME DISCOVERY
    # =================================================
    if memory.get("name") is None and "my name is" in user_input_lower:
        memory["name"] = user_input.split("is")[-1].strip()
        memory["stage"] = "awaiting_kyc"
        return (
            f"Nice to meet you, {memory['name']}!\n\n"
            "To proceed, I'll need to verify your KYC.\n"
            "Please share your PAN and phone number.\n\n"
            "Format:\nPAN: XXXXX1234X, Phone: XXXXXXXXXX"
        )

    # =================================================
    # KYC INPUT
    # =================================================
    if memory.get("stage") == "awaiting_kyc" and "pan" in user_input_lower and "phone" in user_input_lower:
        try:
            parts = user_input.split(",")
            memory["pan"] = parts[0].split(":")[1].strip()
            memory["phone"] = parts[1].split(":")[1].strip()
            memory["stage"] = "kyc_pending"
            return "Thanks. Verifying your KYC details now..."
        except Exception:
            return "Please provide details in format:\nPAN: XXXXX1234X, Phone: XXXXXXXXXX"

    # =================================================
    # KYC VERIFICATION
    # =================================================
    if memory.get("stage") == "kyc_pending":

        result = verify_kyc(memory["name"], memory["pan"], memory["phone"])

        if result["status"] != "verified":
            memory["stage"] = "awaiting_kyc"
            return "KYC verification failed. Please recheck your PAN and phone number."

        memory.update({
            "city": result["city"],
            "credit_score": int(result["credit_score"]),
            "preapproved_limit": int(result["preapproved_limit"]),
            "employment_type": result["employment_type"],
            "current_loan_emi": int(result["current_loan_emi"]),
            "stage": "sales_discovery"
        })

        return (
            f"KYC verified successfully.\n\n"
            f"Name: {result['name']}, City: {result['city']}, "
            f"Employment Type: {result['employment_type']}\n\n"
            "To help you better, may I know what you plan to use this loan for?"
        )

    # =================================================
    # SALES DISCOVERY
    # =================================================
    if memory.get("stage") == "sales_discovery":
        memory["loan_purpose"] = user_input.strip()
        memory["stage"] = "sales_amount"

        return (
            "Got it.\n\n"
            "Please tell me the loan amount you are looking for (in INR)."
        )

    # =================================================
    # SALES AMOUNT
    # =================================================
    if memory.get("stage") == "sales_amount":
        try:
            memory["requested_amount"] = int(user_input.replace(",", "").strip())
            memory["stage"] = "underwriting"
        except Exception:
            return "Please enter a valid loan amount (e.g. 300000)."

    # =================================================
    # UNDERWRITING
    # =================================================
    if memory.get("stage") == "underwriting":

        requested = memory["requested_amount"]
        limit = memory["preapproved_limit"]
        credit_score = memory["credit_score"]

        if credit_score < 700:
            memory["stage"] = "rejected"
            return "Loan rejected due to low credit score."

        if requested <= limit:
            memory["eligible_amount"] = requested

            fraud_result = assess_fraud(memory)
            if fraud_result["is_fraud"]:
                log_fraud_case(memory, fraud_result["reason"])
                memory["stage"] = "internal_review"
                return "Your application requires internal review."

            memory.update({
                "stage": "risk",
                "risk_completed": False
            })

            return "Proceeding with risk assessment."

        memory["stage"] = "rejected"
        return "Requested amount exceeds allowed limit."

    # =================================================
    # RISK ASSESSMENT (RUNS ONLY ONCE)
    # =================================================
    if memory.get("stage") == "risk":

        if memory.get("risk_completed"):
            return "Processing your application. Please wait..."

        result = assess_risk(
            int(memory["eligible_amount"]),
            memory["employment_type"],
            int(memory["current_loan_emi"])
        )

        # ✅ Normalize interest rate once
        ir = result.get("interest_rate", 0)
        if isinstance(ir, str):
            ir = ir.replace("%", "").strip()
        result["interest_rate"] = float(ir)

        memory["risk_result"] = result
        memory["risk_completed"] = True

        if result["decision"] != "approved":
            memory["stage"] = "rejected"
            return f"Loan rejected after risk assessment.\nReason: {result['reason']}"

        memory["stage"] = "sanction_prompt"
        return (
            "Credit assessment completed successfully.\n\n"
            f"Interest Rate: {result['interest_rate']}%\n\n"
            "Would you like to proceed with final loan sanction? (yes / no)"
        )

    # =================================================
    # SANCTION (🔥 FIXED)
    # =================================================
    if memory.get("stage") == "sanction_prompt":

        if user_input_lower == "yes":

            interest_rate = memory["risk_result"]["interest_rate"]
            eligible_amount = memory["eligible_amount"]

            sanction = generate_sanction(
                 memory["name"],                    
                 int(memory["eligible_amount"]),      
                 float(memory["risk_result"]["interest_rate"])
            )

            memory["stage"] = "completed"
            memory["sanction_file"] = sanction["file_path"]

            return (
                "🎉 Loan Approved Successfully!\n\n"
                f"Loan Amount: ₹{sanction['loan_amount']}\n"
                f"Interest Rate: {sanction['interest_rate']}%\n"
                f"Tenure: {sanction['tenure']}\n"
                f"Monthly EMI: ₹{sanction['emi']}\n\n"
                "Thank you for choosing us. Our team will contact you shortly "
                "for disbursement and further documentation."
            )

        if user_input_lower == "no":
            memory["stage"] = "completed"
            return "No problem. Feel free to reach out anytime."

        return "Please reply with yes or no."

    # =================================================
    # INTERNAL REVIEW
    # =================================================
    if memory.get("stage") == "internal_review":
        return "Your application is under internal review."

    # =================================================
    # FALLBACK (LLM)
    # =================================================
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_input})

    response = ollama.chat(model="llama3.1", messages=messages)
    return response["message"]["content"]
