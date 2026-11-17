# LawPilot AI — Multilingual Evaluation Test Results

All 10 test cases were executed against the live LawPilot AI server (`http://127.0.0.1:8000/api/chat`).
The actual raw JSON responses are saved in `testing/raw_outputs/multilingual/`.

**Overall Score:** 10 / 10 Tests Passed (100% Pass Rate)

---

## 1. Summary of Execution Results

| Test ID | Test Name | Target Language | Detected Language | Status | Latency | Script Count / Markers | Grounded Citations Verified |
|---|---|---|---|---|---|---|---|
| **ML_01** | English Baseline | `en` | `en` | **PASS** | 7.46s | Latin / Fluent English | Payment of Wages Act Sec 5, 7, 15; Contract Act Sec 73 |
| **ML_02** | Hindi Legal Guidance | `hi` | `hi` | **PASS** | 11.79s | 1,216 Devanagari chars | Payment of Wages Act Sec 5, 15; State Shops Act |
| **ML_03** | Gujarati Consumer Dispute | `gu` | `gu` | **PASS** | 13.48s | 1,284 Gujarati chars | Consumer Protection Act Sec 2(7), 2(47), 35; E-Commerce Rules |
| **ML_04** | Malayalam Employment Issue | `ml` | `ml` | **PASS** | 18.04s | 830 Malayalam chars | Payment of Wages Act Sec 5, 15; Contract Act Sec 73 |
| **ML_05** | Tamil Unpaid Wages | `ta` | `ta` | **PASS** | 6.49s | 1,251 Tamil chars | Payment of Wages Act Sec 5, 15; State Shops Act |
| **ML_06** | Telugu Unpaid Salary | `te` | `te` | **PASS** | 9.28s | 1,306 Telugu chars | Payment of Wages Act Sec 5, 7; Contract Act Sec 73 |
| **ML_07** | Bengali Salary Non-Payment | `bn` | `bn` | **PASS** | 5.50s | 1,188 Bengali chars | Payment of Wages Act Sec 5, 15; State Shops Act |
| **ML_08** | Hinglish Conversational Query | `hinglish` | `hinglish` | **PASS** | 6.47s | 14 Hinglish markers | Payment of Wages Act Sec 5, 15; State Shops Act |
| **ML_09** | Multi-Turn Language Switching | `en` -> `hinglish` -> `gu` | Auto per turn | **PASS** | 22.1s (total) | Turn 1: English<br>Turn 2: 25 markers<br>Turn 3: 850 Gujarati chars | Model Tenancy Act, Transfer of Property Act Sec 108 |
| **ML_10** | Document Generation (Gujarati) | `gu` | `gu` | **PASS** | 12.3s | 1,203 Gujarati chars | ₹25,000 preserved, 15-day notice clause, editable `[...]` |

---

## 2. Detailed Test Results & Raw Outputs

### Test 1 — English Baseline (ML_01_English)
- **Input:** *"My employer in Bangalore has not paid my salary for two months."*
- **Detected Language:** `en`
- **Result:** **PASS**
- **Excerpt:**
  > "Hello, I am LawPilot AI, your Indian legal assistant. I understand how stressful it is to face non-payment of your hard-earned salary, but please rest assured that Indian labor laws provide clear protections for employees in this exact situation.
  > 
  > ### | Your Situation
  > You are an employee working in Bangalore whose employer has withheld your salary for two months. The key issue is the illegal withholding of earned wages without lawful justification.
  > 
  > ### | Your Legal Position
  > * Under Section 5 of The Payment of Wages Act, 1936, wages must be paid before the expiry of the seventh day after the last day of the wage period... Direct statutory violation.
  > * Under Section 15 of The Payment of Wages Act, 1936, you have the right to approach the designated Labour Authority..."

---

