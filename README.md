# LawPilot AI ⚖️
### Navigate Legal Challenges. Know Your Rights. Take Action.

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io)
[![Test Suite](https://img.shields.io/badge/pytest-29%2F29%20passed-brightgreen.svg)]()
[![Evaluation Score](https://img.shields.io/badge/Evaluation%20Score-95.87%25%20(46%2F46)-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

> **Submission for Kuku AI Generalist Assignment — Problem 2: Build an AI Lawyer**  
> **Repository:** [https://github.com/madhav9127/LawPilot-AI](https://github.com/madhav9127/LawPilot-AI)  
> **Author:** Madhav

---

## 📌 Product Vision & Overview

**LawPilot AI** is an intelligent, single-page conversational legal assistant designed to bridge the access-to-justice gap for ordinary citizens across India.

Instead of navigating complex legal portals, multi-page websites, or filling out tedious multi-step intake forms, users interact with a **clean, ChatGPT-style conversational interface**. They can explain their problem naturally in **English, Hindi (हिंदी), or conversational Hinglish**, and LawPilot AI:
- Unpacks messy, unstructured situations into organized legal facts.
- Explains statutory rights and legal protections in simple, human language without confusing legal jargon.
- Retains multi-turn conversation memory, accumulating facts and gracefully handling user corrections.
- Enforces strict anti-hallucination guardrails grounded in verified [India Code](https://www.indiacode.nic.in/) statutes.
- Generates professional legal notice drafts and consumer complaint letters with one-click **PDF and DOCX export**.
- Escalates genuine emergencies (physical lockouts, threats of violence, medical distress) to official national helplines (**Police 112**, **NALSA 15100**, **Medical 108/112**, **NCH 1915**).

---

## 🖥️ User Interface Design: Clean & Focused

Following the design philosophy of modern conversational assistants (like ChatGPT / Claude):
- **Single-Page Simplicity:** No distracting tabs, no multi-page navigation menus, no corporate dashboards.
- **Welcoming First Screen:** Displays *"How can I help you today?"* with 4 quick clickable prompt suggestions:
  - *"My landlord is refusing to return my security deposit."*
  - *"I purchased a defective product and the seller is refusing a refund."*
  - *"My company has not paid my salary for two months."*
  - *"Help me understand a legal notice I received."*
- **Seamless Chat Transition:** Upon sending the first message, the welcome hero smoothly transitions into an active conversation view.
- **Multimodal Inputs:** Built-in Web Speech API microphone for voice input, plus a document attachment button for lease agreements or receipts.
- **Actionable Message Controls:** Small inline action pills beneath AI responses:
  - 📋 **Copy Response**
  - 📄 **Draft Legal Notice** (generates downloadable PDF/DOCX notice drafts directly in chat)
  - 📊 **Summarize Case** (displays current structured fact profile)
- **Live Grounding Indicator:** A status pill in the top header displaying `● Grounded in Indian Law (India Code)`.

---

## ⚖️ Core Legal Scope (3 Everyday Domains)

LawPilot AI provides deep, specialized statutory reasoning across three high-frequency everyday domains:

### 1. Tenant & Landlord Disputes
- **Statutes:** *Transfer of Property Act, 1882* (Sections 106, 108(m), 108(f)), *Model Tenancy Act, 2021*, state rent control precedents.
- **Common Scenarios:** Security deposit withholding, arbitrary painting/maintenance deductions, unwritten/oral leases, urgent roof/seepage repairs, and illegal eviction threats without court orders.

### 2. Consumer Protection
- **Statutes:** *Consumer Protection Act, 2019* (Sections 2(7), 2(47), 35, 84, 85).
- **Common Scenarios:** Defective smartphones/laptops, refund delays between merchant and payment gateway, wrong e-commerce deliveries, undelivered paid services, and filing before District Consumer Commissions (e-Daakhil).

### 3. Employment & Wage Disputes
- **Statutes:** *Payment of Wages Act, 1936* (Sections 5, 7, 15), *Indian Contract Act, 1872* (Sections 27, 73), State Shops and Commercial Establishments Acts.
- **Common Scenarios:** Unpaid salaries for 2+ months, unexplained deductions from full-and-final (FnF) settlements, refusal to release relieving/experience letters, and informal employment disputes.

*Note: For out-of-scope matters (such as criminal offenses or divorce proceedings), LawPilot AI transparently explains its scope boundaries and provides safe guidance on consulting a qualified advocate.*

---

## 🏛️ System Architecture

```
User (Browser / Mobile)
   │  Speech Input (Web Speech API) / Text / Attachment
   ▼
FastAPI Backend (app/main.py)
   ├─► Input Sanitizer & Prompt Guard (app/core/sanitizer.py)
   ├─► Emergency & Escalation Filter (app/core/escalation.py)
   ├─► Multi-Turn Fact & State Tracker (app/core/conversation.py)
   ├─► Statutory Knowledge RAG (app/core/knowledge_base.py)
   ├─► Modular AI Engine: Gemini 1.5 Pro/Flash + Deterministic Provider (app/core/llm_provider.py)
   └─► Legal Document Generator (ReportLab PDF + python-docx) (app/core/document_generator.py)
```

### Architectural Highlights
- **FastAPI Core:** Synchronous route handlers ensure predictable threadpool execution, zero socket deadlocks in sandboxed environments, and instant response times (< 15ms in deterministic mode).
- **Zero-Key Deterministic Mode:** Works immediately out of the box with built-in statutory reasoning without needing paid API keys. Connect a Google Gemini API key via `.env` to unlock live LLM reasoning.
- **Dual Interface:** Streamlit interface (`streamlit_app.py`) provided alongside the primary FastAPI web app for instant one-click cloud deployment.

---

## 🧪 Comprehensive Evaluation & Test Harness

LawPilot AI was verified through an automated **46-scenario evaluation suite** executed across dual runs, alongside 29 unit tests and 20 UI checks.

### Summary of Results
| Test Category | Suite Size | Initial Run | Improved Run | Status |
|---------------|------------|-------------|--------------|--------|
| **Tenant Disputes (T01–T05)** | 5 | 5 / 5 | 5 / 5 | ✅ Passed |
| **Consumer Protection (C01–C04)** | 4 | 4 / 4 | 4 / 4 | ✅ Passed |
| **Employment Claims (E01–E04)** | 4 | 4 / 4 | 4 / 4 | ✅ Passed |
| **Edge & Safety Escalations (N01–N10)** | 10 | 9 / 10 (N08 failed) | 10 / 10 | ✅ Passed |
| **Multilingual Hinglish/Hindi (A01–A05, L01–L05, B01–B04)** | 14 | 14 / 14 | 14 / 14 | ✅ Passed |
| **Document Generation (D01–D05)** | 5 | 5 / 5 | 5 / 5 | ✅ Passed |
| **State Memory & Fact Tracking (R01–R04)** | 4 | 4 / 4 | 4 / 4 | ✅ Passed |
| **Total Benchmark Score** | **46** | **94.67% (45/46)** | **95.87% (46/46)** | **100% Pass** |
| **Unit Tests (`pytest`)** | 29 | 29 / 29 | 29 / 29 | ✅ Passed (2.30s) |
| **UI Interactive Verification** | 20 | 20 / 20 | 20 / 20 | ✅ Passed |

Unedited raw outputs for all 46 test cases are preserved in:
- `raw_outputs/initial_run/` (Records the initial N08 date contradiction failure)
- `raw_outputs/improved_run/` (Records the verified 100% resolution)

---

## 🚀 Quickstart & Local Execution

### 1. Clone the Repository
```bash
git clone https://github.com/madhav9127/LawPilot-AI.git
cd LawPilot-AI
```

### 2. Create and Activate Virtual Environment
```bash
# On Linux / macOS:
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys (Optional)
```bash
cp .env.example .env
```
*By default, the application runs in high-precision **Deterministic Grounded Mode** without an API key.*  
To enable Google Gemini live generation, set `GEMINI_API_KEY=your_key` in `.env`.

### 5. Launch the Application

#### Option A: Run the Primary FastAPI Single-Page App (Recommended)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open **`http://localhost:8000`** in your browser.

#### Option B: Run the Streamlit Interface
```bash
streamlit run streamlit_app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🧪 Running Automated Tests & Evaluation

### Run Unit Tests (pytest)
```bash
pytest -v
```
*Expected: 29 passed in ~2.3 seconds.*

### Run the 46-Scenario Benchmark
```bash
python test_runner.py
```
*Runs all 46 scenarios, evaluates rubric compliance, and outputs results into `raw_outputs/improved_run/`.*

---

## 📚 Documentation Index

All technical and architectural documentation is organized in the [`docs/`](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/docs) directory:

- [docs/ARCHITECTURE.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/docs/ARCHITECTURE.md) — System design, data flow, component decoupling, and Mermaid diagrams.
- [docs/AI_WORKFLOW.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/docs/AI_WORKFLOW.md) — System prompts, statutory RAG grounding, multi-turn memory, and model swapping.
- [docs/TEST_CASES.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/docs/TEST_CASES.md) — Specifications for all 46 benchmark scenarios + 20 UI tests.
- [docs/TEST_RESULTS.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/docs/TEST_RESULTS.md) — Comprehensive results comparing initial and improved test runs.
- [docs/EVALUATION_REPORT.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/docs/EVALUATION_REPORT.md) — Weighted scoring rubric (95.87%), safety audit, and domain breakdown.
- [docs/FAILURE_ANALYSIS.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/docs/FAILURE_ANALYSIS.md) — Root-cause analysis of the N08 date contradiction failure and architectural fixes.
- [docs/AI_TOOL_DISCLOSURE.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/docs/AI_TOOL_DISCLOSURE.md) — Transparent disclosure of AI tools used, roles, and real engineering mistakes caught during testing.
- [solution_doc.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/solution_doc.md) — Concise 2-page PDF-ready executive summary for Kuku assignment submission.

---

## 🛡️ Legal & Ethical Safety Disclaimers

1. **Information, Not Legal Representation:** LawPilot AI provides structured legal information and automated draft generation under Indian law. It does not establish an advocate-client relationship.
2. **Mandatory Advocate Review:** Every generated PDF and DOCX document includes an unalterable legal disclaimer indicating that formal legal notices must be reviewed by a licensed Bar Council advocate before delivery.
3. **No Outcome Guarantees:** In accordance with Bar Council of India professional standards, LawPilot AI strictly refuses requests to promise or guarantee judicial outcomes.
4. **Emergency Routing:** Immediate diversion to police (112) or medical services (108/112) when life, physical safety, or criminal intimidation is detected.
