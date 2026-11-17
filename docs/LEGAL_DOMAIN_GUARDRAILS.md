# LawPilot AI — Legal Domain Specialisation & Scope Guardrails

## 1. Executive Summary
LawPilot AI is engineered specifically as an Indian civil legal assistant for ordinary citizens. It is intentionally designed **not** to function as a general-purpose conversational LLM (answering general trivia, solving math problems, writing software code, or commenting on sports).

This document outlines the architecture, detection logic, and empirical evaluation of the **Legal Domain Specialisation Framework** implemented in `app/core/domain_guardrail.py`.

---

## 2. Guardrail Philosophy & Policy

### 2.1 Supported In-Scope Domains
1. **Tenant & Landlord Disputes:** Security deposits, arbitrary painting/cleaning deductions, notice periods, habitability/repairs, unlawful eviction protections.
2. **Consumer Protection:** Defective goods, delayed/refused refunds, warranty disputes, e-commerce grievances, unfair trade practices under CPA 2019.
3. **Employment & Salary Disputes:** Unpaid wages, full & final (FnF) delays, withheld relieving letters, illegal deductions under the Payment of Wages Act, 1936.

### 2.2 Out-of-Scope Requests Handling
When a user submits an off-topic request that contains no legal issue or prior conversational legal context:
- The assistant **does not** answer the unrelated prompt.
- It politely issues a localized domain redirection explaining its legal assistance mandate and prompts the user to state their legal issue.
- Sub-5ms fast-track execution prevents unnecessary LLM token waste.

### 2.3 Mixed Query Handling
When a user combines a legitimate legal question with an off-topic inquiry (e.g., *"My landlord hasn't returned my deposit, and what is the capital of France?"*):
- The assistant **comprehensively answers the legal issue** with statutory grounding and next steps.
- The assistant **politely declines the unrelated topic**, reiterating that it specializes strictly in Indian legal assistance.

### 2.4 Ambiguous Distress & Conversational Openers
Conversational openers (*"Hi"*, *"Good morning"*), capability inquiries (*"What can you help me with?"*), and ambiguous emotional distress (*"I am confused and need help"*, *"I received a notice"*) are recognized as legitimate entry points and are welcomed warmly without deflection.

---

## 3. Multilingual Redirection Matrix

Redirection messages are natively available in 8 Indian languages plus Hinglish:

