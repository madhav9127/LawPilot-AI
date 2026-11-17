# LawPilot AI — Executive Solution Document
**Kuku AI Generalist Assignment — Problem 2: Build an AI Lawyer**  
**Author:** Madhav | **Repository:** [github.com/madhav9127/LawPilot-AI](https://github.com/madhav9127/LawPilot-AI)  
**Date:** November 2026 | **Target Format:** 2-Page Submission Document

---

## 1. Problem Chosen & Why
In India, over **50 million cases** are pending across courts, and millions more citizens never approach the legal system due to high consultation fees, fear of complex legal jargon, and lack of basic legal literacy. Ordinary individuals face everyday exploitation—landlords withholding security deposits without explanation, e-commerce platforms refusing legitimate refunds, and employers withholding full-and-final settlements or relieving letters.

**LawPilot AI** was built to solve this access-to-justice gap. It is a focused, multilingual conversational legal assistant that allows ordinary citizens to explain their situation in plain English, Hindi, or Hinglish. It clarifies their statutory rights under Indian law, organizes messy facts into actionable legal summaries, generates formal notice drafts, and transparently guides them on when to escalate to police or consult a qualified advocate.

---

## 2. Target Users & Everyday Pain Points
- **Urban Tenants & Students:** Facing arbitrary security deposit deductions (e.g. ₹15,000 painting charges after 11 months), sudden illegal eviction threats without court orders, or unwritten/oral lease disputes.
- **Retail & E-commerce Consumers:** Battling unresponsive customer support for defective electronics, delayed refunds beyond statutory norms, or fake products delivered by online sellers.
- **Salaried Employees & Gig Workers:** Dealing with unannounced salary delays, missing Full & Final (FnF) settlements, unexplained salary deductions, or withheld experience/relieving certificates.

---

## 3. Assumptions & MVP Scope
1. **Three Core Everyday Domains:** Focus is strictly concentrated on (A) Tenant & Landlord Disputes (*Transfer of Property Act 1882*, *Model Tenancy Act 2021*), (B) Consumer Protection (*Consumer Protection Act 2019*), and (C) Employment & Wage Disputes (*Payment of Wages Act 1936*, *Indian Contract Act 1872*). Out-of-scope matters (criminal law, family disputes) receive safe referral guidance.
2. **Advisory, Not Representation:** LawPilot AI provides legal information, structured analysis, and document drafting—never legal representation or attorney-client privilege.
3. **Safety & Zero-Harm Boundaries:** Medical emergencies immediately trigger 108/112 routing; active physical violence or forceful lockout triggers Police 112 and NALSA 15100 legal aid; fraudulent requests (e.g. forging fake payslips) and requests to guarantee a 100% court victory are strictly refused.

---

## 4. System Architecture
LawPilot AI avoids over-engineered distributed microservices in favor of a clean, highly reliable single-page architecture:

```
[User Browser (Desktop / Mobile)]
   │  HTML5 + Modern CSS + Web Speech API Mic + File Upload
   ▼
[FastAPI Backend Core (Python 3.14 Synchronous / Low-Latency)]
   ├─► Input Sanitizer & Prompt Guard (app/core/sanitizer.py)
   ├─► Emergency & Escalation Filter (app/core/escalation.py)
   ├─► Multi-Turn Fact & State Tracker (app/core/conversation.py)
   ├─► Statutory Knowledge RAG (app/core/knowledge_base.py)
   ├─► AI Inference Engine: Google Gemini 1.5 Pro / Flash + Deterministic Engine (app/core/llm_provider.py)
   └─► Notice & Document Generator (PDF via ReportLab + DOCX) (app/core/document_generator.py)
```

- **Frontend:** Single-page conversational UI (ChatGPT-style). Header with live grounding status pill, welcoming hero with 4 clickable scenario prompts (disappears upon message start), streaming bubble history, audio transcription mic button, document attachment button, and inline action pills ("Draft Legal Notice", "Summarize Case", "Copy Response").
- **Backend:** FastAPI with synchronous request handlers for deterministic test compatibility and threadpool performance; stateless REST endpoints (`/api/chat`, `/api/document/generate`, `/api/health`).

---

## 5. AI vs. Rules Breakdown: Architectural Balance
A common pitfall in legal-tech is allowing an unconstrained LLM to generate statutory provisions and ethical decisions. LawPilot AI implements a strict separation of concerns:

| Component | Mechanism | Rationale |
|-----------|-----------|-----------|
| **Safety Escalation** | **Deterministic Rules & Regex** | Zero false-negative tolerance for emergency dispatch (108/112), physical lockouts, and fraud refusal. |
| **Prompt Injection Defense** | **Rule-based Sanitizer** | Prevents system prompt overrides, prompt leaking, and adversarial jailbreaks before reaching LLM. |
| **Statutory Provision Retrieval** | **Curated Knowledge Base RAG** | Guaranteed citation accuracy to verified India Code provisions and verified limitation periods. |
| **Multi-Turn Fact Tracking** | **Deterministic State Machine** | Distinguishes explicit facts, inferred context, and missing details; prevents hallucinated tenant/deposit amounts. |
| **Natural Language Explanations** | **LLM (Gemini 1.5 / Deterministic Engine)** | Translates rigid statutory clauses into warm, empathetic, simple Hindi/Hinglish/English prose. |
| **Document Assembly** | **Template Engine + ReportLab** | Formats legal notices with exact standard Indian legal headers, party details, facts, and signature blocks. |

---

## 6. Anti-Hallucination & Legal Grounding Mechanism
1. **Statutory Anchoring:** Every legal assertion links back to verified statutes (e.g., Section 108(m) of TPA for reasonable wear & tear, Section 35 of CPA 2019 for District Commission filing, Section 5 of Payment of Wages Act for salary timelines).
2. **Fake Law Refusal:** Adversarial inputs quoting non-existent statutes (e.g. *"Section 999 of Indian Rental Code 2024"*) are intercepted; the assistant explicitly clarifies that no such section exists and cites the actual applicable law (*Transfer of Property Act 1882*).
3. **No Victory Guarantees:** When prompted with *"Guarantee that I will win this case 100%"*, the assistant explicitly refuses, explaining that legal outcomes depend on court appreciation of evidence, judicial discretion, and opposing arguments.
4. **Official India Code Citations:** AI responses provide clean references and direct links to [India Code](https://www.indiacode.nic.in) for user verification.

---

## 7. Test Results & Evaluation Metrics
LawPilot AI was subjected to an automated **46-scenario test harness** covering Tenant (T01–T05), Consumer (C01–C04), Employment (E01–E04), Edge & Safety (N01–N10), Multilingual Hindi/Hinglish (A01–A05, L01–L05, B01–B04), Document Generation (D01–D05), and Fact Tracking (R01–R04), plus 29 unit tests and 20 UI tests.

| Evaluation Metric | Initial Run (`initial_run`) | Improved Run (`improved_run`) | Target Threshold |
|-------------------|-----------------------------|-------------------------------|------------------|
| **Total Test Cases** | 46 / 46 executed | 46 / 46 executed | 46 |
| **Passing Tests** | 45 / 46 (97.8%) | **46 / 46 (100.0%)** | 100% |
| **Weighted Rubric Score** | 94.67% | **95.87%** | ≥ 90% |
| **Statutory Grounding Accuracy** | 100.0% | **100.0%** | 100% |
| **Safety & Escalation Accuracy** | 90.0% (N08 failed) | **100.0% (All safe)** | 100% |
| **Pytest Unit Test Suite** | 29 / 29 passed | **29 / 29 passed (2.30s)** | 100% |
| **UI Interactive Verification** | 20 / 20 passed | **20 / 20 passed** | 100% |

Raw unedited evaluation outputs are permanently recorded in `raw_outputs/initial_run/` and `raw_outputs/improved_run/`.

---

## 8. Failure Analysis & Key Fixes
1. **Contradictory Date Fallthrough (Test N08):** In the initial run, the user claimed conflicting move-out dates (1 Oct vs 15 Oct). A rigid substring match failed due to conversational filler words (*"vacated the flat on 1 October"*), allowing document drafting to proceed.  
   *Fix:* Decoupled date entity extraction and verb co-occurrence in `llm_provider.py`. Result improved from 40% to 100%.
2. **Regex Spacing Boundaries:** In `sanitizer.py`, patterns like `(promise|guarantee)\s+(to\s+)?win` failed on `"guarantee a win"`.  
   *Fix:* Added non-capturing groups `(?:a\s+)?` and `(?:court\s+)?`.
3. **Async Socket Deadlocks in Python 3.14 (Windows Sandbox):** Starlette's async `TestClient` blocked when initializing loop sockets.  
   *Fix:* Converted FastAPI endpoint handlers to standard synchronous `def` functions, enabling instantaneous in-memory execution.

---

## 9. Scalability, Future Scope & Lawyer Referral
- **Lawyer Connect Integration:** Users can export structured case packets (chronological facts, collected evidence, generated notice drafts) directly to vetted NALSA / Bar Council advocates for one-click handoff.
- **State Rent Authority APIs:** Integration with state portal APIs (e.g. Karnataka RERA, Delhi Rental Authority) for automated e-filing.
- **Offline / Edge Deployment:** Lightweight quantised SLMs (e.g. Gemma 2B) running locally on mobile devices for privacy-first rural legal clinics without reliable broadband access.
