# LawPilot AI — Unresolved Issues & Roadmap for Production

## 1. Executive Summary
Following comprehensive red-team testing, domain specialisation hardening, and prompt injection defense integration, LawPilot AI achieves an overall pass rate of **100.0%** (144 / 144 tests passed) and a weighted score of **93.2 / 100**.

This document outlines minor operational boundaries and recommended architectural enhancements for enterprise deployment.

---

## 2. Production Roadmap & Architectural Enhancements

### 2.1 Server-Side OCR for Handwritten Physical Documents
- **Current State:** The document ingestion pipeline reliably handles text files, digital PDFs, and Word DOCX files.
- **Production Roadmap:** Integrate server-side OCR (e.g., Tesseract or Google Cloud Vision OCR) to automatically transcribe physical, handwritten, or degraded rent receipts and police acknowledgments.

### 2.2 Server-Side Whisper for Low-Bandwidth Clients
- **Current State:** Voice input uses browser-native Web Speech API with real-time audio visualization, delivering instant client-side transcription.
- **Production Roadmap:** Add an optional server-side OpenAI Whisper or Faster-Whisper audio transcription endpoint as a fallback for browsers with limited speech recognition support.

### 2.3 Regional State Tenancy Act Granular Ingestion
- **Current State:** The knowledge base covers central statutes (Transfer of Property Act 1882, Model Tenancy Act 2021) and state tenancy enactments for major states (Maharashtra, Karnataka, Delhi, Gujarat, Rajasthan).
- **Production Roadmap:** Expand the knowledge base to ingest local rent control acts for all 28 Indian States and 8 Union Territories.

---

## 3. Operational Boundaries & Risk Mitigations

| Dimension | Known Boundary | Production Mitigation |
|---|---|---|
| **Audio Voice Input** | Relies on browser-level Web Speech API before reaching backend. | Server-side Whisper fallback endpoint for older mobile browsers. |
| **Document Uploads** | Supports text, PDF, and DOCX up to 10 MB. Scanned handwriting requires OCR. | Integrate OCR pipeline for handwritten vernacular lease receipts. |
| **Legal Practicing Limits** | Cannot formally represent clients or file petitions in court registries. | Clear persistent disclaimer that LawPilot AI provides legal information and self-advocacy drafts, not formal attorney representation. |
