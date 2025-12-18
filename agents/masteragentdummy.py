import ollama
from prompts import SYSTEM_PROMPT
from .verification_agent import verify_kyc
from .risk_agent import assess_risk
from .sanction_agent import generate_sanction
from utils.language_support import detect_language, to_english, from_english


def master_agent_response(user_input, chat_history, memory):

    # =================================================
    # LANGUAGE HANDLING (MULTILINGUAL SUPPORT)
    # =================================================
    detected_lang = detect_language(user_input)

    if "lang" not in memory:
        memory["lang"] = detected_lang

    user_lang = memory["lang"]

    # Translate user input to English for internal processing
    user_input_en = to_english(user_input, user_lang)
    user_input_lower = user_input_en.lower().strip()

    # Helper to translate output back to user language
    def reply(text):
        return from_english(text, user_lang)

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
        return reply(
            "Sure, let's start fresh. How can I help you with a personal loan today?"
        )

    # =================================================
    # NAME DISCOVERY
    # =================================================
    if memory.get("name") is None and "my name is" in user_input_lower:
        memory["name"] = user_input_en.split("is")[-1].strip()
        memory["stage"] = "awaiting_kyc"

        return reply(
            f"Nice to meet you, {memory['name']}.\n\n"
            "To proceed, I will need to verify your KYC.\n"
            "Please share your PAN and phone number.\n\n"
            "Format:\nPAN: XXXXX1234X, Phone: XXXXXXXXXX"
        )

    # =================================================
    # KYC INPUT
    # =================================================
    if memory.get("stage") == "awaiting_kyc" and "pan" in user_input_lower and "phone" in user_input_lower:
        try:
            parts = user_input_en.split(",")
            memory["pan"] = parts[0].split(":")[1].strip()
            memory["phone"] = parts[1].split(":")[1].strip()
            memory["stage"] = "kyc_pending"
            return reply("Thank you. Verifying your KYC details now.")
        except:
            return reply(
                "Please provide details in the format:\nPAN: XXXXX1234X, Phone: XXXXXXXXXX"
            )

    # =================================================
    # KYC VERIFICATION (AUTO)
    # =================================================
    if memory.get("stage") == "kyc_pending":

        result = verify_kyc(memory["name"], memory["pan"], memory["phone"])

        if result["status"] != "verified":
            memory["stage"] = "awaiting_kyc"
            return reply(
                "KYC verification failed. Please recheck your PAN and phone number."
            )

        memory.update({
            "city": result["city"],
            "credit_score": int(result["credit_score"]),
            "preapproved_limit": int(result["preapproved_limit"]),
            "employment_type": result["employment_type"],
            "current_loan_emi": int(result["current_loan_emi"]),
            "stage": "sales_discovery"
        })

        return reply(
            "KYC verified successfully.\n\n"
            f"Name: {result['name']}, City: {result['city']}, "
            f"Employment Type: {result['employment_type']}\n\n"
            "To help you better, may I know what you plan to use this loan for?\n"
            "(medical, education, travel, or personal needs)"
        )

    # =================================================
    # SALES DISCOVERY
    # =================================================
    if memory.get("stage") == "sales_discovery":
        memory["loan_purpose"] = user_input_en.strip()
        memory["stage"] = "sales_amount"

        purpose = memory["loan_purpose"].lower()

        if "medical" in purpose:
            pitch = "I understand medical expenses can be urgent. Our loans are processed quickly."
        elif "education" in purpose:
            pitch = "Education is an important investment. A personal loan can help manage these expenses."
        elif "travel" in purpose:
            pitch = "Travel planning is exciting. A personal loan can help you manage costs smoothly."
        else:
            pitch = "Personal loans are flexible and suitable for various personal needs."

        return reply(
            f"{pitch}\n\n"
            "Please tell me the loan amount you are looking for (in INR)."
        )

    # =================================================
    # SALES AMOUNT
    # =================================================
    if memory.get("stage") == "sales_amount":
        try:
            memory["requested_amount"] = int(user_input_en.replace(",", "").strip())
            memory["stage"] = "underwriting"
        except:
            return reply(
                "Please enter a valid loan amount in numbers (for example: 300000)."
            )

    # =================================================
    # UNDERWRITING (AUTO)
    # =================================================
    if memory.get("stage") == "underwriting":

        requested = memory["requested_amount"]
        limit = memory["preapproved_limit"]
        credit_score = memory["credit_score"]

        if credit_score < 700:
            memory["stage"] = "rejected"
            return reply(
                f"Loan rejected due to low credit score.\n\n"
                f"Credit Score: {credit_score}\n"
                "Minimum required score is 700."
            )

        if requested <= limit:
            memory["eligible_amount"] = requested
            memory["stage"] = "risk"
            memory["risk_completed"] = False

            return reply(
                "Your loan is approved based on the pre-approved offer.\n\n"
                f"Requested Amount: ₹{requested}\n"
                f"Pre-approved Limit: ₹{limit}\n\n"
                "Proceeding with risk assessment."
            )

        if requested <= 2 * limit:
            memory["stage"] = "salary_slip_required"
            return reply(
                "Additional verification is required.\n\n"
                "Please upload your latest salary slip for further review."
            )

        memory["stage"] = "rejected"
        return reply(
            f"Loan rejected.\n\n"
            f"Requested amount exceeds the maximum allowed limit of ₹{2 * limit}."
        )

    # =================================================
    # SALARY SLIP (SIMULATED)
    # =================================================
    if memory.get("stage") == "salary_slip_required":
        memory["eligible_amount"] = memory["requested_amount"]
        memory["stage"] = "risk"
        memory["risk_completed"] = False
        return reply(
            "Salary slip verified successfully.\n\nProceeding with final risk assessment."
        )

    # =================================================
    # RISK ASSESSMENT (AUTO)
    # =================================================
    if memory.get("stage") == "risk" and not memory.get("risk_completed"):

        result = assess_risk(
            int(memory["eligible_amount"]),
            memory["employment_type"],
            int(memory["current_loan_emi"])
        )

        rate = result["interest_rate"]
        if isinstance(rate, str):
            rate = rate.replace("%", "").strip()
        result["interest_rate"] = float(rate)

        memory["risk_result"] = result
        memory["risk_completed"] = True

        if result["decision"] != "approved":
            memory["stage"] = "rejected"
            return reply(
                f"Loan rejected after risk assessment.\n\nReason: {result['reason']}"
            )

        memory["stage"] = "sanction_prompt"
        return reply(
            "Credit assessment completed.\n\n"
            f"Credit Score: {memory['credit_score']}\n"
            f"Risk Level: {result['risk_level']}\n"
            f"Interest Rate: {result['interest_rate']}%\n\n"
            "Your loan is approved.\n"
            "Would you like to proceed with final loan sanction? (yes / no)"
        )

    # =================================================
    # SANCTION
    # =================================================
    if memory.get("stage") == "sanction_prompt":

        if user_input_lower == "yes":
            sanction = generate_sanction(
                memory["name"],
                int(memory["eligible_amount"]),
                float(memory["risk_result"]["interest_rate"])
            )

            memory["stage"] = "completed"
            memory["sanction_file"] = sanction["file_path"]

            return reply(
                "Your loan has been sanctioned successfully.\n\n"
                f"Loan Amount: ₹{sanction['loan_amount']}\n"
                f"Interest Rate: {sanction['interest_rate']}%\n"
                f"Tenure: {sanction['tenure']}\n"
                f"Monthly EMI: ₹{sanction['emi']}\n\n"
                "You may download your sanction letter below."
            )

        if user_input_lower == "no":
            memory["stage"] = "completed"
            return reply(
                "No problem. You can reach out anytime if you wish to proceed later."
            )

        return reply("Please reply with yes or no.")

    # =================================================
    # COMPLETION MESSAGE (NO OLLAMA CALL)
    # =================================================
    if memory.get("stage") == "completed":
        return reply(
            "Thank you for choosing our service.\n\n"
            "If you need any assistance in the future, feel free to reach out."
        )

    # =================================================
    # FALLBACK (LLM – SAFE)
    # =================================================
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_input_en})

    response = ollama.chat(model="llama3.1", messages=messages)
    return from_english(response["message"]["content"], user_lang)
