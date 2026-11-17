# LawPilot AI — Multilingual Evaluation Test Cases

Comprehensive test specifications for verifying automatic language detection, cross-turn response language consistency, case fact retention, and legal document generation across Indian regional languages.

---

## 1. Objectives

1. **Automatic Detection:** The application must automatically detect the user's input language per turn without requiring or depending on a manual dropdown selector.
2. **Language Consistency:** If the user prompts in an Indic language (e.g., Gujarati, Malayalam, Tamil, Telugu, Bengali, Hindi, or Hinglish), the assistant must reply in that exact same language, utilizing native legal terminology and proper script.
3. **Cross-Turn Continuity:** When a user switches languages mid-conversation (e.g., English -> Hinglish -> Gujarati), all established facts (amounts, parties, dispute history) must be preserved.
4. **Legal Grounding & Accuracy:** Statutory citations (Payment of Wages Act 1936, Consumer Protection Act 2019, Model Tenancy Act 2021) must remain grounded and uncorrupted by translation.
5. **Document Drafting:** When asked to generate legal notices or letters in an Indic language, the system must draft the complete legal notice in that language with appropriate placeholders.

---

## 2. Test Suite Specifications

| Test ID | Test Name | Language & Script | Domain | Input Prompt | Expected Evaluation Criteria |
|---|---|---|---|---|---|
| **ML_01** | English Baseline | English (Latin) | Employment / Wages | *"My employer in Bangalore has not paid my salary for two months."* | - Response strictly in fluent English.<br>- Identifies Payment of Wages Act 1936 Section 5 & 15.<br>- Preserves Bangalore jurisdiction & 2-month unpaid timeline.<br>- Suggests 15-day written demand notice. |
| **ML_02** | Hindi Legal Guidance | Hindi (Devanagari) | Employment / Wages | *"मेरे नियोक्ता ने पिछले दो महीनों से मेरा वेतन नहीं दिया है। मैं क्या कर सकता हूँ?"* | - Response strictly in Hindi (Devanagari script).<br>- Translates section headers (*आपकी स्थिति*, *आपकी कानूनी स्थिति*, *व्यावहारिक अगले कदम*).<br>- References Payment of Wages Act धारा 5 & 15. |
| **ML_03** | Gujarati Consumer Dispute | Gujarati (Gujarati script) | Consumer Protection | *"મેં ઑનલાઇન એક ખામીયુક્ત ફોન ખરીદ્યો છે અને વેચનાર મને રિફંડ આપવાનો ઇનકાર કરી રહ્યો છે. હવે હું શું કરી શકું?"* | - Response strictly in Gujarati (Gujarati script).<br>- Never defaults to English.<br>- Cites Consumer Protection Act, 2019 Section 2(7) & Section 2(47) (Unfair Trade Practice), and E-Commerce Rules, 2020.<br>- Mentions e-Daakhil and National Consumer Helpline. |
| **ML_04** | Malayalam Employment Issue | Malayalam (Malayalam script) | Employment / Wages | *"എന്റെ ബാംഗ്ലൂരിലുള്ള തൊഴിലുടമ കഴിഞ്ഞ രണ്ട് മാസമായി എനിക്ക് ശമ്പളം നൽകിയിട്ടില്ല. ഞാൻ എന്ത് ചെയ്യണം?"* | - Response strictly in Malayalam script.<br>- Correctly extracts Bangalore employer context.<br>- Cites Payment of Wages Act (വകുപ്പ് 5, 15) & Contract Act 1872.<br>- Translates headers (*നിങ്ങളുടെ സാഹചര്യം*, *പ്രായോഗിക അടുത്ത നടപടികൾ*). |
| **ML_05** | Tamil Unpaid Wages | Tamil (Tamil script) | Employment / Wages | *"எனது நிறுவனம் கடந்த இரண்டு மாதங்களாக எனக்கு சம்பளம் வழங்கவில்லை. நான் என்ன செய்ய வேண்டும்?"* | - Response strictly in Tamil script.<br>- Explains 2-month delay under Payment of Wages Act Section 5 & 15 and State Shops & Establishments Act.<br>- Outlines step-by-step guidance in Tamil. |
| **ML_06** | Telugu Unpaid Salary | Telugu (Telugu script) | Employment / Wages | *"నా యజమాని గత రెండు నెలలుగా నాకు జీతం చెల్లించలేదు. నేను ఏమి చేయాలి?"* | - Response strictly in Telugu script.<br>- Explains legal rights under Payment of Wages Act Sec 5 & 7.<br>- Advises written demand notice with 15 days deadline. |
| **ML_07** | Bengali Salary Non-Payment | Bengali (Bengali script) | Employment / Wages | *"আমার নিয়োগকর্তা গত দুই মাস ধরে আমাকে বেতন দেননি। আমি কী করতে পারি?"* | - Response strictly in Bengali script.<br>- Cites Payment of Wages Act 1936 Sec 5.<br>- Guides reporting to Labour Commissioner. |
| **ML_08** | Hinglish Conversational Query | Hinglish (Latin) | Employment / Wages | *"Meri company ne do mahine se salary nahi di hai. Main kya kar sakta hoon?"* | - Response strictly in conversational Hinglish (Roman script).<br>- No Devanagari script output.<br>- Professional, approachable tone with legal grounding. |
| **ML_09** | Multi-Turn Language Switching | English -> Hinglish -> Gujarati | Tenancy / Deposit | **Turn 1:** *"My landlord has not returned my security deposit."*<br>**Turn 2:** *"Ab mujhe legal notice bhejna hai."*<br>**Turn 3:** *"મારે હવે આગળ શું કરવું જોઈએ?"* | - **Turn 1:** Responds in English explaining deposit recovery.<br>- **Turn 2:** Responds in Hinglish drafting legal notice with 15-day period.<br>- **Turn 3:** Responds in Gujarati explaining next steps after sending notice.<br>- Retains tenant/landlord context across all 3 turns. |
| **ML_10** | Legal Document Drafting (Gujarati) | Gujarati (Gujarati script) | Tenancy / Deposit | *"મારા મકાનમાલિકને ₹25,000 સિક્યોરિટી ડિપોઝિટ પરત આપવા માટે એક ઔપચારિક પત્ર તૈયાર કરો."* | - Drafts complete legal notice in Gujarati script.<br>- Preserves exact amount (₹25,000 / પચીસ હજાર).<br>- Includes editable brackets `[...]` for dates, addresses, and tenant name.<br>- Specifies 15-day compliance window. |

---

## 3. Evaluation Metrics

1. **Script Purity:** Count of characters belonging to the target script Unicode block:
   - Gujarati: `0x0A80` - `0x0AFF`
   - Devanagari (Hindi): `0x0900` - `0x097F`
   - Malayalam: `0x0D00` - `0x0D7F`
   - Tamil: `0x0B80` - `0x0BFF`
   - Telugu: `0x0C00` - `0x0C7F`
   - Bengali: `0x0980` - `0x09FF`
2. **Hinglish Quality:** Natural lexical density of conversational Hindi markers written in Latin script (`aap`, `karein`, `salary`, `bhejein`, `paise`, `hoga`).
3. **Statutory Preservation:** Accurate citation of Indian acts and sections without hallucination or mistranslation.
4. **Context Retention:** Accuracy of retaining specific facts (e.g. ₹25,000, 2 months unpaid, Bangalore location) when switching languages.
