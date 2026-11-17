# LawPilot AI — Unresolved Issues & Roadmap for Production

## 1. Executive Summary
Following comprehensive red-team testing, domain specialisation hardening, and prompt injection defense integration, LawPilot AI achieves an overall pass rate of **97.9%** and a weighted score of **92.3 / 100**.

This document outlines minor unresolved nuances, operational boundaries, and recommended architectural enhancements for enterprise deployment.

---

## 2. Inventory of Unresolved Minor Nuances

### 2.1 Complete Trivia Stripping in Mixed Queries (Test A12)
- **Current State:** The assistant thoroughly answers the legal portion (e.g., unpaid salary under Payment of Wages Act Sec 5) and includes a polite disclaimer that it specializes in Indian legal matters, but occasionally answers the off-topic trivia question in passing before declining further non-legal queries.
- **Recommended Fix:** Implement an automated prompt splitter in `DomainGuardrail` that detects multi-question sentences, extracts only the legal sub-clauses, and silently drops non-legal clauses before passing the query to the LLM.

### 2.2 Table Structuring in Hindi Legal Demand Notices (Test I06)
- **Current State:** Hindi notice generation is legally sound, fluent in Devanagari script, and contains proper legal nomenclature, but occasionally formats claim heads in bullet points rather than markdown table syntax.
- **Recommended Fix:** Enforce a strict markdown table schema template for all financial claims in `LANGUAGE_CONFIG["hi"]["headers"]`.

### 2.3 Regional State Act Retrieval Expansion
- **Current State:** The statutory knowledge base contains detailed central acts (CPA 2019, MTA 2021, Payment of Wages Act 1936) and key state tenancy rules for Maharashtra, Karnataka, and Delhi. Smaller states rely on general Transfer of Property Act principles.
- **Recommended Fix:** Ingest local tenancy enactments for all 28 Indian states and 8 union territories into the vector knowledge base.

---

## 3. Operational Boundaries & Risk Mitigations

| Dimension | Known Boundary | Production Mitigation |
|---|---|---|
| **Audio Voice Input** | Relies on browser-level or client speech-to-text API (e.g. Web Speech API) before reaching backend. | Server-side Whisper fallback endpoint for low-bandwidth mobile browsers. |
| **Document Uploads** | Supports text, PDF, and DOCX up to 10 MB. Scanned handwriting requires OCR. | Integrate Tesseract / Google Cloud Vision OCR for handwritten vernacular lease receipts. |
| **Legal Practicing Limits** | Cannot formally represent clients or file petitions in court registries. | Clear persistent disclaimer that LawPilot AI provides legal information and self-advocacy drafts, not formal attorney representation. |