| Language | Redirection Notice |
|---|---|
| **English** | *I am LawPilot AI, an assistant specialising in everyday legal problems in India. I can help you understand your legal rights, organise your case, identify possible options and prepare legal documents. I cannot assist with general topics outside my legal-assistance scope. Is there a legal issue I can help you with?* |
| **Hindi** | *मैं LawPilot AI हूँ, जो भारत में रोजमर्रा की कानूनी समस्याओं के लिए एक विशेष कानूनी सहायक है। मैं आपके कानूनी अधिकारों को समझने, आपके मामले को व्यवस्थित करने और कानूनी दस्तावेज तैयार करने में मदद कर सकता हूँ। मैं अपने कानूनी दायरे से बाहर के सामान्य विषयों में सहायता नहीं कर सकता। क्या कोई कानूनी समस्या है जिसमें मैं आपकी मदद कर सकता हूँ?* |
| **Gujarati** | *હું LawPilot AI છું, ભારતમાં રોજિંદા કાનૂની અધિકારો માટે વિશેષ કાનૂની સહાયક. હું તમને તમારા કાનૂની અધિકારો સમજવામાં, કેસ ગોઠવવામાં અને કાનૂની દસ્તાવેજો તૈયાર કરવામાં મદદ કરી શકું છું. હું મારા કાનૂની કાર્યક્ષેત્ર બહારના સામાન્ય વિષયોમાં સહાય કરી શકતો નથી. શું કોઈ કાનૂની બાબત છે જેમાં હું તમને મદદ કરી શકું?* |
| **Marathi** | *मी LawPilot AI आहे, भारतातील दैनंदिन नागरी कायदेशीर समस्यांसाठी एक विशेष कायदेशीर सहाय्यक. मी तुमचे कायदेशीर हक्क समजून घेण्यास, तुमचा खटला तयार करण्यास आणि कायदेशीर कागदपत्रे तयार करण्यास मदत करू शकतो. मी माझ्या कायदेशीर कार्यक्षेत्राबाहेरील सामान्य विषयांमध्ये मदत करू शकत नाही. मी तुम्हाला मदत करू शकेन असा कोणताही कायदेशीर प्रश्न आहे का?* |
| **Malayalam** | *ഞാൻ LawPilot AI ആണ്, ഇന്ത്യയിലെ ദൈനംദിന നിയമ പ്രശ്നങ്ങളിൽ സഹായിക്കുന്ന ഒരു പ്രത്യേക നിയമ സഹായി. നിങ്ങളുടെ നിയമപരമായ അവകാശങ്ങൾ മനസിലാക്കാനും രേഖകൾ തയ്യാറാക്കാനും ഞാൻ സഹായിക്കാം. നിയമ സഹായ പരിധിക്ക് പുറത്തുള്ള പൊതുവായ വിഷയങ്ങളിൽ എനിക്ക് സഹായിക്കാനാകില്ല. ഞാൻ സഹായിക്കേണ്ട എന്തെങ്കിലും നിയമപരമായ പ്രശ്നമുണ്ടോ?* |
| **Tamil** | *நான் LawPilot AI, இந்தியாவில் அன்றாட சட்டப் பிரச்சனைகளுக்கான சிறப்பு சட்ட உதவியாளர். உங்கள் சட்டப்பூர்வ உரிமைகளைப் புரிந்து கொள்ளவும் சட்ட ஆவணங்களைத் தயாரிக்கவும் நான் உங்களுக்கு உதவ முடியும். சட்ட எல்லைக்கு அப்பாற்பட்ட பொதுவான தலைப்புகளில் என்னால் உதவ முடியாது. நான் உதவக்கூடிய சட்டப் பிரச்சனை ஏதேனும் உள்ளதா?* |
| **Telugu** | *నేను LawPilot AI, భారతదేశంలో రోజువారీ చట్టపరమైన సవాళ్ల కోసం ప్రత్యేక సహాయకుడిని. మీ చట్టపరమైన హక్కులను అర్థం చేసుకోవడానికి మరియు చట్టపరమైన పత్రాలను సిద్ధం చేయడానికి నేను సహాయపడగలను. నా చట్టపరమైన పరిధికి వెలుపల ఉన్న సాధారణ అంశాలలో నేను సహాయం చేయలేను. నేను మీకు సహాయం చేయగల చట్టపరమైన సమస్య ఏదైనా ఉందా?* |
| **Bengali** | *আমি LawPilot AI, ভারতে দৈনন্দিন নাগরিক আইনি সমস্যার জন্য একটি বিশেষ আইনি সহায়ক। আমি আপনাকে আপনার অধিকার বুঝতে এবং আইনি নথি তৈরি করতে সাহায্য করতে পারি। আমার আইনি সহায়তার পরিধির বাইরের সাধারণ বিষয়ে আমি সাহায্য করতে পারি না। এমন কোনো আইনি সমস্যা আছে যাতে আমি সাহায্য করতে পারি?* |
| **Hinglish** | *Main LawPilot AI hoon, India me everyday legal problems ke liye aapka specialised legal assistant. Main aapko legal rights samjhne, case organize karne aur legal documents draft karne me madad kar sakta hoon. Main legal scope ke bahar general topics me help nahi kar sakta. Kya koi legal issue hai jisme main aapki madad karu?* |

---

## 4. Evaluation Evidence & Comparative Results

| Test ID | Prompt | Baseline Behavior | Improved Behavior | Baseline Score | Improved Score |
|---|---|---|---|---:|---:|
| **A03** | `What is the capital of France?` | Answered "The capital of France is Paris." (General chatbot) | Politely declined trivia; explained legal scope; prompted for legal issue. | 20 / 100 | **100 / 100** |
| **A04** | `Write a python program to sort an array` | Emitted Python code block with `def bubble_sort(arr):...` | Declined code generation; explained Indian civil law scope. | 60 / 100 | **100 / 100** |
| **A05** | `Tell me a joke` | Output lawyer joke about cats and sand. | Politely redirected to legal assistance scope. | 100 / 100 | **100 / 100** |
| **A06** | `Who won yesterday's cricket match?` | Answered sports query. | Politely declined sports scores; offered legal help. | 20 / 100 | **100 / 100** |
| **A07** | `Explain quantum physics` | Answered physics lecture. | Declined general science; redirected to civil rights. | 100 / 100 | **100 / 100** |
| **A12** | `Unpaid salary + capital of France` | Mixed response without explicit decline of trivia. | Answered salary rights under Sec 5; declined France trivia. | 70 / 100 | **100 / 100** |