### Test 2 — Hindi Legal Guidance (ML_02_Hindi)
- **Input:** *"मेरे नियोक्ता ने पिछले दो महीनों से मेरा वेतन नहीं दिया है। मैं क्या कर सकता हूँ?"*
- **Detected Language:** `hi` (Devanagari)
- **Result:** **PASS** (1,216 Devanagari characters)
- **Excerpt:**
  > "नमस्ते, आपकी इस समस्या को सुनकर मुझे बहुत दुख हुआ और मैं आपकी सहायता के लिए यहाँ LawPilot AI हूँ।
  > 
  > ### | आपकी स्थिति (Your Situation)
  > आपके नियोक्ता (employer) ने पिछले दो महीनों से आपका वेतन रोक लिया है... यह मामला एक व्यावसायिक प्रतिष्ठान या कंपनी में कार्यरत कर्मचारी के अवैतनिक वेतन (unpaid wages) से संबंधित है।
  > 
  > ### | आपकी कानूनी स्थिति (Your Legal Position)
  > - **द पेमेंट ऑफ़ वेजेज एक्ट, 1936 की धारा 5:** इस कानून के अनुसार, वेतन का भुगतान वेतन अवधि समाप्त होने के बाद 7वें दिन से पहले किया जाना अनिवार्य है...
  > - **द पेमेंट ऑफ़ वेजेज एक्ट, 1936 की धारा 15:** इस धारा के तहत, आप विलंबित वेतन या अनुचित कटौती के मामलों में श्रम आयुक्त (Labour Commissioner) के समक्ष आवेदन कर सकते हैं..."

---

### Test 3 — Gujarati Consumer Dispute (ML_03_Gujarati)
- **Input:** *"મેં ઑનલાઇન એક ખામીયુક્ત ફોન ખરીદ્યો છે અને વેચનાર મને રિફંડ આપવાનો ઇનકાર કરી રહ્યો છે. હવે હું શું કરી શકું?"*
- **Detected Language:** `gu` (Gujarati)
- **Result:** **PASS** (1,284 Gujarati characters)
- **Key Finding:** Resolved root cause where system previously defaulted to English. Assistant now replies strictly in natural Gujarati with statutory accuracy.
- **Excerpt:**
  > "તમારી મુશ્કેલી બદલ મને ખેદ છે, હું તમારા કાનૂની અધિકારો મેળવવામાં તમારી મદદ કરવા માટે અહીં છું.
  > 
  > ### | તમારી પરિસ્થિતિ (Your Situation)
  > તમે ઑનલાઇન પ્લેટફોર્મ પરથી એક મોબાઈલ ફોન ખરીદ્યો છે જે ખામીયુક્ત નીકળ્યો છે, અને વેચનાર કે ઈ-કોમર્સ કંપની તમને રિફંડ આપવાનો ઇનકાર કરી રહી છે. આ બાબત ગ્રાહક અધિકારોના ભંગ અને ગેરવાજબી વેપાર પ્રથા હેઠળ આવે છે.
  > 
  > ### | તમારો કાનૂની પક્ષ (Your Legal Position)
  > - ગ્રાહક સુરક્ષા અધિનિયમ, 2019 ની કલમ 2(7) મુજબ, તમે કિંમત ચૂકવીને માલ ખરીદનાર "ગ્રાહક" છો...
  > - ગ્રાહક સુરક્ષા અધિનિયમ, 2019 ની કલમ 2(47) હેઠળ ખામીયુક્ત ચીજવસ્તુ પાછી લેવાનો ઇનકાર કરવો અથવા 30 દિવસની અંદર રિફંડ ન આપવું એ એક "અનફેર ટ્રેડ પ્રેક્ટિસ" (અયોગ્ય વેપાર પ્રથા) ગણાય છે...
  > - ગ્રાહક સુરક્ષા (ઈ-કોમર્સ) નિયમો, 2020 ના નિયમ 4 અને 6 અનુસાર, ઈ-કોમર્સ કંપનીઓએ ગ્રીવન્સ ઓફિસર નીમવા પડે છે...
  > 
  > ### | વ્યવહારુ આગલા પગલાં (Practical Next Steps)
  > 1. ઓર્ડરની પહોંચ (Invoice), પેમેન્ટની રસીદ, ખામી દર્શાવતા ફોટોગ્રાફ્સ ભેગા કરો...
  > 2. કંપનીને લેખિતમાં માંગણી નોટિસ મોકલો અને 15 દિવસની અંદર રિફંડ આપવા જણાવો...
  > 3. રાષ્ટ્રીય ગ્રાહક હેલ્પલાઇન (NCH - 1915) અથવા e-Daakhil પૉર્ટલ દ્વારા ફરિયાદ દાખલ કરો."

