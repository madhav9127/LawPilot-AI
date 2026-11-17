# LawPilot AI ⚖️
### Navigate Legal Challenges. Know Your Rights. Take Action.

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io)
[![Test Suite](https://img.shields.io/badge/pytest-29%2F29%20passed-brightgreen.svg)]()
[![Evaluation Score](https://img.shields.io/badge/Evaluation%20Score-93.55%25-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

> **Product Vision:** LawPilot AI is an intelligent, multilingual legal assistant designed to make legal guidance accessible to ordinary people in India. Users explain their everyday legal challenges in plain **English, Hindi, or Hinglish** and receive grounded legal explanations, statutory rights, evidence checklists, and professionally drafted legal documents.

---

## 📌 Problem Statement

Every year, millions of citizens in India face everyday civil disputes:
1. **Tenant & Landlord Conflicts:** Unreturned security deposits, arbitrary deductions for routine painting wear-and-tear, lack of registered agreements, and verbal eviction threats via WhatsApp.
2. **Consumer Grievances:** Defective e-commerce electronics, refund failures between payment gateways and merchants, wrong deliveries, and deficient paid services.
3. **Employment Issues:** Unpaid salaries, unexplained deductions from full-and-final (FnF) settlements, refusal to issue relieving letters, and informal employment.

Most people do not know their basic rights under the **Transfer of Property Act, 1882**, the **Consumer Protection Act, 2019**, or the **Payment of Wages Act, 1936**. Retaining an advocate at the initial inquiry stage is often prohibitively expensive. Meanwhile, generic LLMs frequently hallucinate fake sections or make outcome guarantees.

**LawPilot AI bridges this gap with responsible, grounded AI engineering.**

---

## 🌟 Core Features

- **Multilingual Natural Language Understanding:** Explain problems conversationally in English, Hindi (हिंदी), or conversational Hinglish (e.g., *"Mera landlord ₹25,000 deposit wapas nahi de raha"*).
- **Statutory Legal Grounding & Anti-Hallucination:** Every legal explanation is directly retrieved from official government statutes published on [India Code](https://www.indiacode.nic.in/), Department of Consumer Affairs, and NALSA.
- **Structured Case Builder:** Automatically converts free-form conversations into structured legal facts: parties, roles, disputed amounts, agreements, timelines, and missing information.
- **Dynamic Evidence Checklist:** Itemizes necessary documents (bank statements, move-out photos, WhatsApp chats, salary slips) and explains their legal relevance under Section 65B of the Indian Evidence Act (BSA 2023).
- **Professional Legal Document Generator:** Generates legally structured demand letters, formal legal notices, and consumer complaint drafts with instant **PDF** and **Word (DOCX)** export.
- **Emergency Human Lawyer Escalation:** Detects high-stakes situations (court summons, impending limitation deadlines, criminal threats, illegal physical evictions) and immediately displays emergency helpline numbers (NALSA 15100, Police 112, NCH 1915).
- **Document Upload & Prompt Injection Protection:** Extracts facts, dates, and amounts from uploaded PDFs, DOCX, and receipts, while sanitizing against adversarial prompt injection attempts.
- **Zero-Key Deterministic Demo Mode:** Fully functional out-of-the-box without requiring paid API keys, while allowing seamless integration of Google Gemini, OpenAI, or Anthropic via environment variables.

---

## 🛠️ Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend API** | FastAPI (Python 3.11+) | Asynchronous performance, automatic OpenAPI documentation, clean REST endpoints. |
| **Frontend UI** | Modern Vanilla JS + Responsive CSS | Custom SaaS design (Navy `#0F172A`, Teal `#0D9488`), zero npm build dependencies, instant loading. |
| **Dual Interface** | Streamlit | 1-click deployment on Streamlit Community Cloud for interview presentations. |
| **PDF Generation** | ReportLab | Production-grade PDF rendering with legal formatting and disclaimers. |
| **DOCX Generation**| python-docx | Clean Word document generation for advocate collaboration. |
| **Testing** | pytest | Automated test suite verifying extraction, sanitization, retrieval, and endpoints. |
| **Deployment** | Docker / Render / Streamlit Cloud | Free-tier deployment ready with `render.yaml`, `Procfile`, and `Dockerfile`. |

---

## 🏛️ System Architecture

```
User Dialogue (EN / HI / Hinglish) ──► Input Sanitizer ──► Case Builder (Fact Extraction)
                                                                 │
      ┌──────────────────────────────────────────────────────────┴─────────────────────────┐
      ▼                                                                                    ▼
Anti-Hallucination Retrieval Engine                                         Escalation Detector
  ├─ The Transfer of Property Act, 1882 (Sec 106, 108)                        ├─ Imminent Court Deadlines
  ├─ Model Tenancy Act, 2021 & State Acts                                     ├─ Formal Court Summons
  ├─ Consumer Protection Act, 2019 (Sec 2(7), 2(47), 35)                      ├─ Threats of Violence / Dispossession
  ├─ Payment of Wages Act, 1936 & State Shops Acts                            └─ Emergency Helplines (NALSA 15100, 112)
  └─ Verified Repositories (India Code, NCH, NALSA)
      │
      ▼
Modular LLM Provider (Gemini / OpenAI / Grounded Demo Engine)
      │
      ├─► 8-Point Legal Position Analysis (Plain Language)
      ├─► Dynamic Evidence Checklist (Statutory Relevance)
      └─► Legal Document Generator (Editable Drafts ──► Export to PDF & DOCX)
```

---

## 🚀 Quickstart & Local Execution

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.14
- Git

### 2. Clone Repository
```bash
git clone https://github.com/madhav9127/LawPilot-AI.git
cd LawPilot-AI
```

### 3. Create and Activate Virtual Environment
```bash
# On Linux / macOS:
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables (Optional)
Copy the example environment configuration:
```bash
cp .env.example .env
```
*Note: If no API key is configured, LawPilot AI automatically runs in its intelligent **Deterministic Grounded Mode**.*

To enable live Google Gemini API:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

### 6. Run the Application

#### Option A: Run the Primary Full-Stack Web App (FastAPI)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to: **`http://localhost:8000`**

#### Option B: Run the Streamlit Interface
```bash
streamlit run streamlit_app.py
```
Open your browser and navigate to: **`http://localhost:8501`**

---

## 🧪 Testing and Verification

LawPilot AI includes a comprehensive automated test suite and an evaluation runner covering all 22 required scenarios:

### Run Automated Unit Tests (pytest)
```bash
pytest -v
```
*Result:* **29 passed in 1.04s** (100% pass rate).

### Run the 22-Scenario Evaluation Runner
```bash
python test_runner.py
```
This executes all 12 primary scenarios (T1–T4, C1–C4, E1–E4) and 10 adversarial/boundary tests (A1–A10), writing unedited JSON responses directly into `raw_outputs/` and computing the weighted evaluation score.

*Evaluation Result:* **93.55% / 100% Weighted Average Score** across 22 scenarios.

---

## 🛡️ Legal Safety & Ethical Guardrails

1. **Anti-Hallucination Principle:** The system strictly checks legal sections against its verified statutory registry. If a user asks to confirm a fabricated section (e.g., *"Section 999"*), the system refutes the section and provides the genuine law.
2. **Outcome Guarantees Prohibited:** Compliant with Bar Council of India ethics, the system refuses to guarantee court outcomes and explicitly reminds users that judicial findings depend on evidence and statutory discretion.
3. **Draft Legal Disclaimers:** Every generated document (PDF and DOCX) includes an indelible header stamping it as an informational draft requiring review by a qualified advocate.
4. **Emergency Escalation:** Situations involving criminal threats, court summons, or imminent deadlines trigger prominent emergency guidance and national legal aid contacts (NALSA 15100).
5. **Prompt Injection Defense:** File uploads and chat inputs are scanned and sanitized against instruction override attacks.

---

## 📂 Repository Structure

```
LawPilot-AI/
├── app/
│   ├── main.py                  # FastAPI server & route handlers
│   ├── config.py                # Configuration & secret handling
│   ├── models/schemas.py        # Pydantic schemas (Cases, Citations, Documents)
│   ├── core/
│   │   ├── llm_provider.py      # Modular LLM factory (Gemini, Demo Provider)
│   │   ├── knowledge_base.py    # Grounded Indian legal knowledge base
│   │   ├── case_builder.py      # Structured case extraction & state tracking
│   │   ├── evidence_checklist.py# Dynamic evidence checklist manager
│   │   ├── document_generator.py# Document drafting, PDF & DOCX export
│   │   ├── escalation.py        # Urgency & emergency escalation detector
│   │   ├── sanitizer.py         # Prompt injection & input validation
│   │   └── document_parser.py   # PDF and text extraction from user uploads
│   ├── static/                  # CSS styles, JS controllers, speech engine
│   └── templates/index.html     # Single Page Application
├── streamlit_app.py             # Streamlit dual interface for cloud deployment
├── tests/                       # Automated pytest suite (29 tests)
├── raw_outputs/                 # 22 unedited scenario test outputs
├── test_runner.py               # 22-scenario evaluation execution runner
├── README.md                    # Project documentation
├── SOLUTION_DOCUMENT.md         # 2-page executive solution document
├── ARCHITECTURE.md              # System architecture & Mermaid workflows
├── EVALUATION_REPORT.md         # Detailed evaluation report & rubric metrics
├── WALKTHROUGH_SCRIPT.md        # 3-minute interview demonstration script
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Production Docker container definition
├── render.yaml                  # 1-click Render blueprint
└── Procfile                     # Web process definition
```

---

## ☁️ Deployment Instructions

### Deploy to Streamlit Community Cloud (Free Tier)
1. Fork or push this repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and click **New App**.
3. Select the repository `madhav9127/LawPilot-AI`, branch `master`, and main file `streamlit_app.py`.
4. (Optional) Add your `GEMINI_API_KEY` under Advanced Settings -> Secrets.
5. Click **Deploy**.

### Deploy to Render (Free Tier)
1. In Render, select **New Web Service** and connect `madhav9127/LawPilot-AI`.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Deploy service.

---

## ⚖️ Legal Disclaimer

*LawPilot AI provides general legal information and assistance. It is not a law firm and does not substitute for advice from a qualified advocate licensed by the Bar Council of India. Legal outcomes depend on individual facts, applicable state laws, and judicial jurisdiction.*
