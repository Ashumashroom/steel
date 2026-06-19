# 🏭 Intelligent Maintenance Wizard

**TATA Steel AI Hackathon 2026 | Round 2: Agentic AI Challenge**

The Intelligent Maintenance Wizard is an Agentic AI-powered decision-support platform designed to reduce unplanned downtime in steel manufacturing environments. Built using a multi-agent LangGraph architecture, the system combines real-time data analysis, retrieval-augmented generation (RAG) over equipment manuals, and autonomous reasoning to provide proactive maintenance strategies, root cause analysis, and instant diagnostic support.

## 🚀 Key Features
* **Multi-Agent Orchestration:** Uses LangGraph to route queries between specialized agents (Diagnostic, Root Cause Analysis, Maintenance Planning).
* **Self-Correcting Reasoning:** A Critic Agent evaluates drafted responses against source documents to prevent hallucinations.
* **Dynamic Knowledge Base (RAG):** Powered by ChromaDB for instant semantic search across equipment manuals, SOPs, and failure logs.
* **Conversational Feedback Loop:** Instantly captures engineer feedback directly in the chat to grade responses without disrupting the workflow.
* **Pluggable Inference:** Seamlessly switch between Groq, standard HuggingFace, Google Gemini, or local offline Ollama models.

---

## 🛠️ System Architecture Stack
* **Orchestration:** LangGraph & LangChain
* **Inference Engine:** Groq (Llama-3.3-70b / Llama-3.1-8b)
* **Vector Database:** ChromaDB
* **Frontend UI:** Streamlit
* **Machine Learning:** Scikit-learn (Isolation Forest for anomalies)

---

## 💻 Instructions to Run

### 1. Prerequisites
Ensure you have the following installed on your system:
* **Python 3.10+**
* **Git**

### 2. Local Installation Setup
Clone the repository to your local machine and navigate into the project directory:
```bash
git clone <your_repository_url>
cd <your_project_folder>
