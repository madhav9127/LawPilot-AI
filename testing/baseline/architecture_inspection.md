# LawPilot AI — Phase 1 Baseline Architecture Inspection

Detailed inspection of the LawPilot AI codebase prior to Phase 2 and Phase 4 enhancements.

---

## 1. LLM Provider and Model Configuration
- **Active Provider:** Google Gemini API configured in `app/config.py` (`active_provider = "gemini"`).
- **Underlying Models:** Cascading cascade of `gemini-flash-lite-latest` (primary, fast SSE streaming, high rate-limit tolerance) and `gemini-3.8-flash` (complex reasoning).
- **Fallback Provider:** `DeterministicDemoProvider` in `app/core/llm_provider.py` (structured offline fallback for rate-limiting or network outage scenarios).
- **Secondary Providers:** Architecture supports pluggable `OpenAIProvider` (`gpt-4o-mini`) and `AnthropicProvider` (`claude-3-5-sonnet`).

## 2. Real LLM Execution Verification
- **Network Pipeline:** HTTP POST requests dispatched directly to `https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent?key={api_key}&alt=sse`.
- **Streaming Implementation:** Genuine real-time token streaming using Server-Sent Events (`data: {"type": "token", "content": ...}\n\n`).
- **Audit Verification:** Every request is assigned a unique `req_id` (e.g. `req_ec703b62`) logged in the runtime audit trail.

## 3. RAG Architecture and Grounding
- **Module:** `app/core/knowledge_base.py` (`LegalKnowledgeBase`).
- **Mechanism:** Pre-retrieval statutory keyword & vector matching across verified Indian acts.
- **Context Injection:** Structured prompt injection formats retrieved provisions into the model prompt:
  ```text
  Ground your statutory analysis in these verified provisions:
  - The Payment of Wages Act, 1936 Section 5: Time of payment of wages...
  - The Transfer of Property Act, 1882 Section 108: Rights and liabilities of lessor and lessee...
  ```
- **Metadata Emission:** Citations are emitted in initial SSE metadata events (`{"type": "metadata", "citations": [...]}`) and rendered as official source pills in the UI.

## 4. Official Connected Legal Sources
1. **Tenancy & Housing:**
   - The Transfer of Property Act, 1882 (Section 106, 108)
   - The Model Tenancy Act, 2021 (Section 4, 11, 21, 23)
   - State Rent Control Acts (Maharashtra Rent Control Act 1999, Delhi Rent Control Act 1958, Karnataka Rent Act 1999)
2. **Consumer Protection:**
   - The Consumer Protection Act, 2019 (Section 2(7), 2(47), 35, 38, Chapter VI Product Liability)
   - Consumer Protection (E-Commerce) Rules, 2020 (Rule 4, 5, 6)
3. **Employment & Wages:**
   - The Payment of Wages Act, 1936 (Section 3, 5, 7, 15)
   - The Industrial Disputes Act, 1947 (Section 25F, 33C)
   - The Indian Contract Act, 1872 (Section 73)
   - State Shops and Commercial Establishments Acts (Karnataka, Maharashtra, Delhi, UP)

## 5. Conversation State and Memory Management
- **Frontend Storage:** Stored in browser `localStorage` under `lawpilot_conversations` as JSON with unique UUID `session_id`.
- **Backend Transmission:** Transmitted in `ChatRequest.conversation_history` as an array of `{role: "user" | "assistant", content: "..."}`.
- **Prompt Windowing:** In `app/core/llm_provider.py`, the most recent 6 conversational turns are injected into the LLM context window to preserve continuity without context overflow.

## 6. Multilingual Detection Architecture
- **Module:** `app/core/llm_provider.py` (`detect_message_language`).
- **Unicode Analysis:** Direct character code point scanning across native Indic Unicode blocks:
  - Devanagari (`0x0900-0x097F`) for Hindi and Marathi
  - Gujarati (`0x0A80-0x0AFF`)
  - Malayalam (`0x0D00-0x0D7F`)
  - Tamil (`0x0B80-0x0BFF`)
  - Telugu (`0x0C00-0x0C7F`)
  - Bengali (`0x0980-0x09FF`)
  - Gurmukhi (`0x0A00-0x0A7F`)
  - Kannada (`0x0C80-0x0CFF`)
- **Script Discrimination:** Devanagari letter ळ (`U+0933`) and Marathi morphological markers cleanly separate Marathi from Hindi.
- **Hinglish Classification:** Lexical frequency matching across conversational Romanized Hindi tokens (`aap`, `karein`, `salary`, `bhejein`, `paise`).

## 7. Voice Transcription Pipeline
- **API:** Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`).
- **Interface:** Modern ChatGPT-style pill transforming into a live audio visualizer.
- **Visual Feedback:** 20 responsive waveform bars driven by Web Audio API `AnalyserNode` connected to microphone stream.
- **Transparency:** Transcribed speech text appears directly in the textarea, allowing user verification and manual edits before submission.

## 8. Document Generation Pipeline
- **Module:** `app/core/document_generator.py` and template directives in `llm_provider.py`.
- **Formats:** Plain text, Markdown notices, and downloadable Microsoft Word `.docx` documents (`python-docx`).
- **Factual Integrity:** Retains exact user figures (e.g. ₹25,000) and marks missing information with editable brackets `[...]`.

## 9. Legal Citation Verification
- **Verification Guardrail:** Static pre-verification ensures that citations outputted by the model correspond to genuine sections within connected statutes.
- **Anti-Hallucination Directives:** Prompts explicitly prohibit inventing fictional section numbers, non-existent Supreme Court judgments, or imaginary statutory guarantees.

## 10. Baseline Domain Scope Assessment (Weaknesses Identified)
- **Strengths:** Strong handling of tenancy, consumer, and employment disputes; effective urgent safety escalation for threats and criminal emergencies.
- **Identified Weaknesses:**
  1. *Out-of-Scope Non-Legal Requests:* Baseline answered some trivia ("Capital of France", "Python code") or jokes instead of consistently redirecting with the specialized legal assistance disclaimer.
  2. *Mixed Queries:* When presented with a prompt combining legal and entertainment questions (e.g. "My employer has not paid me. Also, suggest a movie"), baseline tended to answer the legal issue without explicitly declining the movie suggestion.
  3. *Red-Team Edge Cases:* Prompt injection attempts demanding complete system prompt disclosure (F03) or developer instructions required dedicated input sanitization filters.
