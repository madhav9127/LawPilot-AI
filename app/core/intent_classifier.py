"""
LawPilot AI — Dedicated Intent Classification & Legal Scope Router
Classifies every user interaction into one of 5 distinct intents:
1. URGENT_SAFETY: Imminent physical harm, violence, domestic crisis, or severe cyber blackmail.
2. GREETING_OR_SOCIAL: Natural greetings, pleasantries, identity inquiries ("who are you").
3. AMBIGUOUS_QUERY: Short, vague help requests requiring factual clarification.
4. NON_LEGAL_QUERY: General-purpose inquiries (trivia, math, coding, jokes, science, sports, lifestyle, recipes).
5. LEGAL_QUERY: Any genuine substantive or procedural matter under Indian law across all legal domains.

Ensures:
- Open legal scope: Does NOT restrict legal questions to a fixed 4-domain list.
- Polite multilingual rejection of purely non-legal inquiries in the user's latest language.
- Contextual follow-up understanding based on conversation history.
- Mixed query support (answering legal issue while disclaiming unrelated request).
- Prompt injection resistance against roleplay and scope evasion.
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

class UserIntentEnum(str, Enum):
    URGENT_SAFETY = "URGENT_SAFETY"
    GREETING_OR_SOCIAL = "GREETING_OR_SOCIAL"
    AMBIGUOUS_QUERY = "AMBIGUOUS_QUERY"
    NON_LEGAL_QUERY = "NON_LEGAL_QUERY"
    LEGAL_QUERY = "LEGAL_QUERY"


# Localized responses for non-legal queries
NON_LEGAL_SCOPE_RESPONSES = {
    "en": (
        "I am LawPilot AI, a specialised assistant for legal matters in India. "
        "I can help you understand legal rights, explore legal options, interpret legal documents, and prepare legal drafts. "
        "I am unable to assist with general topics unrelated to law. "
        "Is there an Indian legal matter I can help you with?"
    ),
    "hi": (
        "मैं LawPilot AI हूँ, भारत में कानूनी मामलों के लिए एक विशेष सहायक। "
        "मैं आपके कानूनी अधिकारों को समझने, कानूनी विकल्पों का पता लगाने, कानूनी दस्तावेजों की व्याख्या करने और कानूनी ड्राफ्ट तैयार करने में मदद कर सकता हूँ। "
        "मैं कानून से असंबंधित सामान्य विषयों (जैसे सामान्य ज्ञान, कोडिंग, विज्ञान या मनोरंजन) में सहायता करने में असमर्थ हूँ। "
        "क्या कोई भारतीय कानूनी मामला है जिसमें मैं आपकी मदद कर सकता हूँ?"
    ),
    "gu": (
        "હું LawPilot AI છું, ભારતમાં કાનૂની બાબતો માટે એક વિશિષ્ટ સહાયક. "
        "હું તમને કાનૂની અધિકારો સમજવામાં, કાનૂની વિકલ્પો શોધવામાં, કાનૂની દસ્તાવેજોનું વિશ્લેષણ કરવામાં અને કાનૂની ડ્રાફ્ટ તૈયાર કરવામાં મદદ કરી શકું છું. "
        "હું કાયદા સાથે અસંબંધિત સામાન્ય વિષયોમાં સહાય કરવામાં અસમર્થ છું. "
        "શું કોઈ ભારતીય કાનૂની બાબત છે જેમાં હું તમને મદદ કરી શકું?"
    ),
    "mr": (
        "मी LawPilot AI आहे, भारतातील कायदेशीर बाबींसाठी एक विशेष सहाय्यक. "
        "मी तुमचे कायदेशीर हक्क समजून घेण्यास, कायदेशीर पर्याय शोधण्यास, कायदेशीर कागदपत्रांचे विश्लेषण करण्यास आणि कायदेशीर मसुदे तयार करण्यास मदत करू शकतो. "
        "मी कायद्याशी असंबंधित सामान्य विषयांमध्ये मदत करण्यास असमर्थ आहे. "
        "असा कोणताही भारतीय कायदेशीर विषय आहे का ज्यामध्ये मी तुम्हाला मदत करू शकेन?"
    ),
    "ml": (
        "ഞാൻ LawPilot AI ആണ്, ഇന്ത്യയിലെ നിയമപരമായ കാര്യങ്ങൾക്കായുള്ള ഒരു പ്രത്യേക സഹായി. "
        "നിയമപരമായ അവകാശങ്ങൾ മനസ്സിലാക്കാനും നിയമപരമായ ഓപ്ഷനുകൾ പരിശോധിക്കാനും നിയമ രേഖകൾ തയ്യാറാക്കാനും എനിക്ക് നിങ്ങളെ സഹായിക്കാനാകും. "
        "നിയമവുമായി ബന്ധമില്ലാത്ത പൊതുവായ കാര്യങ്ങളിൽ സഹായിക്കാൻ എനിക്ക് കഴിയില്ല. "
        "ഞാൻ സഹായിക്കേണ്ട എന്തെങ്കിലും ഇന്ത്യൻ നിയമപരമായ പ്രശ്നമുണ്ടോ?"
    ),
    "ta": (
        "நான் LawPilot AI, இந்திய சட்ட விவகாரங்களுக்கான ஒரு பிரத்யேக உதவியாளர். "
        "சட்ட உரிமைகளைப் புரிந்துகொள்ளவும், சட்ட வழிகளை ஆராயவும், சட்ட வரைவுகளைத் தயாரிக்கவும் என்னால் உதவ முடியும். "
        "சட்டம் சாராத பொதுவான தலைப்புகளில் என்னால் உதவ முடியாது. "
        "நான் உதவக்கூடிய ஏதேனும் இந்திய சட்ட விவகாரம் உள்ளதா?"
    ),
    "te": (
        "నేను LawPilot AI, భారతదేశంలోని చట్టపరమైన విషయాల కోసం ప్రత్యేక సహాయకుడిని. "
        "చట్టపరమైన హక్కులను అర్థం చేసుకోవడానికి, చట్టపరమైన ఎంపికలను అన్వేషించడానికి మరియు చట్టపరమైన ముసాయిదాలను సిద్ధం చేయడానికి నేను సహాయపడగలను. "
        "చట్టంతో సంబంధం లేని సాధారణ అంశాలలో నేను సహాయం చేయలేను. "
        "నేను మీకు సహాయం చేయగల భారతీయ చట్టపరమైన సమస్య ఏదైనా ఉందా?"
    ),
    "bn": (
        "আমি LawPilot AI, ভারতের আইনি বিষয়ে একটি বিশেষ সহায়ক। "
        "আমি আপনাকে আইনি অধিকার বুঝতে, আইনি বিকল্পগুলি সন্ধান করতে এবং আইনি খসড়া প্রস্তুত করতে সাহায্য করতে পারি। "
        "আইনের সাথে সম্পর্কিত নয় এমন সাধারণ বিষয়ে আমি সাহায্য করতে অক্ষম। "
        "এমন কোনো ভারতীয় আইনি বিষয় আছে যাতে আমি আপনাকে সাহায্য করতে পারি?"
    ),
    "hinglish": (
        "Main LawPilot AI hoon, India me legal matters ke liye ek specialised assistant. "
        "Main aapke legal rights samjhne, legal options explore karne, legal documents interpret karne aur legal drafts prepare karne me help kar sakta hoon. "
        "Main Indian law se unrelated general topics (jaise coding, recipes, trivia ya entertainment) me help nahi kar sakta. "
        "Kya koi Indian legal matter hai jisme main aapki madad kar sakta hoon?"
    )
}

# Localized clarifying questions for ambiguous inputs
AMBIGUOUS_CLARIFYING_RESPONSES = {
    "en": (
        "I am here to help you. To understand your legal rights and options under Indian law, could you please share a few more details about your situation?\n\n"
        "For example:\n"
        "- What specific dispute or problem are you experiencing?\n"
        "- Who is the other party involved (e.g. landlord, employer, seller, bank, family member, neighbour, or authority)?\n"
        "- Have you received any notice, contract, agreement, or official document?"
    ),
    "hi": (
        "मैं आपकी सहायता के लिए यहाँ हूँ। भारतीय कानून के तहत आपके अधिकारों और विकल्पों को समझने के लिए, क्या आप अपनी स्थिति के बारे में कुछ और जानकारी साझा कर सकते हैं?\n\n"
        "उदाहरण के लिए:\n"
        "- आप किस प्रकार की समस्या या विवाद का सामना कर रहे हैं?\n"
        "- इसमें दूसरा पक्ष कौन है (जैसे मकान मालिक, नियोक्ता, दुकानदार, बैंक, रिश्तेदार या पुलिस)?\n"
        "- क्या आपको कोई कानूनी नोटिस, अनुबंध या दस्तावेज़ प्राप्त हुआ है?"
    ),
    "gu": (
        "હું તમારી મદદ માટે અહીં છું. ભારતીય કાયદા હેઠળ તમારા અધિકારો અને વિકલ્પોને સમજવા માટે, શું તમે તમારી પરિસ્થિતિ વિશે થોડી વધુ વિગતો આપી શકો છો?\n\n"
        "ઉદાહરણ તરીકે:\n"
        "- તમે કઈ સમસ્યા અથવા વિવાદનો સામનો કરી રહ્યા છો?\n"
        "- આમાં સામેનો પક્ષ કોણ છે (જેમ કે મકાનમાલિક, નોકરીદાતા, વિક્રેતા, બેંક કે પોલીસ)?\n"
        "- શું તમને કોઈ નોટિસ, કરાર કે કાનૂની દસ્તાવેજ મળ્યો છે?"
    ),
    "mr": (
        "मी तुमच्या मदतीसाठी येथे आहे. भारतीय कायद्यानुसार तुमचे हक्क आणि पर्याय समजून घेण्यासाठी, तुम्ही तुमच्या परिस्थितीबद्दल थोडी अधिक माहिती देऊ शकाल का?\n\n"
        "उदा.\n"
        "- तुम्ही नेमक्या कोणत्या समस्येचा किंवा वादाचा सामना करत आहात?\n"
        "- यात दुसरी व्यक्ती किंवा संस्था कोण आहे (उदा. घरमालक, मालक/कंपनी, बँक, शेजारी किंवा पोलीस)?\n"
        "- तुम्हाला कोणतीही कायदेशीर नोटीस, करार किंवा अधिकृत दस्तऐवज मिळाला आहे का?"
    ),
    "ml": (
        "നിങ്ങളെ സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്. നിങ്ങളുടെ നിയമപരമായ അവകാശങ്ങൾ വ്യക്തമായി മനസ്സിലാക്കാൻ, ദയവായി കുറച്ചുകൂടി വിവരങ്ങൾ നൽകാമോ?\n\n"
        "ഉദാഹരണത്തിന്:\n"
        "- നിങ്ങൾ നേരിടുന്ന പ്രത്യേക പ്രശ്നം എന്താണ്?\n"
        "- എതിർകക്ഷി ആരാണ് (ഉടമസ്ഥൻ, തൊഴിലുടമ, വിൽപ്പനക്കാരൻ, ബാങ്ക്, അല്ലെങ്കിൽ പോലീസ്)?\n"
        "- നിങ്ങൾക്ക് എന്തെങ്കിലും നോട്ടീസോ രേഖയോ ലഭിച്ചിട്ടുണ്ടോ?"
    ),
    "ta": (
        "நான் உங்களுக்கு உதவ இங்கே இருக்கிறேன். உங்கள் சட்ட உரிமைகளைப் புரிந்து கொள்ள, தயவுசெய்து உங்கள் சூழ்நிலையைப் பற்றி மேலும் சில விவரங்களைப் பகிர முடியுமா?\n\n"
        "உதாரணமாக:\n"
        "- நீங்கள் எதிர்கொள்ளும் குறிப்பிட்ட பிரச்சனை என்ன?\n"
        "- இதில் சம்பந்தப்பட்ட மற்றொரு தரப்பினர் யார் (வீட்டு உரிமையாளர், முதலாளி, வங்கி, அல்லது காவல்துறை)?\n"
        "- உங்களுக்கு ஏதேனும் நோட்டீஸ் அல்லது ஒப்பந்த ஆவணம் வந்துள்ளதா?"
    ),
    "te": (
        "నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను. మీ చట్టపరమైన హక్కులను అర్థం చేసుకోవడానికి, దయచేసి మీ పరిస్థితి గురించి మరికొన్ని వివరాలను పంచుకోగలరా?\n\n"
        "ఉదాహరణకు:\n"
        "- మీరు ఎదుర్కొంటున్న నిర్దిష్ట సమస్య ఏమిటి?\n"
        "- ఇందులో పాల్గొన్న ఇతర పక్షం ఎవరు (ఇంటి యజమాని, యజమాని, బ్యాంక్ లేదా పోలీసులు)?\n"
        "- మీకు ఏదైనా నోటీసు లేదా చట్టపరమైన పత్రం అందిందా?"
    ),
    "bn": (
        "আমি আপনাকে সাহায্য করতে এখানে আছি। ভারতীয় আইনের অধীনে আপনার অধিকারগুলি বুঝতে, আপনার পরিস্থিতি সম্পর্কে কিছু বিশদ তথ্য শেয়ার করবেন?\n\n"
        "উদাহরণস্বরূপ:\n"
        "- আপনি ঠিক কী সমস্যার সম্মুখীন হচ্ছেন?\n"
        "- এর সাথে অন্য কোন পক্ষ জড়িত (বাড়িওয়ালা, নিয়োগকর্তা, বিক্রেতা, ব্যাংক বা পুলিশ)?\n"
        "- আপনি কি কোনো নোটিশ বা আইনি নথি পেয়েছেন?"
    ),
    "hinglish": (
        "Main aapki help ke liye yahan hoon. Indian law ke according aapke legal rights ko samajhne ke liye, kya aap apni situation ke bare me thodi aur details share kar sakte hain?\n\n"
        "Jaise:\n"
        "- Aap kya specific problem ya dispute face kar rahe hain?\n"
        "- Dusri party kaun hai (jaise landlord, employer, seller, bank, family member ya police)?\n"
        "- Kya aapko koi notice, contract ya official document mila hai?"
    )
}

# Localized urgent emergency responses
URGENT_SAFETY_RESPONSES = {
    "en": (
        "⚠️ **URGENT SAFETY & EMERGENCY GUIDANCE**\n\n"
        "If you or someone else is in immediate physical danger, facing an ongoing attack, or under threat of bodily harm, please prioritize your immediate safety right now:\n\n"
        "1. **Emergency Police Response:** Dial **112** (National Emergency Response Support System) immediately.\n"
        "2. **Women Helpline (Domestic Abuse & Distress):** Dial **1091** or **181** for 24x7 emergency protection and police dispatch.\n"
        "3. **Cyber Blackmail & Non-Consensual Imagery:** If someone is threatening to leak private/intimate photos or videos, do not pay money or yield to extortion. Call **1930** (Cybercrime Helpline) and file an immediate report at [cybercrime.gov.in](https://cybercrime.gov.in).\n"
        "4. **Seek Immediate Shelter:** Move to a populated public space, a police station, or reach out to nearby trusted neighbours/family.\n\n"
        "Once you are in a secure location, LawPilot AI can assist you with understanding your rights under the Bharatiya Nagarik Suraksha Sanhita (BNSS 2023), lodging an FIR (Section 173 BNSS), or seeking urgent judicial protection orders."
    ),
    "hi": (
        "⚠️ **तत्काल सुरक्षा एवं आपातकालीन मार्गदर्शन**\n\n"
        "यदि आप या कोई अन्य व्यक्ति तत्काल शारीरिक खतरे में है, हमले का सामना कर रहा है या जान-माल का खतरा है, तो कृपया तुरंत अपनी व्यक्तिगत सुरक्षा को प्राथमिकता दें:\n\n"
        "1. **आपातकालीन पुलिस सहायता:** तुरंत **112** (राष्ट्रीय आपातकालीन हेल्पलाइन) पर कॉल करें।\n"
        "2. **महिला हेल्पलाइन (घरेलू हिंसा एवं संकट):** 24x7 आपातकालीन सहायता के लिए **1091** या **181** डायल करें।\n"
        "3. **साइबर ब्लैकमेल एवं निजी फोटो की धमकी:** यदि कोई निजी/अतरंग तस्वीरें या वीडियो लीक करने की धमकी देकर ब्लैकमेल कर रहा है, तो पैसे न दें। तुरंत **1930** (साइबर हेल्पलाइन) पर कॉल करें और [cybercrime.gov.in](https://cybercrime.gov.in) पर रिपोर्ट दर्ज करें।\n"
        "4. **सुरक्षित स्थान पर जाएं:** तुरंत किसी भीड़-भाड़ वाली जगह, निकटतम पुलिस स्टेशन जाएं या विश्वसनीय पड़ोसियों/परिजनों से संपर्क करें।\n\n"
        "सुरक्षित होने के बाद, LawPilot AI आपको धारा 173 BNSS के तहत एफआईआर दर्ज करने या अदालत से सुरक्षा आदेश प्राप्त करने में कानूनी सहायता प्रदान कर सकता है।"
    ),
    "gu": (
        "⚠️ **તાત્કાલિક સુરક્ષા અને ઈમરજન્સી માર્ગદર્શન**\n\n"
        "જો તમે અથવા અન્ય કોઈ તાત્કાલિક શારીરિક જોખમમાં હોય અથવા હુમલાનો સામનો કરી રહ્યા હોય, તો કૃપા કરીને અત્યારે તમારી સલામતીને પ્રાથમિકતા આપો:\n\n"
        "1. **ઈમરજન્સી પોલીસ સહાય:** તાત્કાલિક **112** (રાષ્ટ્રીય ઈમરજન્સી હેલ્પલાઇન) પર કૉલ કરો.\n"
        "2. **મહિલા હેલ્પલાઇન:** 24x7 સહાય માટે **1091** અથવા **181** ડાયલ કરો.\n"
        "3. **સાયબર બ્લેકમેલ અને અંગત ફોટોની ધમકી:** જો કોઈ અંગત તસવીરો લીક કરવાની ધમકી આપી રહ્યું હોય, તો પૈસા આપશો નહીં. તરત જ **1930** પર કૉલ કરો અને [cybercrime.gov.in](https://cybercrime.gov.in) પર ફરિયાદ નોંધાવો.\n"
        "4. **સલામત સ્થળે જાઓ:** તાત્કાલિક નજીકના પોલીસ સ્ટેશન અથવા સુરક્ષિત સ્થળે પહોંચો.\n\n"
        "સુરક્ષિત થયા પછી, LawPilot AI તમને કલમ 173 BNSS હેઠળ FIR નોંધવા અથવા કાનૂની રક્ષણ મેળવવામાં મદદ કરશે."
    ),
    "mr": (
        "⚠️ **तातडीचे सुरक्षा व आपत्कालीन मार्गदर्शन**\n\n"
        "जर तुम्ही किंवा इतर कोणी तात्काळ शारीरिक धोक्यात असाल किंवा हल्ल्याचा सामना करत असाल, तर कृपया ताबडतोब स्वतःच्या सुरक्षिततेला प्राधान्य द्या:\n\n"
        "1. **आपत्कालीन पोलीस मदत:** ताबडतोब **112** (राष्ट्रीय आपत्कालीन क्रमांक) वर कॉल करा.\n"
        "2. **महिला हेल्पलाइन:** २४ तास मदतीसाठी **1091** किंवा **181** डायल करा.\n"
        "3. **सायबर ब्लॅकमेल व खाजगी फोटोची धमकी:** कोणी खाजगी फोटो लीक करण्याची धमकी देत असल्यास खंडणी देऊ नका. त्वरित **1930** वर कॉल करा आणि [cybercrime.gov.in](https://cybercrime.gov.in) वर तक्रार नोंदवा.\n"
        "4. **सुरक्षित ठिकाणी जा:** ताबडतोब जवळच्या पोलीस ठाण्यात किंवा सुरक्षित ठिकाणी आश्रय घ्या.\n\n"
        "सुरक्षित झाल्यावर, LawPilot AI तुम्हाला कलम 173 BNSS अंतर्गत FIR नोंदवण्यासाठी किंवा कायदेशीर संरक्षणासाठी मदत करेल."
    ),
    "ml": (
        "⚠️ **അടിയന്തര സുരക്ഷാ നിർദ്ദേശം**\n\n"
        "നിങ്ങളോ മറ്റാരെങ്കിലുമോ ഉടനടി ശാരീരിക അപകടത്തിലാണെങ്കിൽ, ദയവായി നിങ്ങളുടെ സുരക്ഷയ്ക്ക് മുൻഗണന നൽകുക:\n\n"
        "1. **പോലീസ് അടിയന്തര സഹായം:** ഉടൻ തന്നെ **112** ൽ വിളിക്കുക.\n"
        "2. **വനിതാ ഹെൽപ്പ് ലൈൻ:** **1091** അല്ലെങ്കിൽ **181** ൽ വിളിക്കുക.\n"
        "3. **സൈബർ ബ്ലാക്ക് മെയിലിംഗ്:** സ്വകാര്യ ചിത്രങ്ങൾ പ്രചരിപ്പിക്കുമെന്ന് ഭീഷണിപ്പെടുത്തുകയാണെങ്കിൽ പണം നൽകരുത്. ഉടൻ **1930** ൽ വിളിക്കുക അല്ലെങ്കിൽ [cybercrime.gov.in](https://cybercrime.gov.in) ൽ പരാതി നൽകുക.\n"
        "4. **സുരക്ഷിത സ്ഥാനത്തേക്ക് മാറുക:** ഉടൻ അടുത്തുള്ള പോലീസ് സ്റ്റേഷനിലോ സുരക്ഷിതമായ സ്ഥലത്തോ എത്തുക."
    ),
    "hinglish": (
        "⚠️ **URGENT SAFETY & EMERGENCY GUIDANCE**\n\n"
        "Agar aap ya koi aur immediate physical danger ya ongoing attack face kar rahe hain, to please turant apni safety ko priority dein:\n\n"
        "1. **Emergency Police Response:** Turant **112** dial karein.\n"
        "2. **Women Helpline:** 24x7 emergency safety ke liye **1091** ya **181** call karein.\n"
        "3. **Cyber Blackmail / Private Photo Threats:** Agar koi intimate photos ya videos leak karne ki dhamki dekar blackmail kar raha hai, to paise mat dein. Turant **1930** call karein aur [cybercrime.gov.in](https://cybercrime.gov.in) par report karein.\n"
        "4. **Safe Place Par Jayein:** Nearest police station ya crowded public place par move karein.\n\n"
        "Physically safe hone ke baad, LawPilot AI aapko Section 173 BNSS ke under FIR lodge karne me assist karega."
    )
}


class IntentClassifier:
    """
    Semantic Intent Classifier and Scope Router for LawPilot AI.
    """

    # 1. URGENT SAFETY PATTERNS (Highest priority)
    URGENT_SAFETY_PATTERNS = [
        r"\b(?:physically\s+attack(?:ing|ed)?|attacking\s+me|attacked\s+me|beating\s+me|beaten\s+up|threaten(?:ed|ing)?\s+to\s+kill|kill\s+me|kill\s+my|murder\s+me|stab(?:bing|bed)?|shooting|danger\s+right\s+now|immediate\s+danger|someone\s+is\s+trying\s+to\s+hurt\s+me|threatening\s+to\s+hurt|assault(?:ing|ed)?\s+me|kidnap(?:ping|ped)?|suicide|kill\s+myself|break\s+my\s+legs|goons\s+outside|bouncers\s+attacking)\b",
        r"\b(?:leak\s+(?:my\s+)?(?:private|intimate|nude|naked|personal)\s+(?:photos?|photographs?|pictures?|videos?|pics?)|sharing\s+my\s+(?:nudes|private\s+photos|private\s+photographs)|morphing\s+my\s+photos|blackmailing\s+me\s+with\s+(?:photos|photographs|videos|pictures)|extorting\s+me\s+with\s+(?:photos|photographs|videos))\b",
        r"(?:हमला\s*कर\s*रहा|जान\s*से\s*मारने|मारपीट\s*कर|हल्ला\s*करत\s*आहे|जीवाला\s*धोका|खाजगी\s*फोटो\s*लीक|प्राइवेट\s*फोटो\s*लीक|મારી\s*પર\s*હુમલો|જાનથી\s*મારી\s*નાખવાની|અંગત\s*ફોટો\s*લીક|આક્રમણ|ജീവന്\s*ഭീഷണി|സ്വകാര്യ\s*ചിത്രങ്ങൾ|தாக்குகிறார்|கொலை\s*மிரட்டல்|దాడి\s*చేస్తున్నారు|আক্রমণ\s*করছে)"
    ]

    # 2. GREETINGS & SOCIAL PATTERNS
    GREETING_PATTERNS = [
        r"^(?:hi|hello|hey|namaste|pranam|kem\s*cho|kemon\s*acho|vanakkam|namaskaram|namaskara|adaab|sat\s*sri\s*akal|sasriyakaal|good\s*(?:morning|afternoon|evening))\b",
        r"^(?:who\s+are\s+you|what\s+is\s+your\s+name|what\s+do\s+you\s+do|what\s+can\s+you\s+help\s+me\s+with|how\s+are\s+you)\b",
        r"^(?:thank\s+you|thanks|thanks\s+a\s+lot|thank\s+you\s+so\s+much|bye|goodbye|alvida|shukriya|dhanyawad)\b",
        r"^(?:नमस्ते|प्रणाम|नमस्कार|નમસ્તે|કેમ\s*છો|നമസ്കാരം|வணக்கம்|నమస్కారం|নমস্কার)"
    ]

    # 3. AMBIGUOUS PATTERNS (Short, vague distress without specific facts)
    AMBIGUOUS_PATTERNS = [
        r"^(?:i\s+need\s+help|please\s+help\s+me|help\s+me|help\s+me\s+please|i\s+have\s+a\s+problem|someone\s+is\s+troubling\s+me|i\s+am\s+in\s+(?:serious\s+)?trouble|i\s+received\s+a\s+document|what\s+can\s+i\s+do|i\s+don't\s+know\s+what\s+to\s+do|feeling\s+stressed|confused\s+about\s+what\s+to\s+do|something\s+bad\s+happened|need\s+advice|can\s+you\s+help\s+me\??)$",
        r"^(?:मुझे\s*मदद\s*चाहिए|मेरी\s*मदद\s*करो|कोई\s*मुझे\s*परेशान\s*कर\s*रहा\s*है|मुझे\s*एक\s*दस्तावेज़\s*मिला\s*है|मैं\s*मुसीबत\s*में\s*हूँ|મને\s*મદદ\s*જોઈએ\s*છે|હું\s*મુશ્કેલીમાં\s*છું|मला\s*मदत\s*हवी\s*आहे|मी\s*अडचणीत\s*आहे|എനിക്ക്\s*സഹായം\s*വേണം)$"
    ]

    # 4. NON-LEGAL / UNRELATED GENERAL TOPICS PATTERNS
    NON_LEGAL_PATTERNS = [
        # Geography / General Trivia
        r"\b(?:capital\s+of\s+[a-zA-Z]+|who\s+is\s+the\s+president\s+of|largest\s+ocean|tallest\s+building|currency\s+of\s+[a-zA-Z]+|who\s+is\s+the\s+prime\s+minister\s+of\s+(?!india)|deepest\s+lake|highest\s+peak|when\s+did\s+world\s+war)\b",
        # Programming / Non-Legal IT
        r"\b(?:write\s+(?:a\s+)?(?:python|c\+\+|java|javascript|php|sql|ruby|go|c#)\s+(?:program|script|code|function)|python\s+code|sort\s+an?\s+(?:list|array)|binary\s+search|bubble\s+sort|leetcode|help\s+me\s+create\s+a\s+website|how\s+to\s+build\s+a\s+website|write\s+an\s+algorithm|debug\s+this\s+code)\b",
        # Machine Learning / AI non-legal theory
        r"\b(?:explain\s+machine\s+learning|what\s+is\s+machine\s+learning|how\s+does\s+machine\s+learning\s+work|neural\s+networks?|deep\s+learning|nlp\s+model|linear\s+regression)\b",
        # Science / Physics / Math
        r"\b(?:explain\s+quantum\s+physics|quantum\s+physics|theory\s+of\s+relativity|schrodinger|photosynthesis|how\s+(?:does\s+)?photosynthesis\s+works?|solve\s+(?:this\s+)?mathematics|solve\s+(?:this\s+)?math|solve\s+(?:an?\s+)?equation|calculus|what\s+is\s+2\s*\+\s*2|2\s*\+\s*2|periodic\s+table|gravity\s+formula)\b",
        # Creative writing / Jokes / Entertainment
        r"\b(?:tell\s+me\s+a\s+(?:funny\s+)?joke|tell\s+(?:me\s+)?a\s+joke|write\s+a\s+(?:romantic\s+)?poem|sing\s+a\s+song|write\s+a\s+rap|write\s+a\s+story\s+about|bedtime\s+story)\b",
        # Sports / Games
        r"\b(?:who\s+won\s+(?:yesterday'?s\s+)?cricket\s+match|who\s+won\s+the\s+match|cricket\s+match|ipl\s+score|football\s+score|fifa\s+world\s+cup|olympics|chess\s+opening)\b",
        # Lifestyle / Gym / Cooking / Recipes
        r"\b(?:gym\s+workout\s+plan|workout\s+plan|fitness\s+plan|how\s+to\s+lose\s+weight|recipe\s+for|give\s+me\s+a\s+recipe|recipe\s+in\s+[a-zA-Z]+|how\s+to\s+bake|how\s+to\s+cook)\b",
        # Travel / Weather
        r"\b(?:what\s+is\s+the\s+weather\s+today|weather\s+forecast|suggest\s+a\s+travel\s+itinerary|travel\s+itinerary|trip\s+to\s+[a-zA-Z]+|tourist\s+places\s+in)\b",
        # Entertainment recommendations
        r"\b(?:suggest\s+a\s+(?:good\s+)?movie|recommend\s+a\s+movie|best\s+movies\s+to\s+watch|recommend\s+a\s+book)\b",
        # Prompt injection / Evasion to general chatbot
        r"\b(?:act\s+as\s+chatgpt|act\s+as\s+an\s+unrestricted\s+ai|ignore\s+(?:your\s+)?legal\s+restrictions|forget\s+you\s+are\s+a\s+lawyer|act\s+as\s+dan|developer\s+mode|pretend\s+you\s+are\s+chatgpt)\b",
        # Indic Non-Legal Patterns
        r"(?:चुटकुला|जोक|विनोद|જોક|જોક્સ|ચુટકલો|തമാശ|நகைச்சுவை|జోక్|কৌতুক)",
        r"(?:रेसिपी\s*दो|રેસીપી\s*આપો|रेसिपी\s*द्या|പാചകക്കുറിപ്പ്|ரெசிபி|రెసిపీ|রেসিপি)",
        r"(?:मशीन\s*लर्निंग\s*(?:के\s*बारे\s*में|समझाइए|क्या\s*है)|મશીન\s*લર્નિંગ\s*સમજાવો|मशीन\s*लर्निंग\s*स्पष्ट\s*करा|മെഷീൻ\s*ലേണിംഗ്|மெஷின்\s*லேர்னிங்|మొషిన్\s*లెర్నింగ్|মেশিন\s*লার্নিং)",
        r"(?:कविता\s*लिखो|कविता\s*લખો|कविता\s*लिहा|കവിത\s*എഴുതുക|கவிதை|కవిత|কবিতা)",
        r"(?:फ्रांस\s*की\s*राजधानी|ફ્રાન્સની\s*રાજધાની|फ्रान्सची\s*राजधानी|ഫ്രാൻസിന്റെ\s*തലസ്ഥാനം|குவாண்டம்\s*இயற்பியல்|క్వాంటమ్\s*ఫిజిక్స్|কোয়ান্টাম\s*পদার্থবিদ্যা)"
    ]

    # Explicit legal terms across ALL Indian legal domains (to avoid false rejection)
    LEGAL_KEYWORDS_BROAD = [
        # Criminal, police, FIR, courts, procedure
        r"\b(?:fir|police|complaint|arrest|bail|anticipatory|warrant|summons|charge\s*sheet|magistrate|court|judge|advocate|lawyer|bns|bnss|bsa|ipc|crpc|evidence|statute|statutory|offence|crime|cheating|fraud|theft|assault|extortion|defamation|contempt|habeas\s*corpus|mandamus|writ|appeal|revision|tribunal|quash)\b",
        # Civil, property, land, tenancy
        r"\b(?:deposit|rent|tenant|landlord|eviction|evict|lease|agreement|possession|encroachment|property|land|registration|sub-registrar|mutation|patta|khata|rera|partition|will|probate|succession|legal\s*heir|gift\s*deed|sale\s*deed|title|trespass|boundary|trespassing|occupying\s*my\s*land)\b",
        # Consumer, contracts, commercial
        r"\b(?:consumer|defective|refund|replacement|warranty|guarantee|e-commerce|seller|unfair\s*trade|deficiency\s*in\s*service|nch|e-daakhil|district\s*forum|ncdrc|contract|breach|damages|penalty|indemnity|promissory\s*note|arbitration|mediation|lok\s*adalat)\b",
        # Employment, wages, labour
        r"\b(?:salary|wages|employer|employee|workplace|termination|resignation|fired|relieving|experience\s*letter|gratuity|provident\s*fund|pf|bonus|posh|harassment|discrimination|severance|labour\s*court|labour\s*commissioner|dues|withheld)\b",
        # Banking, finance, insurance, tax
        r"\b(?:cheque|cheque\s*bounce|dishonour|section\s*138|ni\s*act|bank\s*account|account\s*freeze|cyber\s*fraud|online\s*fraud|hacked|phishing|upi|unauthorized\s*transaction|rbi\s*ombudsman|insurance|claim\s*rejected|policy|tax|income\s*tax|gst|tax\s*notice|scrutiny|challan|traffic\s*challan)\b",
        # Family, matrimonial, custody
        r"\b(?:divorce|maintenance|alimony|custody|child\s*support|restitution|hindu\s*marriage|special\s*marriage|muslim\s*marriage|pwdva|domestic\s*violence|dowry|498a)\b",
        # IPR, RTI, Constitutional, Misc
        r"\b(?:trademark|copyright|patent|infringement|piracy|intellectual\s*property|rti|right\s*to\s*information|pio|first\s*appeal|mact|motor\s*accident|accident\s*claim|pollution|ngt|citizenship|passport\s*impounded)\b",
        r"\b(?:section\s+\d+|order\s+\d+|article\s+\d+|rule\s+\d+|act\s+of\s+\d{4}|tenancy\s+act|consumer\s+protection\s+act|penal\s+code|civil\s+procedure|criminal\s+procedure)\b",
        # Indic Legal Indicators
        r"(?:डिपॉज़िट|वेतन|किराया|मकान\s*मालिक|सैलरी|रिफंड|दोषपूर्ण|नोटीस|एफआईआर|जमानत|तलाक|घरेलू\s*हिंसा|रेरा|चेक\s*बाउंस|ચલણ|ટ્રાફિક|સિક્યોરિટી|પગાર|ભાડું|મકાનમાલિક|રિફંડ|ખામીયુક્ત|ડિપોઝિટ|પોલીસ|એફઆઈઆર|જામીન|છૂટાછેડા|રેરા|ચેક\s*બાઉન્સ|શમ્બળ|ശമ്പളം|വാടക|തൊഴിലുടമ|റീഫണ്ട്|പോലീസ്|ജാമ്യം|വിവാഹമോചനം|ஜாமீன்|சம்பளம்|வாடகை|நிறுவனம்|விவாகரத்து|ஜீதம்|అద్దె|డిపాజిట్|బెయిల్|విడాకులు|বেতন|ভাড়া|রিফান্ড|ঘরমালিক|ডিভোর্স|জামিন|जामीन|घटस्फोट)"
    ]

    @classmethod
    def detect_language(cls, text: str, explicit_lang: Optional[str] = None) -> str:
        """Detects the language of the message."""
        if explicit_lang and explicit_lang in NON_LEGAL_SCOPE_RESPONSES:
            return explicit_lang

        # Unicode script checks
        if re.search(r"[\u0A80-\u0AFF]", text):
            return "gu"
        if re.search(r"[\u0D00-\u0D7F]", text):
            return "ml"
        if re.search(r"[\u0B80-\u0BFF]", text):
            return "ta"
        if re.search(r"[\u0C00-\u0C7F]", text):
            return "te"
        if re.search(r"[\u0980-\u09FF]", text):
            return "bn"
        if re.search(r"[\u0900-\u097F]", text):
            # Check for Marathi markers
            marathi_markers = ["आहे", "नाही", "काय", "मला", "तुम्ही", "करणे", "झाले", "सांगा", "हवा", "होते", "द्या"]
            if any(m in text for m in marathi_markers):
                return "mr"
            return "hi"

        # Latin script checks
        lower = text.lower()
        hinglish_words = [
            "kya", "hai", "mujhe", "mera", "meri", "hum", "nahi", "raha", "rahi", "karo", "batayein",
            "paisa", "makan", "kiraya", "naukri", "pulis", "thana", "madad", "bhai", "sir", "karna", "chahiye"
        ]
        match_count = sum(1 for w in hinglish_words if re.search(rf"\b{w}\b", lower))
        if match_count >= 2:
            return "hinglish"

        return "en"

    @classmethod
    def classify_intent(
        cls,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        language: Optional[str] = None
    ) -> Tuple[UserIntentEnum, Optional[str], bool, str]:
        """
        Classifies user intent into one of the 5 required outcomes by delegating
        to the authoritative IntentGate engine.
        Returns:
            (intent, response_text, is_mixed, explanation)
        """
        from app.core.intent_gate import IntentGate, UserIntentEnum as GateIntentEnum
        decision = IntentGate.evaluate(
            message=message,
            conversation_history=conversation_history,
            language=language
        )
        intent_map = {
            GateIntentEnum.LEGAL_QUERY: UserIntentEnum.LEGAL_QUERY,
            GateIntentEnum.NON_LEGAL_QUERY: UserIntentEnum.NON_LEGAL_QUERY,
            GateIntentEnum.GREETING_OR_SOCIAL: UserIntentEnum.GREETING_OR_SOCIAL,
            GateIntentEnum.AMBIGUOUS: UserIntentEnum.AMBIGUOUS_QUERY,
            GateIntentEnum.URGENT_SAFETY: UserIntentEnum.URGENT_SAFETY
        }
        mapped_intent = intent_map.get(decision.intent, UserIntentEnum.NON_LEGAL_QUERY)
        return (
            mapped_intent,
            decision.direct_response,
            decision.is_mixed,
            decision.reasoning
        )