---

### Test 4 — Malayalam Employment Issue (ML_04_Malayalam)
- **Input:** *"എന്റെ ബാംഗ്ലൂരിലുള്ള തൊഴിലുടമ കഴിഞ്ഞ രണ്ട് മാസമായി എനിക്ക് ശമ്പളം നൽകിയിട്ടില്ല. ഞാൻ എന്ത് ചെയ്യണം?"*
- **Detected Language:** `ml` (Malayalam)
- **Result:** **PASS** (830 Malayalam characters)
- **Excerpt:**
  > "ഇന്ത്യൻ തൊഴിൽ, വേതന നിയമങ്ങളുടെ അടിസ്ഥാനത്തിൽ നിങ്ങളുടെ കേസിന്റെ നിയമപരമായ വിലയിരുത്തൽ താഴെ നൽകുന്നു:
  > 
  > ### | നിങ്ങളുടെ സാഹചര്യം (Your Situation)
  > നിങ്ങളുടെ തൊഴിലുടമ കഴിഞ്ഞ രണ്ട് മാസമായി നിങ്ങളുടെ ശമ്പളം തടഞ്ഞുവെച്ചിരിക്കുകയാണ്...
  > 
  > ### | നിങ്ങളുടെ നിയമപരമായ അവകാശം (Your Legal Position)
  > * **വേതന വിതരണ നിയമം, 1936 (വകുപ്പ് 5)**: വേതന കാലയളവ് കഴിഞ്ഞ് 7 മുതൽ 10 ദിവസത്തിനകം തൊഴിലുടമ ശമ്പളം വിതരണം ചെയ്യണം.
  > * **വേതന വിതരണ നിയമം, 1936 (വകുപ്പ് 15)**: കുടിശ്ശികയുള്ള ശമ്പളം നഷ്ടപരിഹാരത്തോടെ തിരികെ ലഭിക്കാൻ ലേബർ കമ്മീഷണറെ സമീപിക്കാം."

---

### Test 5 — Tamil Unpaid Wages (ML_05_Tamil)
- **Input:** *"எனது நிறுவனம் கடந்த இரண்டு மாதங்களாக எனக்கு சம்பளம் வழங்கவில்லை. நான் என்ன செய்ய வேண்டும்?"*
- **Detected Language:** `ta` (Tamil)
- **Result:** **PASS** (1,251 Tamil characters)
- **Excerpt:**
  > "வணக்கம், நான் உங்கள் லாவ் பிலாட் ஏஐ (LawPilot AI), உங்களுக்கு உதவ இங்கே இருக்கிறேன்.
  > 
  > ### | உங்கள் நிலைமை (Your Situation)
  > உங்கள் நிறுவனம் கடந்த இரண்டு மாதங்களாக உங்களுக்கு சம்பளம் வழங்கவில்லை...
  > 
  > ### | உங்கள் சட்டப்பூர்வ நிலை (Your Legal Position)
  > - ஊதிய வழங்கல் சட்டம், 1936 இன் பிரிவு 5 மற்றும் மாநில கடைகள் மற்றும் வணிக நிறுவனங்கள் சட்டத்தின் படி, நிறுவனங்கள் குறிப்பிட்ட காலத்திற்குள் ஊதியம் வழங்குவது கட்டாயமாகும்.
  > - ஊதிய வழங்கல் சட்டம், 1936 இன் பிரிவு 15 இன் கீழ், தொழிலாளர் அதிகாரியிடம் (Labour Authority/Commissioner) முறையிட உங்களுக்கு உரிமை உண்டு."

