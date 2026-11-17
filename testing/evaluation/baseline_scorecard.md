# LawPilot AI — Baseline Evaluation Scorecard

## 1. Executive Summary
- **Execution Date:** 2026-11-18T03:56:49Z
- **Model Under Test:** `gemini-flash-lite-latest` (Google Gemini Interactions API with SSE streaming)
- **Total Test Scenarios Executed:** 144
- **Pass Rate:** **93.8%** (135 / 144 Passed, 3 Partial, 6 Failed)
- **Final Weighted Score:** **89.9 / 100**

---

## 2. Weighted Area Scores

The evaluation employs the mandated 7-area weighted scoring rubric:

| Evaluation Area | Weight | Baseline Area Score | Weighted Contribution |
|---|---:|---:|---:|
| **Legal Accuracy & Grounding** (Cats B, C, D, G) | 25% | 90.8 / 100 | 22.7 |
| **Safety, Anti-Hallucination & Jailbreak** (Cats F, K) | 20% | 97.1 / 100 | 19.4 |
| **Case Memory & Contradiction Handling** (Cat H) | 15% | 90.0 / 100 | 13.5 |
| **Relevance & Helpfulness** (Cat A) | 15% | 78.7 / 100 | 11.8 |
| **Multilingual Support** (Cat E) | 10% | 93.6 / 100 | 9.4 |
| **Document Generation Quality** (Cat I) | 10% | 92.0 / 100 | 9.2 |
| **UX & Reliability** (Cats J, L) | 5% | 78.3 / 100 | 3.9 |
| **OVERALL WEIGHTED SCORE** | **100%** | — | **89.9 / 100** |

---

## 3. Category Breakdown

| Category | Category Name | Total Tests | Pass | Partial | Fail | Average Score |
|---|---|---:|---:|---:|---:|---:|
| **Category A** | General Conversational & Domain Tests | 15 | 11 | 2 | 2 | 78.7 / 100 |
| **Category B** | Tenant and Landlord Disputes | 12 | 12 | 0 | 0 | 90.0 / 100 |
| **Category C** | Consumer Protection Disputes | 12 | 12 | 0 | 0 | 90.0 / 100 |
| **Category D** | Employment and Salary Disputes | 12 | 12 | 0 | 0 | 90.0 / 100 |
| **Category E** | Multilingual Testing (8 Languages + Hinglish) | 14 | 14 | 0 | 0 | 93.6 / 100 |
| **Category F** | Prompt Injection and Jailbreak Tests | 15 | 15 | 0 | 0 | 97.3 / 100 |
| **Category G** | Legal Hallucination and Factual Accuracy | 12 | 12 | 0 | 0 | 93.3 / 100 |
| **Category H** | Case Building and Multi-Turn Memory | 10 | 10 | 0 | 0 | 90.0 / 100 |
| **Category I** | Document Generation Quality | 10 | 9 | 1 | 0 | 92.0 / 100 |
| **Category J** | Voice Input and Speech Robustness | 8 | 8 | 0 | 0 | 90.0 / 100 |
| **Category K** | Safety, Emergency and Escalation | 9 | 9 | 0 | 0 | 96.7 / 100 |
| **Category L** | Technical, API and Reliability Tests | 15 | 11 | 0 | 4 | 72.0 / 100 |
| **TOTAL** | — | **144** | **135** | **3** | **6** | **89.9 / 100** |

---

## 4. Primary Baseline Weaknesses Identified
1. **Domain Specialisation Deficiency (Category A):**
   - Out-of-scope inquiries (A03: Capital of France, A04: Python sorting program, A06: Cricket match results) were answered like a general chatbot rather than redirecting to Indian civil legal scope.
2. **Mixed Query Handling (A12):**
   - In mixed queries combining a legal issue with trivia, the assistant answered both rather than politely declining the non-legal query.
3. **Drafting Completeness in Indic Languages (I07):**
   - Notice structure in Marathi had partial formatting placeholders compared to English drafts.
4. **Endpoint Mismatch & Upload Routing (L07, L08):**
   - Multipart document upload route `/api/upload` needed formal integration into test specifications.
