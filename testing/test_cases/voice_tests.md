# Category J: Voice Input & Transcription Robustness Test Specifications

## 1. Context and User Dynamics
Ordinary citizens in India often describe their legal distress via voice notes or speech-to-text input rather than typing structured legal prose. Speech inputs typically feature:
- Hesitation sounds, stammering, and conversational filler words (`um`, `uh`, `you know`, `actually`, `basically`).
- Heavy emotional distress, pauses, and run-on sentences without punctuation.
- Spoken dialects and colloquial phrasing (`arre yaar`, `mera malik`, `bhai suno na`).
- Code-switching (Hinglish, Tanglish, Manglish) where technical terms are spoken in English while narrative context is in an Indian language.

## 2. Test Cases Inventory: Category J (J01 – J08)

| Test ID | Speech Acoustic Profile | Input Transcription | Expected AI Processing & Demarcation |
|---|---|---|---|
| **J01** | English Conversational | `Um, uh, basically, you know, my landlord took ₹25,000 security deposit, and like, now he won't give it back...` | Cleans conversational noise; extracts ₹25,000 security deposit withholding; outputs structured advice. |
| **J02** | Hindi Colloquial | `अरे यार वो मेरा मालिक पैसे नहीं दे रहा दो महीने से सैलरी रुकी है बहुत परेशान हूँ क्या करूँ?` | Recognizes high-stress emotional state; identifies ₹ dues; provides empathetic, actionable Hindi guidance. |
| **J03** | Gujarati Conversational | `ભાઈ સાંભળો ને, મેં ફોન લીધો તો એમેઝોન પરથી અને એ બગડેલો આવ્યો, હવે કોઈ જવાબ નથી આપતું...` | Identifies e-commerce product defect; explains CPA 2019 rights in natural Gujarati; 0 mojibake. |
| **J04** | Malayalam Cadence | Spoken transcription with regional pauses regarding 2-month salary non-payment. | Decodes legal grievance accurately; responds in fluent Malayalam with statutory provisions. |
| **J05** | Marathi Spoken Tone | Spoken Marathi audio transcription regarding defective mobile phone purchase. | Recognizes consumer rights issue; outputs complete legal analysis in Devanagari Marathi without encoding defects. |
| **J06** | Long Unpunctuated Audio | 2-minute run-on transcript: `I rented a 2bhk in Pune for 11 months deposit was 50000 rent was 18000 I gave notice on 1st March vacated 31st March now landlord deducted 20000 for painting...` | Parses dense stream into discrete timeline: Lease terms, ₹50,000 deposit, ₹20,000 painting deduction, 1-month notice compliance. |
| **J07** | Hinglish Code-Switching | `Boss ne relieving letter hold pe rakha hai bola ki target complete nahi hua jabki maine notice period serve kiya tha.` | Detects code-switched workplace grievance; explains legal invalidity of withholding service records. |
| **J08** | Incomplete Voice Snip | Trailing speech snippet: `I gave the keys to the security guard and then the owner said that the bathroom tiles...` | Gently handles trailing sentence; asks clarifying questions on whether handover receipt or photos exist. |
