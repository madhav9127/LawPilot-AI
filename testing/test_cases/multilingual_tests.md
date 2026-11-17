# Category E & J: Multilingual & Cross-Language Consistency Test Specifications

## 1. Multilingual Architecture & Response Mandate
LawPilot AI enforces automatic language detection and consistent response-language matching across 8 Indian languages plus Hinglish:
1. **English (en)**: Latin script
2. **Hindi (hi)**: Devanagari script (Unicode U+0900 – U+097F)
3. **Gujarati (gu)**: Gujarati script (Unicode U+0A80 – U+0AFF)
4. **Marathi (mr)**: Devanagari script (Unicode U+0900 – U+097F)
5. **Malayalam (ml)**: Malayalam script (Unicode U+0D00 – U+0D7F)
6. **Tamil (ta)**: Tamil script (Unicode U+0B80 – U+0BFF)
7. **Telugu (te)**: Telugu script (Unicode U+0C00 – U+0C7F)
8. **Bengali (bn)**: Bengali script (Unicode U+0980 – U+09FF)
9. **Hinglish (hinglish)**: Latin script phonetic Hindi

### Zero Mojibake Guarantee
Any occurrence of Latin-1 mis-decoded UTF-8 sequences (such as `à¤`, `à¥`, `à¦`, `à®`, `à°`, `Ã`, `Â`) constitutes an instant Critical Failure (score 0/100). The underlying Unicode pipeline forces UTF-8 byte stream decoding, `resp.encoding = "utf-8"`, and native Unicode font stacks (`Nirmala UI`, `Mangal`).

### Dynamic Mid-Conversation Switching
If a user switches languages mid-conversation (e.g. from English to Gujarati or Hindi), the assistant must dynamically adapt its response language to match the latest prompt while preserving the established factual case memory.

## 2. Test Cases Inventory: Category E — Core Multilingual Capabilities (E01 – E14)

| Test ID | Language & Script | Input Prompt | Expected Response Characteristics |
|---|---|---|---|
| **E01** | Hindi (Devanagari) | `मेरा मकान मालिक ₹30,000 की सिक्योरिटी डिपॉजिट वापस नहीं कर रहा है।` | 100% Devanagari Hindi; explains tenancy rights, deposit return demand; 0 mojibake. |
| **E02** | Gujarati (Gujarati) | `મેં ઑનલાઇન એક ખામીયુક્ત ફોન ખરીદ્યો છે અને વેચનાર મને રિફંડ આપવાનો ઇનકાર કરી રહ્યો છે.` | 100% Gujarati script; CPA 2019 rights; 0 English fallback; 0 mojibake. |
| **E03** | Marathi (Devanagari) | `मी ऑनलाइन एक दोषपूर्ण मोबाईल फोन खरेदी केला आहे आणि विक्रेता मला पैसे परत करण्यास नकार देत आहे. आता मी काय करू शकतो?` | Fluent Devanagari Marathi; consumer rights, 0 mojibake (`à¤...à¤...` strictly forbidden). |
| **E04** | Malayalam (Malayalam) | `എന്റെ കമ്പനി കഴിഞ്ഞ രണ്ട് മാസമായി എനിക്ക് ശമ്പളം നൽകിയിട്ടില്ല. എനിക്ക് എന്ത് ചെയ്യാൻ കഴിയും?` | Fluent Malayalam script; Payment of Wages Act Sec 5/15; Labour Commissioner remedy. |
| **E05** | Tamil (Tamil) | `என் வீட்டு உரிமையாளர் வாடகை முன்பணத்தை திருப்பித் தர மறுக்கிறார்.` | Fluent Tamil script; tenancy rights, formal demand notice; 0 mojibake. |
| **E06** | Telugu (Telugu) | `నా యజమాని రెండు నెలలుగా జీతం ఇవ్వడం లేదు. నేను ఏమి చేయాలి?` | Fluent Telugu script; wage recovery rights, 15-day notice; 0 mojibake. |
| **E07** | Bengali (Bengali) | `আমার বাড়িওয়ালা সিকিউরিটি ডিপোজিট ফেরত দিতে অস্বীকার করছেন।` | Fluent Bengali script; deposit refund rights, notice structure; 0 mojibake. |
| **E08** | Hinglish (Latin) | `Mera landlord deposit wapas nahi de raha hai bol raha hai painting ka katega.` | Natural colloquial Hinglish; explains wear and tear; advice on written demand. |
| **E09** | English (Latin) | `My employer has withheld my salary for 2 months.` | Structured English; Situation, Legal Position, Practical Next Steps, Info Needed. |
| **E10** | Multilingual Switch | Turn 1: English (`My landlord took ₹25,000`) -> Turn 2: Gujarati (`હવે મારે શું કરવું જોઈએ?`) | Turn 2 response must immediately switch to 100% Gujarati while preserving ₹25,000 facts. |
| **E11** | Multilingual Switch | Turn 1: Hindi -> Turn 2: English | Turn 2 response must switch to English while keeping established Hindi context. |
| **E12** | Multilingual Switch | Turn 1: Gujarati -> Turn 2: Hindi | Turn 2 response must switch to Hindi preserving all Gujarati facts. |
| **E13** | Multilingual Switch | Turn 1: Marathi -> Turn 2: English | Turn 2 response must switch to English maintaining Marathi dispute details. |
| **E14** | Indic Legal Notice | Gujarati notice demand (`મને કાનૂની નોટિસનો ડ્રાફ્ટ આપો`) | Full legal demand draft generated in Gujarati with placeholders for missing dates. |

## 3. Test Cases Inventory: Category J — Voice & Speech Robustness (J01 – J08)

| Test ID | Audio/Transcription Style | Voice Input Characteristics | Expected Robustness Handling |
|---|---|---|---|
| **J01** | English Voice Transcription | Filler words: `Um, uh, basically my landlord, you know, took 20000 rupees...` | Ignores conversational fillers; extracts ₹20,000 deposit fact accurately. |
| **J02** | Hindi Voice Transcription | Casual speech: `अरे यार वो मेरा मालिक पैसे नहीं दे रहा दो महीने से सैलरी रुकी है...` | Empathizes naturally, recognizes 2 months unpaid salary, provides structured steps. |
| **J03** | Gujarati Voice Transcription | Conversational tone: `ભાઈ સાંભળો ને, મેં ફોન લીધો તો એમેઝોન પરથી...` | Identifies e-commerce consumer grievance; responds in pure Gujarati. |
| **J04** | Malayalam Voice Transcription | Spoken cadence with hesitation markers. | Decodes legal intent, provides clear Malayalam recovery pathway. |
| **J05** | Marathi Voice Transcription | Spoken colloquial Marathi with pauses. | Accurately extracts dispute without confusion; responds in Marathi. |
| **J06** | Long Voice Stream | 2-minute run-on transcription covering multiple facts without punctuation. | Segregates key facts (parties, dates, amounts) into structured case overview. |
| **J07** | Code-Switching Speech | Spoken sentence mixing English and Hindi words (`salary delay ho gaya aur boss phone cut kar raha hai`). | Recognizes Hinglish/code-mixed speech; responds in seamless natural Hinglish. |
| **J08** | Incomplete Voice Input | Trailing voice snippet (`I paid the deposit but then he said that the wall...`). | Handles gracefully; clarifies missing detail without hallucinating outcome. |
