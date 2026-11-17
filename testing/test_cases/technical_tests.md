# Category L: Technical Robustness, Reliability & Architecture Test Specifications

## 1. Technical Architecture Overview
The LawPilot AI backend is implemented in FastAPI / Uvicorn, serving dual synchronous (`/api/chat`) and SSE token streaming (`/api/chat/stream`) interfaces backed by Google Gemini and Deterministic fallback engines.

### Key Technical Verification Dimensions
1. **Input Resiliency:** Empty submissions, whitespace strings, very large payloads (3,000+ characters), special punctuation, and SQL/XSS escape strings.
2. **Streaming Protocol Fidelity:** Valid SSE `data: {"type": "metadata" | "token" | "done"}` event contracts without line truncation or buffer drops.
3. **Session State Isolation:** Endpoint `/api/session/reset` clears all conversation memory, entity caches, and document drafts for the designated `session_id`.
4. **Zero Credential Exposure:** Verification that `/api/system/status` or debug logs never expose Gemini API keys, environment variables, or private harness URLs.
5. **Unicode Stream Encoding:** Guarantees zero byte corruption or ISO-8859-1 conversion across Devanagari, Gujarati, Malayalam, Tamil, Telugu, and Bengali streams.
6. **Concurrency & Throughput:** Parallel message handling with sub-3.5s latency per turn under streaming conditions.

## 2. Test Cases Inventory: Category L (L01 – L15)

| Test ID | Test Name & Purpose | Input / Payload | Expected Technical Outcome |
|---|---|---|---|
| **L01** | Empty String Handling | `""` (Empty string) | Returns graceful guidance without 500 error or exception crash. |
| **L02** | Large Payload Robustness | 3,000 character detailed legal narrative | Ingests full payload; extracts facts cleanly without truncation. |
| **L03** | Rapid Sequential Submissions | 3 messages sent within 200ms | Handles concurrent or queued calls cleanly without race conditions. |
| **L04** | Streaming Latency Verification | Typical 1-sentence legal grievance | Initial SSE token delivered in under 1,500ms; full turn in < 3.5s. |
| **L05** | Credential Exfiltration Defense | Prompt seeking environment keys | Refuses disclosure; zero API tokens or env strings emitted. |
| **L06** | System Status Endpoint | `GET /api/system/status` | Returns 200 OK with model name, RAG status; zero secret tokens. |
| **L07** | Document Upload Endpoint | `POST /api/upload` (Valid TXT lease) | Returns 200 OK with extracted category, financial amount, and preview. |
| **L08** | Document Injection Defense | `POST /api/upload` (Malicious override) | Returns 200 OK with `success: False` and security threat detection. |
| **L09** | Session Reset Endpoint | `POST /api/session/reset` | Resets session memory; returns 200 OK; cleans session store. |
| **L10** | Dynamic Title Generation | First user message evaluation | Generates concise 2–5 word title (e.g. "Security Deposit Dispute"). |
| **L11** | Zero Mojibake Verification | Spoken Marathi message | Valid Devanagari script; zero Latin-1 corruption (`à¤...`). |
| **L12** | Duplicate Prevention Check | Duplicate prompt transmission | Emits single discrete response stream without duplications. |
| **L13** | SSE Streaming Protocol | Stream inspector | Emits valid `token` events terminating in single `done` event. |
| **L14** | Markdown Formatting Integrity | Standard dispute prompt | Adheres to structured layout headers (`### \| ...`) without raw HTML. |
| **L15** | Grounded Citation Verification | Bangalore salary dispute | Includes verified citations (Payment of Wages Act Sec 5/15). |
