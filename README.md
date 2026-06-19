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
Bash
# On Mac/Linux:
python -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
Install the required dependencies:

Bash
pip install -r requirements.txt
3. Configuration & API Keys (Optional but Recommended)
For maximum speed during the hackathon evaluation, the system is optimized to use Groq by default.

Create a new file named .env in the root directory and add your API keys:

Plaintext
GROQ_API_KEY="your_groq_api_key_here"
(Note: The system also supports Google Gemini, HuggingFace, and Local Ollama. You can switch between these dynamically using the Streamlit sidebar toggle in the app).

4. Application Launch & Data Initialization
Since the problem statement did not provide a live steel plant dataset, we engineered a robust synthetic generation pipeline to populate the AI's knowledge base.

Start the application:

Bash
streamlit run app.py
Once the application opens in your browser (http://localhost:8501), follow these steps to initialize the brain of the system:

Open the Left Sidebar.

Under the "Data Management" section, click "Generate Synthetic Data". Wait a few seconds for the green success message.

Next, click "Index Documents (RAG)". This will process all the generated text files and build the ChromaDB vector store. Wait for the success message.

5. Testing the System
Once the data is indexed, the system is fully operational. Navigate to the "💬 Maintenance Chat" tab to test the agentic pipeline:

Test 1: Core Diagnostics
Copy and paste this exact prompt to test the RAG and Diagnostic Agent:

"BF-001 is showing high vibration. What could be wrong?"

Test 2: Natural Language Feedback Loop
Test our seamless feedback classifier by replying to the bot's answer with:

"thanks, that makes sense" OR "that's incorrect"

The system will automatically bypass the heavy LLM processing loop, classify your intent, log the feedback score instantly, and return a fast UI confirmation.
