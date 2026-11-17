# LawPilot AI — System Architecture Specification

This document details the software architecture, component relationships, lifecycle workflows, and anti-hallucination guardrails of **LawPilot AI**.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    Client["Client Layer (Desktop & Mobile Web)
    • Modern Vanilla JS SPA
    • Web Speech API (English & Hindi)
    • Streamlit Cloud Frontend"]

    Gateway["API Gateway & Routing (FastAPI)
    • CORS & Request Validation
    • File Size & Extension Verification
    • Session Context Management"]

    subgraph SecurityCore["Security & Sanitization"]
        Sanitizer["Sanitizer Engine
        • Prompt Injection Detection
        • XSS Stripping
        • Adversarial Guarantee & Fabrication Guard"]
    end

    subgraph CoreEngine["Core Intelligence Engine"]
        CaseBuilder["Case Builder
        • Entity & Financial Extraction
        • Timeline & Conflict Detection
        • Missing Info Identifier"]

        KnowledgeBase["Grounded Legal Knowledge Base
        • Verified Indian Statutory Registry
        • Anti-Hallucination Citation Lookup
        • Central vs State Rent/Shops Acts"]

        Escalation["Escalation Detector
        • Court Summons & Deadlines
        • Physical Threats & Dispossession
        • Emergency Helplines (112, 15100)"]
    end

    subgraph LLMLayer["Modular AI Provider Layer"]
        ProviderFactory["Provider Factory"]
        Gemini["Google Gemini Provider"]
        DemoProvider["Deterministic Grounded Engine"]
    end

    subgraph OutputGenerators["Legal Output Services"]
        AnalysisRenderer["8-Point Legal Position Analysis"]
        EvidenceMgr["Dynamic Evidence Checklist"]
        DocGen["Legal Document Generator
        • ReportLab PDF Engine
        • python-docx Word Engine"]
    end

    Client --> Gateway
    Gateway --> SecurityCore
    SecurityCore --> CoreEngine
    CoreEngine --> LLMLayer
    LLMLayer --> OutputGenerators
    OutputGenerators --> Gateway
    Gateway --> Client
```

---

## 2. Component Responsibilities

| Component | Module Path | Primary Responsibility |
|---|---|---|
| **API Server** | `app/main.py` | Exposes REST endpoints (`/api/chat`, `/api/case`, `/api/document`, `/api/upload`), serves single-page app and handles file streaming. |
| **Configuration** | `app/config.py` | Manages environment secrets, active provider discovery, and system parameters without leaking keys. |
| **Data Schemas** | `app/models/schemas.py` | Strongly typed Pydantic models for chat requests, case entities, evidence items, and legal notices. |
| **Sanitizer** | `app/core/sanitizer.py` | Neutralizes prompt injection, system overrides, victory guarantee requests, and section invention attacks. |
| **Knowledge Base** | `app/core/knowledge_base.py` | Grounded registry of verified Indian acts (India Code), URLs, commencement dates, and citation verifier. |
| **Case Builder** | `app/core/case_builder.py` | Natural language fact extraction (parties, amounts, agreements, dates, conflict warnings). |
| **Escalation Detector**| `app/core/escalation.py` | Detects emergency situations (arrest, summons, physical force, deadlines) and attaches helpline guidance. |
| **Document Generator** | `app/core/document_generator.py` | Generates legally structured notices; exports production-grade PDF (ReportLab) and DOCX (python-docx). |
| **Document Parser** | `app/core/document_parser.py` | Extracts text from uploaded PDF/DOCX/TXT and analyzes clauses with injection protection. |
| **LLM Provider** | `app/core/llm_provider.py` | Modular abstraction for Gemini API and deterministic grounded demo engine. |
| **Frontend UI** | `app/static/`, `app/templates/` | Responsive SaaS design system with tab switching, voice assistant, and live case editing. |

---

## 3. AI Request Lifecycle & Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Browser Frontend
    participant API as FastAPI /api/chat
    participant San as Sanitizer Engine
    participant Esc as Escalation Detector
    participant CB as Case Builder
    participant KB as Legal Knowledge Base
    participant LLM as Grounded LLM Provider

    User->>UI: Types: "Landlord deposit return nahi kar raha ₹25000"
    UI->>API: POST /api/chat {message, language: 'hinglish', state: 'Delhi'}
    API->>San: inspect_for_threats(message)
    San-->>API: Status: Clean (No injection)
    API->>Esc: analyze(message)
    Esc-->>API: Escalation: None (Standard civil dispute)
    API->>CB: extract_case(message, state)
    CB-->>API: CaseData {category: 'tenant', amount: 25000, role: 'Tenant'}
    API->>KB: retrieve_grounded_laws(message, 'tenant', 'Delhi')
    KB-->>API: Citations [TPA Sec 108, Model Tenancy Act Sec 11]
    API->>LLM: generate_response(CaseData, Citations, Hinglish)
    LLM-->>API: 8-Point Legal Position Analysis + Grounded Markdown
    API-->>UI: ChatMessage {content, citations, follow_up_questions}
    UI-->>User: Displays response, citation badges & next step recommendations
```

---

## 4. Legal Retrieval & Anti-Hallucination Workflow

```mermaid
flowchart LR
    Query["User Statement & Legal Query"] --> Extractor["Entity & Category Extractor"]
    Extractor --> Matcher["Statutory Keyword & State Matcher"]
    
    subgraph Registry["Verified Indian Statutory Registry"]
        TPA["Transfer of Property Act, 1882
        (Sec 106, 108)"]
        CPA["Consumer Protection Act, 2019
        (Sec 2(7), 2(47), 35)"]
        PWA["Payment of Wages Act, 1936
        (Sec 5, 7, 15)"]
        StateActs["State Rent Control & Shops Acts
        (Maharashtra, Delhi, Karnataka)"]
    end
    
    Matcher --> Registry
    Registry --> Verifier{"Citation Verified in Registry?"}
    Verifier -- Yes --> Injector["Inject Verified Metadata & URL into Context"]
    Verifier -- No / Fake Claim --> Refuter["Refute Fake Section & Disclaim Invention"]
    
    Injector --> PromptAssembler["Assemble Grounded Prompt"]
    Refuter --> SafeGuidance["Return Safe General Advice"]
```

---

## 5. Case-Building & Document Generation Workflow

```mermaid
flowchart TD
    RawInput["User Statement / Uploaded PDF"] --> Parser["Document Parser & Sanitizer"]
    Parser --> Facts["Extracted Facts (Amounts, Dates, Parties)"]
    Facts --> ConflictCheck{"Chronological Contradiction?"}
    ConflictCheck -- Yes --> Flag["Flag Timeline Inconsistency to User"]
    ConflictCheck -- No --> Dashboard["Sync with Case Dashboard"]

    Dashboard --> UserReview["User Edits or Confirms Facts in UI"]
    UserReview --> DocSelector["Select Template (Notice / Complaint / Demand)"]
    DocSelector --> Templater["Document Generator Engine"]
    
    Templater --> StampDisclaimer["Stamp Mandatory Draft Legal Disclaimer"]
    StampDisclaimer --> PDF["Generate PDF (ReportLab)"]
    StampDisclaimer --> DOCX["Generate DOCX (python-docx)"]
    PDF --> Download["Client Download"]
    DOCX --> Download
```

---

## 6. Error Handling & Resilience Strategy

1. **API Key Fallback:** If `GEMINI_API_KEY` is not provided, invalid, or reaches quota limits, the system does not crash; it smoothly switches to the **Deterministic Grounded Engine**, outputting verified statutory citations and marking responses as `[Demo Mode — Grounded Statutory Rules]`.
2. **Untrusted Upload Sanitization:** Uploaded documents are parsed in memory, checked against prompt-injection regex patterns, and stripped of dangerous scripting before fact extraction.
3. **Statutory Out-of-Bounds:** Queries outside supported civil domains (e.g., criminal IPC/BNS, divorce, patents) trigger bounded guidance explaining statutory scope limitations and directing users to NALSA (15100).
