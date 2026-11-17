# LawPilot AI — Complete System Architecture & Technical Specifications

## 1. High-Level Architecture
LawPilot AI is designed with an asymmetric decoupling between user-facing client interfaces and an intelligent Python FastAPI core:

```
┌─────────────────────────────────────────────────────────────┐
│                 Client Layer (Browser / Web)                │
│  - Vanilla JavaScript & SSE Token Consumer                  │
│  - Unified State Controller & ChatGPT-Style Typing Dots     │
│  - Settings Modal & Multi-turn Conversational Memory UI     │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / SSE POST (/api/chat/stream)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI / Uvicorn Core                  │
│  - REST Endpoints (/api/chat, /api/upload, /api/session)    │
│  - Server-Sent Events (SSE) Streaming Pipeline              │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
       ▼                       ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  Tier 1 & 2  │       │    Tier 3    │       │    Tier 4    │
│  Sanitizer   │       │    Domain    │       │     RAG      │
│      &       │──────►│  Guardrail   │──────►│  Knowledge   │
│  Escalation  │       │  Controller  │       │     Base     │
└──────────────┘       └──────────────┘       └──────┬───────┘
                                                     │
                                                     ▼
                                      ┌──────────────────────────────┐
                                      │   Google Gemini LLM Engine   │
                                      │  - gemini-flash-lite-latest  │
                                      │  - gemini-3.8-flash fallback │
                                      │  - Deterministic Demo Fallback│
                                      └──────────────────────────────┘
```

---

## 2. Core Modules Description

| Module Path | Core Purpose & Implementation |
|---|---|
| `app/main.py` | FastAPI application bootstrap, CORS middleware, SSE streaming router, upload endpoints, session reset, and system health status inspection. |
| `app/core/llm_provider.py` | Primary intelligence layer implementing `GeminiInteractionsProvider`, streaming token generator, multilingual prompt builder, fast-track routing, and `DeterministicDemoProvider` fallback. |
| `app/core/domain_guardrail.py` | Legal domain scope controller enforcing specialized Indian civil legal scope (tenancy, consumer, employment) and localized redirections. |
| `app/core/sanitizer.py` | Multi-pattern regex defense engine protecting against prompt injections, secret exfiltration, authority manipulation, and evidence fabrication. |
| `app/core/knowledge_base.py` | Grounded statutory repository indexing authentic sections of MTA 2021, CPA 2019, Payment of Wages Act 1936, and Legal Services Authorities Act. |
| `app/core/case_builder.py` | Entity extractor isolating parties, financial amounts (INR), property addresses, transaction dates, and conflict detection. |
| `app/core/conversation.py` | Persistent multi-turn session memory tracker maintaining chronological facts and resolving user fact corrections. |
| `app/core/title_generator.py` | Automatic conversation title generator extracting 2–5 word concise, domain-relevant titles across Indian languages. |
| `app/core/document_parser.py` | Multipart document parser inspecting user-uploaded agreements, invoices, and payslips with integrated injection quarantining. |
| `app/core/escalation.py` | High-priority safety scanner identifying physical threats, imminent eviction, domestic violence, and providing national emergency helplines. |

---

## 3. Streaming & Latency Profile
- **Protocol:** HTTP/1.1 chunked transfer encoding emitting standard `text/event-stream`.
- **First-Token Latency (TTFT):**
  - Fast-track / Scope Redirection: < 15ms.
  - Google Gemini API Streaming: 1,200ms – 1,800ms.
- **Throughput:** ~40 tokens/second over streaming SSE.
- **Encoding Integrity:** Guaranteed zero Latin-1 / UTF-8 byte conversion defects by explicit raw UTF-8 line decoding.