---

### Test 6 — Telugu Unpaid Salary (ML_06_Telugu)
- **Input:** *"నా యజమాని గత రెండు నెలలుగా నాకు జీతం చెల్లించలేదు. నేను ఏమి చేయాలి?"*
- **Detected Language:** `te` (Telugu)
- **Result:** **PASS** (1,306 Telugu characters)
- **Excerpt:**
  > "నమస్కారం, మీ యజమాని గత రెండు నెలలుగా జీతం చెల్లించకపోవడం వల్ల మీరు ఎదుర్కొంటున్న ఆర్థిక ఇబ్బందికి నేను చింతిస్తున్నాను.
  > 
  > ### | మీ పరిస్థితి (Your Situation)
  > మీరు ఒక ఉద్యోగి అయి ఉండి, మీ యజమాని మీకు గత రెండు నెలలుగా రావాల్సిన జీతాన్ని ఇవ్వకుండా నిలిపివేశారు...
  > 
  > ### | మీ చట్టపరమైన స్థితి (Your Legal Position)
  > - ది పేమెంట్ ఆఫ్ వేజెస్ యాక్ట్, 1936 సెక్షన్ 5 ప్రకారం, వేతన కాలం ముగిసిన తర్వాత 7వ తేదీలోపు యజమాని జీతం చెల్లించాలి.
  > - ది ఇండియన్ కాంట్రాక్ట్ యాక్ట్, 1872 సెక్షన్ 73 ప్రకారం నష్టపరిహారానికి యజమాని బాధ్యత వహించాలి."

---

### Test 7 — Bengali Salary Non-Payment (ML_07_Bengali)
- **Input:** *"আমার নিয়োগকর্তা গত দুই মাস ধরে আমাকে বেতন দেননি। আমি কী করতে পারি?"*
- **Detected Language:** `bn` (Bengali)
- **Result:** **PASS** (1,188 Bengali characters)
- **Excerpt:**
  > "আপনার এই কঠিন পরিস্থিতিতে আমি আন্তরিকভাবে দুঃখিত এবং আপনার পাশে আছি।
  > 
  > ### | আপনার বর্তমান পরিস্থিতি (Your Situation)
  > আপনি একজন চাকরিজীবী এবং আপনার নিয়োগকর্তা গত দুই মাস ধরে আপনার বকেয়া বেতন আটকে রেখেছেন...
  > 
  > ### | আপনার আইনি অবস্থান (Your Legal Position)
  > * পেমেন্ট অফ ওয়েজেস অ্যাক্ট, ১৯৩৬-এর ধারা ৫ অনুযায়ী, নির্দিষ্ট মজুরি মেয়াদ শেষ হওয়ার পরবর্তী ৭ দিনের মধ্যে বেতন পরিশোধ করা বাধ্যতামূলক।
  > * ধারা ১৫ অনুযায়ী, বেতন প্রদানে বিলম্বের বিরুদ্ধে ক্ষতিপূরণসহ লেবার কমিশনারের নিকট আবেদন করার আইনি অধিকার আপনার রয়েছে।"

---

