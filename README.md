# Agentic AI Personal Loan Assistant

An Agentic AI-powered personal loan processing system that automates the end-to-end loan journey for NBFC-style lending workflows.  
The system uses a modular Master–Worker agent architecture to deliver explainable, scalable, and user-friendly loan processing.

---

## 🚀 Features

- Conversational AI-based loan application
- End-to-end loan journey automation
- Modular agent-based architecture
- KYC verification using structured data
- Rule-based underwriting and risk assessment
- Fraud screening and internal review routing
- Dynamic interest rate assignment
- Automated PDF loan sanction letter generation
- Real-time journey progress tracking
- User feedback collection

---

## 🧠 System Architecture

The system follows an **Agentic AI design** where a central **Master Agent** orchestrates multiple specialized agents:

### Core Agents
- **Master Agent** – Workflow orchestration and state management  
- **KYC Verification Agent** – PAN & phone validation  
- **Sales Discovery Agent** – Loan purpose and requirement capture  
- **Underwriting Agent** – Eligibility and limit checks  
- **Risk Assessment Agent** – Credit scoring and interest rate assignment  
- **Fraud Detection Agent** – Silent fraud screening  
- **Sanction Agent** – PDF sanction letter generation  

---

## 🧩 Technology Stack

- **Language:** Python  
- **Frontend:** Streamlit  
- **AI / LLM:** LLaMA 3.1 (via Ollama)  
- **Architecture:** Agentic AI (Master–Worker model)  
- **Data Handling:** Pandas, CSV-based mock datasets  
- **PDF Generation:** ReportLab  
- **State Management:** Custom memory store  
- **Visualization:** Streamlit components  

---

## 📂 Project Structure
```
AGENT-LOAN-BOT/
├── agents/
│ ├── master_agent.py
│ ├── verification_agent.py
│ ├── risk_agent.py
│ ├── fraud_agent.py
│ ├── eligibility_agent.py
│ └── sanction_agent.py
│
├── data/
│ └── kyc_data.csv
│
├── sanction_letters/
│
├── feedback_data/
│ └── feedback.csv
│
├── utils/
│ ├── fraud_logger.py
│ └── language_support.py
│
├── app.py
├── memory.py
├── prompts.py
├── requirements.txt
└── README.md
```


