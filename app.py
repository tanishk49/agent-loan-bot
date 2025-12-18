import streamlit as st
from agents.master_agent import master_agent_response
from memory import init_memory, reset_memory
import os
import csv 

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Personal Loan Assistant",
    page_icon="💼",
    layout="wide"
)

# ---------------- TITLE ----------------
st.title("AI Personal Loan Assistant")
st.caption("Agentic AI-powered Digital Sales Assistant for NBFC Personal Loans")

# ---------------- SESSION STATE INIT ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "memory" not in st.session_state:
    st.session_state.memory = init_memory()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Loan Journey Tracker")

    # -------- LANGUAGE SELECTOR (NEW) --------
    st.subheader("Language Preference")

    language_map = {
        "Auto Detect": None,
        "English": "en",
        "Hindi": "hi",
        "Marathi": "mr",
        "Tamil": "ta",
        "Telugu": "te"
    }

    selected_language = st.selectbox(
        "Choose language",
        list(language_map.keys()),
        index=0
    )

    # Optional override: store language in memory
    if language_map[selected_language]:
        st.session_state.memory["lang"] = language_map[selected_language]

    st.divider()

    # -------- JOURNEY STAGES --------
    stages = [
        ("start", "Conversation Start"),
        ("awaiting_kyc", "KYC Collection"),
        ("kyc_pending", "KYC Verification"),
        ("sales_discovery", "Sales Discovery"),
        ("sales_amount", "Loan Requirement"),
        ("underwriting", "Underwriting"),
        ("salary_slip_required", "Salary Slip Check"),
        ("risk", "Risk Assessment"),
        ("sanction_prompt", "Sanction Approval"),
        ("completed", "Loan Sanctioned"),
        ("rejected", "Application Approval")
    ]

    current_stage = st.session_state.memory.get("stage", "start")

    for stage_key, stage_label in stages:
        if stage_key == current_stage:
            st.success(stage_label)
        else:
            st.write(stage_label)

    st.divider()

    if st.button("Start New Application"):
        st.session_state.chat_history = []
        st.session_state.memory = reset_memory()
        st.rerun()

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Reply here...")

if user_input:
    # User message
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Agent response
    response = master_agent_response(
        user_input,
        st.session_state.chat_history,
        st.session_state.memory
    )

    st.session_state.chat_history.append(
        {"role": "assistant", "content": response}
    )
    with st.chat_message("assistant"):
        st.markdown(response)

# ---------------- PROGRESS BAR ----------------
progress_map = {
    "start": 10,
    "awaiting_kyc": 20,
    "kyc_pending": 30,
    "sales_discovery": 45,
    "sales_amount": 55,
    "underwriting": 65,
    "salary_slip_required": 75,
    "risk": 85,
    "sanction_prompt": 95,
    "completed": 100,
    "rejected": 100
}

stage = st.session_state.memory.get("stage", "start")

if stage not in ["completed", "rejected"]:
    st.progress(progress_map.get(stage, 10))

# ---------------- PDF DOWNLOAD ----------------
sanction_file = st.session_state.memory.get("sanction_file")

if stage == "completed" and sanction_file and os.path.exists(sanction_file):
    st.divider()
    st.subheader("Loan Approved Successfully")

    st.markdown(
        """
        **Thank you for choosing us for your personal loan needs.**  

        We're pleased to inform you that your personal loan has been **successfully sanctioned**.  
        Please download your official sanction letter below for your reference.
        """
    )

    with open(sanction_file, "rb") as pdf_file:
        st.download_button(
            label="Download Sanction Letter (PDF)",
            data=pdf_file,
            file_name="Loan_Sanction_Letter.pdf",
            mime="application/pdf"
        )

    st.success(
         """
        ✅ **Next Steps:**  
        - Our team will contact you shortly for **final documentation and disbursement**.    
        - For any assistance, you may continue this chat or reach out through our official support channels.

        We appreciate your trust and look forward to serving you again.
        """
    )    
    # --- Feedback section ---
    st.divider()
    st.subheader("We Value Your Feedback")
    rating = st.radio(
        "How would you rate your experience with our AI Loan Assistant?",
        [1, 2, 3, 4, 5],
        horizontal=True
    )
    feedback = st.text_area(
        "Any feedback or suggestions for us? (Optional)",
        placeholder="Tell us what you liked or how we can improve..."
    )

    if st.button("Submit Feedback"):
         feedback_file = "feedback_data/feedback.csv"
         
    
         if not os.path.exists(feedback_file):
            with open(feedback_file, "w", newline="", encoding="utf-8") as f:
             writer = csv.writer(f)
             writer.writerow(["rating", "feedback"])
         
         # Append feedback
         with open(feedback_file, "a", newline="", encoding="utf-8") as f:
             writer = csv.writer(f)
             writer.writerow([rating, feedback])

         st.success("Thank you for your feedback! Your response has been recorded.")   
         
     
    
    # ------ 
    # --- Feedback Summary ---
    st.divider()
    st.subheader("📊 Customer Feedback Summary")

    feedback_file = "feedback_data/feedback.csv"
    
    if os.path.exists(feedback_file):
       ratings = []
       with open(feedback_file, "r", encoding="utf-8") as f:
              reader = csv.DictReader(f)
              for row in reader:
                try:
                  ratings.append(int(row["rating"]))
                except:
                  pass
       if ratings:
           avg_rating = round(sum(ratings) / len(ratings), 2)
           st.metric("⭐ Average Rating", avg_rating)
           st.metric("🧾 Total Responses", len(ratings))
       else:
           st.info("No feedback submitted yet.")
           
    else:
           st.info("Feedback data not available yet.")
    
    