### Test 8 — Hinglish Conversational Query (ML_08_Hinglish)
- **Input:** *"Meri company ne do mahine se salary nahi di hai. Main kya kar sakta hoon?"*
- **Detected Language:** `hinglish`
- **Result:** **PASS** (14 Hinglish colloquial markers detected, 0 Devanagari characters)
- **Excerpt:**
  > "Main aapki pareshani samajh sakta hoon aur aapki is mushkil samay mein poori madad karoonga.
  > 
  > ### | Your Situation (Aapki Situation)
  > Aapki company ne aapko pichle do mahine se salary nahi di hai, jisse aapko financial aur mental pareshani ka samna karna pad raha hai. Yeh mamla employment dispute aur unpaid wages ke antargat aata hai.
  > 
  > ### | Your Legal Position (Aapke Kanooni Adhikar)
  > - The Payment of Wages Act, 1936 ke Section 5 ke anusar, wages (salary) ka bhugtaan wage period khatam hone ke 7 din ke andar ho jana chahiye...
  > - Payment of Wages Act ke Section 15 ke antargat Labour Commissioner ke paas application daal sakte hain...
  > 
  > ### | Practical Next Steps (Agla Kadam)
  > 1. Apni employment contract, appointment letter, payslips aur bank statements ki copies ikattha karein.
  > 2. Company ko ek likhit demand notice bhejiye jisme 15 din ke andar apni baaki salary ka poora bhugtaan karne ko kahein."

---

### Test 9 — Multi-Turn Language Switching (ML_09_Language_Switching)
- **Turn 1 (English):** *"My landlord has not returned my security deposit."*
  - **Assistant Response:** Responds in English explaining deposit recovery rights under Model Tenancy Act 2021 and Transfer of Property Act 1882.
- **Turn 2 (Hinglish):** *"Ab mujhe legal notice bhejna hai."*
  - **Assistant Response:** Responds in Hinglish, generating a full legal notice draft (`LEGAL NOTICE DRAFT (KANOONI NOTICE)`) tailored to security deposit recovery with ₹[Amount] and a 15-day compliance window.
- **Turn 3 (Gujarati):** *"મારે હવે આગળ શું કરવું જોઈએ?"*
  - **Assistant Response:** Responds in Gujarati, preserving the landlord-tenant dispute context, referencing the notice already drafted, and guiding the tenant on approaches to the Rent Authority if the landlord does not respond within 15 days.
- **Result:** **PASS** across all 3 turns. 0 context loss.

---

### Test 10 — Legal Document Generation in Gujarati (ML_10_Document_Generation_Gujarati)
- **Input:** *"મારા મકાનમાલિકને ₹25,000 સિક્યોરિટી ડિપોઝિટ પરત આપવા માટે એક ઔપચારિક પત્ર તૈયાર કરો."*
- **Detected Language:** `gu` (Gujarati)
- **Result:** **PASS** (1,203 Gujarati characters)
- **Key Verifications:**
  - Preserved exact deposit amount: `₹25,000/- (પચીસ હજાર રૂપિયા પૂરા)`.
  - Proper legal document format:
    ```
    **કાનૂની માંગણી નોટિસ (LEGAL DEMAND NOTICE)**
    તારીખ: [આજની તારીખ દાખલ કરો]
    પ્રતિ,
    [મકાનમાલિકનું નામ]
    [મકાનમાલિકનું સરનામું]
    વિષય: ₹25,000/- સિક્યોરિટી ડિપોઝિટ પરત કરવા બાબત.
    ...
    આથી, આ નોટિસ મળ્યાના 15 દિવસ ની અંદર મારી ₹25,000/- ની રકમ પૂરેપૂરી પરત કરવા અથવા મારા બેંક ખાતામાં જમા કરાવવા વિનંતી છે...
    ```
  - Standard placeholders `[...]` for tenant name, date, address.
  - Statutory grounding in Model Tenancy Act, 2021.

---

## 3. Conclusion
The multilingual engine in LawPilot AI operates with full automatic detection and consistent language delivery across English, Hindi, Gujarati, Malayalam, Tamil, Telugu, Bengali, and Hinglish. Statutory grounding, fact preservation, and formal legal document drafting are verified across all test scenarios.
