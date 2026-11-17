# LawPilot AI — Multilingual Support Architecture & Guide

This document describes the design, automatic language detection pipeline, prompt engineering strategy, and evaluation metrics for LawPilot AI's multilingual legal assistance capabilities.

---

## 1. Architectural Philosophy: Automatic Per-Turn Detection

Indian legal consumers naturally interact across multiple languages, frequently code-switching between regional scripts and conversational Roman-script phrasing (such as Hinglish).

### Why Manual Dropdowns Were Deprecated
Earlier iterations featured a manual language selector (`English`, `Hindi`, `Hinglish`) in the top navigation bar. In real-world testing, this proved counterproductive:
1. Users frequently switch languages mid-conversation (e.g., asking a question in English, requesting a notice draft in Hinglish, and asking for next steps in Gujarati).
2. Manual selectors forced the user to manually re-select options on every turn.
3. Unsupported languages in the dropdown forced inputs to inappropriately default to English.

**Solution:** LawPilot AI utilizes **Automatic Per-Turn Language Detection**. Every incoming message is analyzed in real time. The language of the user's latest prompt strictly dictates the language of the assistant's response.

---

## 2. Detection Algorithm & Unicode Script Classification

Detection is implemented in `detect_message_language(...)` in `app/core/llm_provider.py`. The algorithm executes a 3-tier analysis:

### Tier 1: Explicit User Language Requests
Regex patterns check if the user explicitly asked for a specific language in their prompt (e.g., `"in gujarati"`, `"in hindi"`, `"draft in malayalam"`, `"reply in hinglish"`). If detected, that explicit request takes precedence.

### Tier 2: Indic Script Unicode Frequency Analysis
For messages written in native Indic scripts, character code points are tallied across standard Unicode blocks:
- **Gujarati (`gu`):** `0x0A80` – `0x0AFF`
- **Devanagari / Hindi (`hi`):** `0x0900` – `0x097F`
- **Malayalam (`ml`):** `0x0D00` – `0x0D7F`
- **Tamil (`ta`):** `0x0B80` – `0x0BFF`
- **Telugu (`te`):** `0x0C00` – `0x0C7F`
- **Bengali (`bn`):** `0x0980` – `0x09FF`
- **Kannada (`kn`):** `0x0C80` – `0x0CFF`
- **Marathi (`mr`):** `0x0900` – `0x097F` (with Marathi phonetic filters)
- **Punjabi / Gurmukhi (`pa`):** `0x0A00` – `0x0A7F`
- **Odia (`or`):** `0x0B00` – `0x0B7F`

If characters from an Indic script block exceed a threshold (>= 2 characters), the dominant script is identified and the target language is assigned immediately.

### Tier 3: Latin Script Classification (English vs. Hinglish)
If no Indic script characters are detected and the text is in Latin script:
1. The message is checked against common Hinglish conversational markers (`aap`, `karein`, `karna`, `nahi`, `mera`, `meri`, `mujhe`, `bhejein`, `bataiye`, `paise`, `hoga`, etc.).
2. Common Hinglish phrases are checked (`ab mujhe`, `legal notice bhejna`, `salary nahi di`, `kya karu`, `kar sakta`).
3. If Hinglish markers or phrases are found, the message is classified as `hinglish`.
4. Otherwise, it defaults cleanly to standard `en` (English).

---

## 3. System Prompt Injection & Language Consistency

In `_build_prompt(...)`, the detected language configures a strict system instruction injected directly into the Gemini prompt:

```text
CRITICAL MANDATORY LANGUAGE REQUIREMENT:
The user's latest message is in {LANGUAGE_NAME} ({SCRIPT_NAME} script).
You MUST respond entirely and fluently in {LANGUAGE_NAME} ({SCRIPT_NAME} script).
- Do NOT reply in English unless the user explicitly requested English.
- Every section (Situation, Legal Position, Practical Next Steps, Information still needed, and Document Drafts) must be written in {LANGUAGE_NAME}.
- Use official statutory titles with English parenthetical references (e.g. ગ્રાહક સુરક્ષા અધિનિયમ, 2019 (The Consumer Protection Act, 2019)).
- Maintain natural tone, grammatical accuracy, and legal precision in {LANGUAGE_NAME}.
```

### Native Section Headers
The `LANGUAGE_CONFIG` dictionary supplies pre-translated, culturally natural headers for structured responses:

| Language | Situation Header | Legal Position Header | Next Steps Header | Info Needed Header |
|---|---|---|---|---|
| **English** | `### \| Your Situation` | `### \| Your Legal Position` | `### \| Practical Next Steps` | `### ℹ️ Information I still need from you` |
| **Hindi** | `### \| आपकी स्थिति (Your Situation)` | `### \| आपकी कानूनी स्थिति (Your Legal Position)` | `### \| व्यावहारिक अगले कदम (Practical Next Steps)` | `### ℹ️ आपसे आवश्यक जानकारी` |
| **Gujarati** | `### \| તમારી પરિસ્થિતિ (Your Situation)` | `### \| તમારો કાનૂની પક્ષ (Your Legal Position)` | `### \| વ્યવહારુ આગલા પગલાં (Practical Next Steps)` | `### ℹ️ તમારી પાસેથી જરૂરી માહિતી` |
| **Malayalam** | `### \| നിങ്ങളുടെ സാഹചര്യം (Your Situation)` | `### \| നിങ്ങളുടെ നിയമപരമായ അവകാശം (Your Legal Position)` | `### \| പ്രായോഗിക അടുത്ത നടപടികൾ (Practical Next Steps)` | `### ℹ️ നിങ്ങളിൽ നിന്ന് ആവശ്യമായ കൂടുതൽ വിവരങ്ങൾ` |
| **Tamil** | `### \| உங்கள் நிலைமை (Your Situation)` | `### \| உங்கள் சட்டப்பூர்வ நிலை (Your Legal Position)` | `### \| நடைமுறை அடுத்த கட்டங்கள்` | `### ℹ️ உங்களிடம் இருந்து தேவைப்படும் தகவல்கள்` |
| **Telugu** | `### \| మీ పరిస్థితి (Your Situation)` | `### \| మీ చట్టపరమైన స్థితి (Your Legal Position)` | `### \| ఆచరణాత్మక తదుపరి చర్యలు (Practical Next Steps)` | `### ℹ️ మీ నుండి ఇంకా అవసరమైన సమాచారం` |
| **Bengali** | `### \| আপনার বর্তমান পরিস্থিতি (Your Situation)` | `### \| আপনার আইনি অবস্থান (Your Legal Position)` | `### \| ব্যবহারিক পরবর্তী পদক্ষেপ (Practical Next Steps)` | `### ℹ️ আপনার কাছ থেকে প্রয়োজনীয় তথ্য` |
| **Hinglish** | `### \| Your Situation (Aapki Situation)` | `### \| Your Legal Position (Aapke Kanooni Adhikar)` | `### \| Practical Next Steps (Agla Kadam)` | `### ℹ️ Information I still need from you (Zaroori Jankari)` |

---

## 4. Cross-Turn Fact Retention

When a user switches languages mid-conversation:
- The session state (`session_id`) tracks conversation history across all turns.
- Numerical facts (e.g., `₹25,000`, `2 months`, `15 days`), locations (`Bangalore`, `Jaipur`), and party relationships (`landlord/tenant`, `employer/employee`) remain bound in memory.
- When shifting from English to Hinglish to Gujarati, the assistant maintains established context without requesting the user to repeat prior facts.

---

## 5. Regional Document & Notice Drafting

When prompted to generate formal documents (e.g. legal demand notices for unpaid salary or unreturned security deposit), the document generator produces complete drafts in the target Indic language.

Key drafting rules:
1. **Preserve Exact Figures:** Numerical values such as `₹25,000` or `15 days` are accurately reflected in the regional script.
2. **Clear Placeholders:** Standardized brackets `[...]` (e.g., `[તમારું નામ]`, `[મકાનમાલિકનું નામ]`, `[ખાલી કર્યાની તારીખ]`) clearly indicate details to be filled by the user.
3. **Statutory Reference:** Cites applicable acts (e.g. Model Tenancy Act, Payment of Wages Act) in the notice body.

---

## 6. Verification and Test Results

The multilingual capability is tested continuously via `tests/run_multilingual_evaluation.py`.
- **Suite Pass Rate:** 10 / 10 tests passed (100%).
- **Raw Test Artifacts:** Stored in `testing/raw_outputs/multilingual/`.
- **Test Case Manifest:** Documented in [testing/multilingual_test_cases.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/testing/multilingual_test_cases.md).
- **Test Execution Results:** Documented in [testing/multilingual_test_results.md](file:///c:/Users/ASUS/OneDrive/Desktop/kukufmm/testing/multilingual_test_results.md).
