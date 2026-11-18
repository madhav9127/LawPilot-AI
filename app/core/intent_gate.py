"""
LawPilot AI — Dedicated Backend-Level Semantic Intent Gate & Scope Router

Enforces strict product boundaries:
- Comprehensive Indian Legal Scope (All domains of Indian law: civil, criminal, constitutional,
  family, property, consumer, employment, cyber, banking, tax, IPR, insurance, motor accident, etc.)
- Strict Exclusion of General-Purpose Topics (programming, math, science, entertainment, recipes,
  general trivia, lifestyle, DIY/plumbing, world history, product buying, athletics, etc.)
- Multi-Turn Context-Aware Topic Disentanglement (prevents legal context contamination)
- Fail-Safe Architecture (never defaults uncertain queries to LEGAL_QUERY)
"""

import os
import re
import json
import uuid
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger("lawpilot.intent_gate")

class UserIntentEnum(str, Enum):
    LEGAL_QUERY = "LEGAL_QUERY"
    NON_LEGAL_QUERY = "NON_LEGAL_QUERY"
    GREETING_OR_SOCIAL = "GREETING_OR_SOCIAL"
    AMBIGUOUS = "AMBIGUOUS"
    URGENT_SAFETY = "URGENT_SAFETY"


@dataclass
class IntentDecision:
    intent: UserIntentEnum
    confidence: float
    is_mixed: bool
    context_influenced: bool
    topic_changed: bool
    detected_language: str
    reasoning: str
    direct_response: Optional[str] = None
    rag_invoked: bool = False
    legal_generation_invoked: bool = False


# Standard Non-Legal Scope Refusals across languages (Section 7 specification)
STANDARD_NON_LEGAL_RESPONSES = {
    "en": (
        "I am LawPilot AI, an assistant specialising in everyday legal problems in India. "
        "I can help you understand your legal rights, organise your case, identify possible options and prepare legal documents. "
        "I cannot assist with general topics outside my legal-assistance scope. "
        "Is there a legal issue I can help you with?"
    ),
    "hi": (
        "मैं LawPilot AI हूँ, भारत में कानूनी मामलों के लिए एक विशेष सहायक। "
        "मैं आपके कानूनी अधिकारों को समझने, कानूनी विकल्पों का पता लगाने, कानूनी दस्तावेजों की व्याख्या करने और कानूनी ड्राफ्ट तैयार करने में मदद कर सकता हूँ। "
        "मैं कानून से असंबंधित सामान्य विषयों में सहायता नहीं कर सकता। "
        "क्या कोई कानूनी मामला है जिसमें मैं आपकी मदद कर सकता हूँ?"
    ),
    "gu": (
        "હું LawPilot AI છું, ભારતમાં કાનૂની બાબતો માટે એક વિશિષ્ટ સહાયક. "
        "હું તમને કાનૂની અધિકારો સમજવામાં, કાનૂની વિકલ્પો શોધવામાં, કાનૂની દસ્તાવેજોનું અર્થઘટન કરવામાં અને કાનૂની ડ્રાફ્ટ તૈયાર કરવામાં મદદ કરી શકું છું. "
        "હું કાયદા સાથે અસંબંધિત સામાન્ય વિષયોમાં સહાય કરી શકતો નથી. "
        "શું કોઈ કાનૂની બાબત છે જેમાં હું તમને મદદ કરી શકું?"
    ),
    "mr": (
        "मी LawPilot AI आहे, भारतातील कायदेशीर बाबींसाठी एक विशेष सहाय्यक. "
        "मी तुमचे कायदेशीर हक्क समजून घेण्यास, कायदेशीर पर्याय शोधण्यास, कायदेशीर कागदपत्रांचे विश्लेषण करण्यास आणि कायदेशीर मसुदे तयार करण्यास मदत करू शकतो. "
        "मी कायद्याशी असंबंधित सामान्य विषयांमध्ये मदत करू शकत नाही. "
        "असा कोणताही कायदेशीर विषय आहे का ज्यामध्ये मी तुम्हाला मदत करू शकेन?"
    ),
    "ml": (
        "ഞാൻ LawPilot AI ആണ്, ഇന്ത്യയിലെ നിയമപരമായ കാര്യങ്ങൾക്കായുള്ള ഒരു പ്രത്യേക സഹായി. "
        "നിയമപരമായ അവകാശങ്ങൾ മനസ്സിലാക്കാനും നിയമപരമായ ഓപ്ഷനുകൾ പരിശോധിക്കാനും രേഖകൾ തയ്യാറാക്കാനും എനിക്ക് നിങ്ങളെ സഹായിക്കാനാകും. "
        "നിയമവുമായി ബന്ധമില്ലാത്ത പൊതുവായ വിഷയങ്ങളിൽ സഹായിക്കാൻ എനിക്ക് കഴിയില്ല. "
        "ഞാൻ സഹായിക്കേണ്ട എന്തെങ്കിലും നിയമപരമായ കാര്യമുണ്ടോ?"
    ),
    "ta": (
        "நான் LawPilot AI, இந்திய சட்ட விவகாரங்களுக்கான ஒரு பிரத்யேக உதவியாளர். "
        "சட்ட உரிமைகளைப் புரிந்துகொள்ளவும், சட்ட வழிகளை ஆராயவும், சட்ட வரைவுகளைத் தயாரிக்கவும் என்னால் உதவ முடியும். "
        "சட்டம் சாராத பொதுவான தலைப்புகளில் என்னால் உதவ முடியாது. "
        "நான் உதவக்கூடிய ஏதேனும் சட்ட விவகாரம் உள்ளதா?"
    ),
    "te": (
        "నేను LawPilot AI, భారతదేశంలోని చట్టపరమైన విషయాల కోసం ప్రత్యేక సహాయకుడిని. "
        "చట్టపరమైన హక్కులను అర్థం చేసుకోవడానికి, చట్టపరమైన ఎంపికలను అన్వేషించడానికి మరియు చట్టపరమైన ముసాయిదాలను సిద్ధం చేయడానికి నేను సహాయపడగలను. "
        "చట్టంతో సంబంధం లేని సాధారణ అంశాలలో నేను సహాయం చేయలేను. "
        "నేను మీకు సహాయం చేయగల చట్టపరమైన సమస్య ఏదైనా ఉందా?"
    ),
    "bn": (
        "আমি LawPilot AI, ভারতের আইনি বিষয়ে একটি বিশেষ সহায়ক। "
        "আমি আপনাকে আইনি অধিকার বুঝতে, আইনি বিকল্পগুলি সন্ধান করতে এবং আইনি খসড়া প্রস্তুত করতে সাহায্য করতে পারি। "
        "আইনের সাথে সম্পর্কিত নয় এমন সাধারণ বিষয়ে আমি সাহায্য করতে পারি না। "
        "এমন কোনো আইনি বিষয় আছে যাতে আমি আপনাকে সাহায্য করতে পারি?"
    ),
    "hinglish": (
        "Main LawPilot AI hoon, India me legal matters ke liye ek specialised assistant. "
        "Main aapke legal rights samjhne, legal options explore karne, legal documents interpret karne aur legal drafts prepare karne me help kar sakta hoon. "
        "Main law se unrelated general topics me help nahi kar sakta. "
        "Kya koi legal issue hai jisme main aapki help kar sakta hoon?"
    )
}


# Clarification for generic drafting inquiries
DRAFTING_INQUIRY_RESPONSES = {
    "en": (
        "I can help you draft formal legal notices, complaint letters, demand notices, and legal communications in India. "
        "What kind of letter do you need to draft, and does it concern a tenancy dispute, unpaid salary, consumer grievance, or another legal matter?"
    ),
    "hi": (
        "मैं भारत में औपचारिक कानूनी नोटिस, शिकायत पत्र, मांग पत्र और कानूनी पत्राचार तैयार करने में आपकी मदद कर सकता हूँ। "
        "आपको किस प्रकार का पत्र तैयार करना है, और क्या यह किरायेदारी विवाद, बकाया वेतन, उपभोक्ता शिकायत, या किसी अन्य कानूनी मामले से संबंधित है?"
    ),
    "gu": (
        "હું ભારતમાં ઔપચારિક કાનૂની નોટિસ, ફરિયાદ પત્ર, માંગણી પત્ર અને કાનૂની પત્રવ્યવહાર તૈયાર કરવામાં તમારી મદદ કરી શકું છું. "
        "તમારે કયા પ્રકારનો પત્ર તૈયાર કરવો છે, અને શું તે ભાડૂઆત વિવાદ, બાકી પગાર, ગ્રાહક ફરિયાદ કે અન્ય કોઈ કાનૂની બાબત સાથે સંબંધિત છે?"
    ),
    "mr": (
        "मी भारतात औपचारिक कायदेशीर नोटीस, तक्रार अर्ज, मागणी पत्र आणि कायदेशीर पत्रव्यवहार तयार करण्यास मदत करू शकतो. "
        "तुम्हाला कोणत्या प्रकारचे पत्र तयार करायचे आहे, आणि ते भाडेकरू वाद, थकीत वेतन, ग्राहक तक्रार किंवा इतर कोणत्याही कायदेशीर बाबीशी संबंधित आहे का?"
    ),
    "hinglish": (
        "Main India me formal legal notice, complaint letter, demand notice aur legal communications draft karne me help kar sakta hoon. "
        "Aapko kis tarah ka letter draft karna hai, aur kya ye tenancy dispute, unpaid salary, consumer grievance ya kisi doosre legal matter se related hai?"
    )
}

# Ambiguous Clarification Requests across languages
AMBIGUOUS_CLARIFICATION_RESPONSES = {
    "en": (
        "I am here to help. To understand whether your situation involves an Indian legal matter and what rights apply, "
        "could you please share a few more details about the dispute or problem you are experiencing?"
    ),
    "hi": (
        "मैं आपकी सहायता के लिए यहाँ हूँ। आपकी स्थिति में कौन से भारतीय कानूनी अधिकार और उपाय लागू होते हैं, "
        "यह समझने के लिए क्या आप अपनी समस्या या विवाद के बारे में कुछ और विवरण साझा कर सकते हैं?"
    ),
    "gu": (
        "હું તમારી મદદ માટે અહીં છું. તમારી પરિસ્થિતિમાં કયા કાનૂની અધિકારો અને વિકલ્પો લાગુ પડે છે તે સમજવા માટે, "
        "શું તમે તમારી સમસ્યા કે વિવાદ વિશે થોડી વધુ વિગતો શેર કરી શકો છો?"
    ),
    "mr": (
        "मी तुमच्या मदतीसाठी येथे आहे. तुमच्या परिस्थितीत कोणते कायदेशीर हक्क आणि पर्याय लागू होतात हे समजून घेण्यासाठी, "
        "तुम्ही तुमच्या समस्येबद्दल किंवा वादाबद्दल थोडी अधिक माहिती देऊ शकाल का?"
    ),
    "ml": (
        "നിങ്ങളെ സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്. നിങ്ങളുടെ സാഹചര്യത്തിൽ എന്തെല്ലാം നിയമപരമായ അവകാശങ്ങളാണ് ഉള്ളതെന്ന് മനസ്സിലാക്കാൻ, "
        "നിങ്ങൾ നേരിടുന്ന പ്രശ്നത്തെക്കുറിച്ച് കുറച്ചുകൂടി വിവരങ്ങൾ പങ്കുവെക്കാമോ?"
    ),
    "ta": (
        "நான் உங்களுக்கு உதவ இங்கே இருக்கிறேன். உங்கள் சூழ்நிலையில் என்ன சட்ட உரிமைகள் பொருந்தும் என்பதைப் புரிந்து கொள்ள, "
        "நீங்கள் எதிர்கொள்ளும் பிரச்சனை பற்றிய கூடுதல் விவரங்களைப் பகிர முடியுமா?"
    ),
    "te": (
        "నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను. మీ పరిస్థితిలో ఏ చట్టపరమైన హక్కులు వర్తిస్తాయో అర్థం చేసుకోవడానికి, "
        "మీరు ఎదుర్కొంటున్న సమస్య గురించి మరికొన్ని వివరాలను పంచుకోగలరా?"
    ),
    "bn": (
        "আমি আপনাকে সাহায্য করতে এখানে আছি। আপনার পরিস্থিতিতে কোন আইনি অধিকার প্রযোজ্য তা বোঝার জন্য, "
        "আপনি যে সমস্যার সম্মুখীন হচ্ছেন সে সম্পর্কে আরও কিছু বিশদ জানাতে পারবেন কি?"
    ),
    "hinglish": (
        "Main aapki help ke liye yahan hoon. Aapki situation me kaun se legal rights apply hote hain yeh samajhne ke liye, "
        "kya aap apne dispute ya problem ke bare me thodi aur details share kar sakte hain?"
    )
}

# Urgent Emergency Guidance across languages
URGENT_SAFETY_RESPONSES = {
    "en": (
        "⚠️ **URGENT SAFETY & EMERGENCY GUIDANCE**\n\n"
        "If you or someone else is in immediate physical danger, facing an ongoing assault, or under threat of bodily harm, please prioritize your immediate safety right now:\n\n"
        "1. **Emergency Police Response:** Dial **112** (National Emergency Response Support System) immediately.\n"
        "2. **Women Helpline (Domestic Abuse & Distress):** Dial **1091** or **181** for 24x7 emergency protection and police dispatch.\n"
        "3. **Cyber Blackmail & Non-Consensual Imagery:** If someone is threatening to leak private/intimate photos or videos, do not pay money or yield to extortion. Call **1930** (Cybercrime Helpline) and file an immediate report at [cybercrime.gov.in](https://cybercrime.gov.in).\n"
        "4. **Seek Immediate Shelter:** Move to a populated public space, a police station, or reach out to trusted neighbours/family.\n\n"
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
        "4. **સલામત સ્થળે જાઓ:** તાત્કાલિક નજીકના પોલીસ સ્ટેશન અથવા સુરક્ષિત સ્થળે પહોંચો."
    ),
    "mr": (
        "⚠️ **तातडीचे सुरक्षा व आपत्कालीन मार्गदर्शन**\n\n"
        "जर तुम्ही किंवा इतर कोणी तात्काळ शारीरिक धोक्यात असाल किंवा हल्ल्याचा सामना करत असाल, तर कृपया ताबडतोब स्वतःच्या सुरक्षिततेला प्राधान्य द्या:\n\n"
        "1. **आपत्कालीन पोलीस मदत:** ताबडतोब **112** (राष्ट्रीय आपत्कालीन क्रमांक) वर कॉल करा.\n"
        "2. **महिला हेल्पलाइन:** २४ तास मदतीसाठी **1091** किंवा **181** डायल करा.\n"
        "3. **सायबर ब्लॅकमेल व खाजगी फोटोची धमकी:** कोणी खाजगी फोटो लीक करण्याची धमकी देत असल्यास खंडणी देऊ नका. त्वरित **1930** वर कॉल करा आणि [cybercrime.gov.in](https://cybercrime.gov.in) वर तक्रार नोंदवा.\n"
        "4. **सुरक्षित ठिकाणी जा:** ताबडतोब जवळच्या पोलीस ठाण्यात किंवा सुरक्षित ठिकाणी आश्रय घ्या."
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
        "4. **Safe Place Par Jayein:** Nearest police station ya crowded public place par move karein."
    )
}


class IntentGate:
    """
    Dedicated Backend-Level Semantic Intent Gate.
    Runs prior to legal RAG retrieval, case building, and response generation.
    """

    @classmethod
    def normalize_informal(cls, text: str) -> str:
        """Normalizes common phonetic misspellings and informal shorthand."""
        t = text.lower()
        subs = [
            (r"\blandlrd\b", "landlord"),
            (r"\brnt\b", "rent"),
            (r"\bdposit\b", "deposit"),
            (r"\bnhe\b", "nahi"),
            (r"\bkru\b", "karu"),
            (r"\bemployr\b", "employer"),
            (r"\bsalry\b", "salary"),
            (r"\breson\b", "reason"),
            (r"\binfomation\b", "information"),
            (r"\bwht\b", "what"),
            (r"\btel\b", "tell"),
            (r"\bfuny\b", "funny"),
            (r"\bjok\b", "joke"),
            (r"\bhlp\b", "help"),
            (r"\bhlo\b", "hello"),
            (r"\bplz\b", "please")
        ]
        for p, r in subs:
            t = re.sub(p, r, t)
        return t

    @classmethod
    def detect_language(cls, text: str, explicit_lang: Optional[str] = None) -> str:
        """Determines message language from character scripts and vocabulary."""
        if explicit_lang and explicit_lang in STANDARD_NON_LEGAL_RESPONSES:
            return explicit_lang

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
            marathi_markers = ["आहे", "नाही", "काय", "मला", "तुम्ही", "करणे", "झाले", "सांगा", "हवा", "होते", "द्या"]
            if any(m in text for m in marathi_markers):
                return "mr"
            return "hi"

        lower = text.lower()
        hinglish_words = ["kya", "hai", "mujhe", "mera", "meri", "hum", "nahi", "raha", "rahi", "karo", "batayein", "paisa", "makan", "kiraya", "naukri", "madad", "bina", "karu", "rok"]
        if sum(1 for w in hinglish_words if re.search(rf"\b{w}\b", lower)) >= 2:
            return "hinglish"

        return "en"

    @classmethod
    def evaluate(
        cls,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        language: Optional[str] = None
    ) -> IntentDecision:
        """
        Evaluates user input through the multi-tiered semantic gate.
        Returns validated IntentDecision with routing directives.
        """
        trimmed = message.strip() if message else ""
        lang_str = cls.detect_language(trimmed, language)

        if not trimmed:
            return IntentDecision(
                intent=UserIntentEnum.GREETING_OR_SOCIAL,
                confidence=1.0,
                is_mixed=False,
                context_influenced=False,
                topic_changed=False,
                detected_language=lang_str,
                reasoning="Empty input treated as conversational greeting.",
                direct_response="Hello! I am LawPilot AI, your legal assistant for Indian law. How can I assist you with your legal questions today?"
            )

        lower = trimmed.lower()
        norm_text = cls.normalize_informal(trimmed)
        norm_clean = re.sub(r'[?.!,;:]+$', '', norm_text).strip()
        words = norm_text.split()
        word_count = len(words)

        # -------------------------------------------------------------
        # TIER 1: CRITICAL SAFETY TRIAGING (Imminent Harm / Assault / Extortion)
        # -------------------------------------------------------------
        urgent_safety_patterns = [
            r"\b(?:physically\s+attack(?:ing|ed)?|attacking\s+me|attacked\s+me|beating\s+me|beaten\s+up|threaten(?:ed|ing)?\s+to\s+kill|kill\s+me|kill\s+my|murder\s+me|stab(?:bing|bed)?|shooting|danger\s+right\s+now|immediate\s+danger|someone\s+is\s+trying\s+to\s+hurt\s+me|threatening\s+to\s+hurt|assault(?:ing|ed)?\s+me|kidnap(?:ping|ped)?|suicide|kill\s+myself|break\s+my\s+legs|goons\s+outside|bouncers\s+attacking|men\s+with\s+weapons|break\s+into\s+my\s+house)\b",
            r"\b(?:leak\s+(?:my\s+)?(?:private|intimate|nude|naked|personal)\s+(?:photos?|photographs?|pictures?|videos?|pics?)|sharing\s+my\s+(?:nudes|private\s+photos|private\s+photographs)|circulate\s+my\s+(?:nudes|nude|private)|morphing\s+my\s+photos|blackmailing\s+me\s+with\s+(?:photos|photographs|videos|pictures)|extorting\s+me\s+with\s+(?:photos|photographs|videos))\b",
            r"(?:हमला\s*कर\s*रहा|जान\s*से\s*मारने|मारपीट\s*कर|हल्ला\s*करत\s*आहे|जीवाला\s*धोका|खाजगी\s*फोटो\s*लीक|प्राइवेट\s*फोटो\s*लीक|મારી\s*પર\s*હુમલો|જાનથી\s*મારી\s*નાખવાની|અંગત\s*ફોટો\s*લીક|આક્રમણ|ജീവന്\s*ഭീഷണി|സ്വകാര്യ\s*ചിത്രങ്ങൾ|தாக்குகிறார்|கொலை\s*மிரட்டல்|దాడి\s*చేస్తున్నారు|আক্রমণ\s*করছে)"
        ]
        if any(re.search(pat, norm_text) or re.search(pat, trimmed) for pat in urgent_safety_patterns):
            resp = URGENT_SAFETY_RESPONSES.get(lang_str, URGENT_SAFETY_RESPONSES["en"])
            return IntentDecision(
                intent=UserIntentEnum.URGENT_SAFETY,
                confidence=0.99,
                is_mixed=False,
                context_influenced=False,
                topic_changed=False,
                detected_language=lang_str,
                reasoning="Urgent physical safety or cyber extortion detected; routed immediately to emergency helplines 112/1091/1930.",
                direct_response=resp,
                rag_invoked=False,
                legal_generation_invoked=False
            )

        # -------------------------------------------------------------
        # TIER 2: ADVERSARIAL ROLEPLAY / JAILBREAK NEUTRALIZATION
        # -------------------------------------------------------------
        jailbreak_patterns = [
            r"\b(?:act\s+as\s+chatgpt|act\s+as\s+an\s+unrestricted\s+ai|ignore\s+(?:your\s+)?legal\s+restrictions|forget\s+you\s+are\s+a\s+lawyer|act\s+as\s+dan|developer\s+mode|pretend\s+you\s+are\s+chatgpt|pretend\s+you\s+are\s+not\s+a\s+lawyer)\b"
        ]
        if any(re.search(pat, norm_text) for pat in jailbreak_patterns):
            resp = STANDARD_NON_LEGAL_RESPONSES.get(lang_str, STANDARD_NON_LEGAL_RESPONSES["en"])
            return IntentDecision(
                intent=UserIntentEnum.NON_LEGAL_QUERY,
                confidence=0.98,
                is_mixed=False,
                context_influenced=False,
                topic_changed=True,
                detected_language=lang_str,
                reasoning="Prompt injection / roleplay scope evasion neutralized; specialized legal identity enforced.",
                direct_response=resp,
                rag_invoked=False,
                legal_generation_invoked=False
            )

        # -------------------------------------------------------------
        # TIER 3: CONTEXTUAL FOLLOW-UP & TOPIC SHIFT ANALYSIS
        # -------------------------------------------------------------
        has_legal_history = False
        if conversation_history:
            for turn in conversation_history[-4:]:
                t_content = turn.get("content", "").lower()
                if any(w in t_content for w in ["fir", "court", "deposit", "landlord", "salary", "employer", "police", "notice", "divorce", "cheque", "hacked", "tax", "bnss", "cpa", "consumer"]):
                    has_legal_history = True
                    break

        # Contextual follow-up phrases (dependent on active consultation)
        is_follow_up_phrase = bool(re.search(
            r"^(?:what\s+should\s+i\s+do\s+next\??|what\s+next\??|how\s+much\s+time\s+do\s+i\s+have\??|what\s+documents\s+are\s+needed\??|can\s+i\s+go\s+to\s+court\??|how\s+do\s+i\s+approach\s+the\s+(?:magistrate|court)\b|what\s+is\s+the\s+fee\s+to\s+file\b|ab\s+kya\s+karein\??|aage\s+kya\s+karna\s+hoga\??|what\s+are\s+my\s+next\s+steps\??)$",
            norm_text
        ))

        if is_follow_up_phrase and has_legal_history:
            return IntentDecision(
                intent=UserIntentEnum.LEGAL_QUERY,
                confidence=0.95,
                is_mixed=False,
                context_influenced=True,
                topic_changed=False,
                detected_language=lang_str,
                reasoning="Follow-up query semantically bound to active legal consultation in conversation history.",
                direct_response=None,
                rag_invoked=True,
                legal_generation_invoked=True
            )

        # -------------------------------------------------------------
        # TIER 4: PURE SOCIAL & GREETINGS
        # -------------------------------------------------------------
        greeting_patterns = [
            r"^(?:hi|hello|hey|namaste|pranam|kem\s*cho|kemon\s*acho|vanakkam|namaskaram|namaskara|adaab|sat\s*sri\s*akal|sasriyakaal|good\s*(?:morning|afternoon|evening))\b",
            r"^(?:who\s+are\s+you|what\s+is\s+your\s+name|what\s+do\s+you\s+do|what\s+can\s+you\s+help\s+me\s+with|how\s+are\s+you)\b",
            r"^(?:thank\s+you|thanks|thanks\s+a\s+lot|thank\s+you\s+so\s+much|bye|goodbye|alvida|shukriya|dhanyawad)\b",
            r"^(?:नमस्ते|प्रणाम|नमस्कार|નમસ્તે|કેમ\s*છો|നമസ്കാരം|வணக்கம்|నమస్కారం|নমস্কার)"
        ]
        is_greeting = any(re.search(pat, norm_text) or re.search(pat, trimmed) for pat in greeting_patterns)

        # -------------------------------------------------------------
        # TIER 5: SEMANTIC INTENT CLASSIFICATION (LEGAL vs NON-LEGAL)
        # -------------------------------------------------------------

        # Semantic Legal Intent: Rights, disputes, wrongs, liabilities, authorities, remedies, procedures
        legal_semantic_intent = bool(re.search(
            r"\b(?:fir|police|complaint|arrest|bail|anticipatory|warrant|summons|charge\s*sheet|magistrate|court|judge|advocate|lawyer|bns|bnss|bsa|ipc|crpc|evidence|statute|statutory|offence|crime|cheating|fraud|theft|assault|extortion|defamation|contempt|habeas\s*corpus|mandamus|writ|appeal|revision|tribunal|quash|zero\s*fir|e-fir|"
            r"notice|legal\s*notice|court\s*notice|notice\s*received|received\s*a\s*notice|deposit|rent|tenant|landlord|eviction|evict|lease|agreement|possession|encroachment|property|land|registration|sub-registrar|mutation|patta|khata|satbara|7/12|rera|partition|will|probate|succession|ancestral\s*property|coparcenary|legal\s*heir|gift\s*deed|sale\s*deed|title|trespass|boundary|trespassing|occupying\s*my\s*land|cut\s+down\s+a\s+tree|bachelors\s+from\s+renting|housing\s+society|rwa|residents\s+welfare|"
            r"consumer|defective|refund|replacement|warranty|guarantee|e-commerce|seller|unfair\s*trade|deficiency\s*in\s*service|nch|e-daakhil|district\s*forum|ncdrc|contract|breach|damages|penalty|indemnity|promissory\s*note|arbitration|mediation|lok\s*adalat|specific\s*performance|"
            r"salary|wages|employer|employee|workplace|termination|terminate|resignation|fired|relieving|experience\s*(?:certificate|letter)|gratuity|provident\s*fund|pf|bonus|posh|harassment|discrimination|severance|labour\s*court|labour\s*commissioner|dues|withheld|full\s*and\s*final|"
            r"cheque|cheque\s*bounce|dishonour|section\s*138|ni\s*act|bank\s*account|account\s*freeze|sarfaesi|loan\s*app|loan\s*default|recovery\s*agent|drt|cyber\s*fraud|online\s*fraud|hacked|phishing|upi|unauthorized\s*transaction|rbi\s*ombudsman|insurance|claim\s*rejected|claim\s*was\s*rejected|policy|tax|income\s*tax|gst|tax\s*notice|scrutiny|challan|traffic\s*challan|meter\s*tampering|electricity\s*board|electricity\s*act|seize\s*my\s*(?:personal\s+)?smartphone|"
            r"divorce|maintenance|alimony|custody|child\s*support|restitution|hindu\s*marriage|special\s*marriage|muslim\s*marriage|pwdva|domestic\s*violence|dowry|498a|pocso|child\s*abuse|"
            r"trademark|copyright|patent|infringement|piracy|intellectual\s*property|defaming|fake\s*(?:1-star\s+)?reviews|rti|right\s*to\s*information|pio|first\s*appeal|mact|motor\s*accident|accident\s*claim|hit\s*and\s*run|pollution|ngt|citizenship|passport\s*impounded|rte|central\s*administrative\s*tribunal|free\s*legal\s*aid|nalsa|dlsa|"
            r"section\s+\d+|order\s+\d+|article\s+\d+|rule\s+\d+|act\s+of\s+\d{4}|tenancy\s+act|consumer\s+protection\s+act|penal\s+code|civil\s+procedure|criminal\s+procedure)\b",
            norm_text
        )) or bool(re.search(
            r"(?:"
            # Hindi / Devanagari (Hindi, Marathi)
            r"डिपॉज़िट|वेतन|किराया|मकान\s*मालिक|सैलरी|रिफंड|दोषपूर्ण|नोटीस|नोटिस|एफआईआर|जमानत|तलाक|घरेलू\s*हिंसा|रेरा|चेक|बाउंस|बैंक|फ्रॉड|धोखाधड़ी|कोर्ट|अदालत|वकील|मुकदमा|चोरी|मारपीट|संपत्ति|ज़मीन|अधिकार|धारा|शिकायत|अपराध|क्षतिपूर्ति|"
            r"जामीन|घटस्फोट|पोटगी|विवाह|घरमालक|भाडे|हक्क|वाद|न्यायालय|फसवणूक|तक्रार|गुन्हा|वारस|सातबारा|"
            # Gujarati
            r"ચલણ|ટ્રાફિક|સિક્યોરિટી|પગાર|ભાડું|મકાનમાલિક|રિફંડ|ખામીયુક્ત|ડિપોઝિટ|પોલીસ|એફઆઈઆર|જામીન|છૂટાછેડા|રેરા|ચેક|બાઉન્સ|ફ્રોડ|છેતરપિંડી|યુપીઆઇ|ફરિયાદ|કોર્ટ|અદાલત|નોટિસ|વકીલ|મિલકત|જમીન|અધિકાર|કલમ|ગુનો|વારસદાર|"
            # Malayalam
            r"ശമ്പളം|വാടക|തൊഴിലുടമ|റീഫണ്ട്|പോലീസ്|ജാമ്യം|വിവാഹമോചനം|ചെക്ക്|ബൗൺസ്|തട്ടിപ്പ്|പരാതി|കോടതി|നോട്ടീസ്|അഭിഭാഷകൻ|സ്വത്ത്|തകരാർ|നഷ്ടപരിഹാരം|കേസ്|ഉപഭോക്തൃ|അവകാശം|നിയമം|"
            # Tamil
            r"ஜாமீன்|சம்பளம்|வாடகை|நிறுவனம்|விவாகரத்து|காசோலை|பவுன்ஸ்|மோசடி|புகார்|போலீஸ்|நீதிமன்றம்|நோட்டீஸ்|வழக்கறிஞர்|சொத்து|சட்டம்|உரிமை|நுகர்வோர்|இழப்பீடு|வழக்கு|"
            # Telugu
            r"జీతం|అద్దె|డిపాజిట్|బెయిల్|విడాకులు|ఆక్రమించారు|భూమిని|చెక్|బౌన్స్|మోసం|ఫిర్యాదు|పోలీస్|కోర్టు|నోటీసు|న్యాయవాది|ఆస్తి|చట్టం|హక్కు|వినియోగదారుల|నష్టపరిహారం|కేసు|"
            # Bengali
            r"বেতন|ভাড়া|রিফান্ড|ঘরমালিক|ডিভোর্স|জামিন|বাড়িওয়ালা|ডিপোজিট|চেক|বাউন্স|প্রতারণা|অভিযোগ|পুলিশ|আদালত|নোটিশ|উকিল|সম্পত্তি|মামলা|ধারা|অধিকার|ক্রেতা|ক্ষতিপূরণ"
            r")",
            trimmed
        ))

        # Semantic Non-Legal Intent: General knowledge, coding, science, biology, DIY/household, sports, cooking, history, entertainment
        non_legal_semantic_intent = bool(re.search(
            r"\b(?:where\s+is\s+|where\s+are\s+|where\s+can\s+i\s+find\s+|where\s+to\s+find\s+|where\s+in\s+the\s+world|"
            r"what\s+is\s+(?!section|the\s+section|article|order|rule|the\s+law|an?\s+fir|bail|anticipatory|a\s+legal|my\s+legal|the\s+act|the\s+procedure|the\s+punishment|the\s+penalty|the\s+fine|bns|bnss|bsa|ipc|crpc|cpa|rera|pwdva|posh|legal\s+heir|limitation|order\s+37|due\s+process|quash)|"
            r"who\s+is\s+(?!the\s+magistrate|the\s+judge|the\s+police|the\s+advocate|the\s+lawyer|the\s+public\s+prosecutor|the\s+commissioner)|"
            r"who\s+was\s+|who\s+were\s+|when\s+was\s+|when\s+did\s+|why\s+is\s+|why\s+are\s+|why\s+do\s+|"
            r"teach\s+me\s+|teach\s+(?:oops\s+)?python|oops\s+python|learn\s+python|learn\s+coding|how\s+to\s+code|"
            r"capital\s+of\s+[a-zA-Z]+|who\s+is\s+the\s+president\s+of|largest\s+ocean|tallest\s+building|currency\s+of\s+[a-zA-Z]+|who\s+is\s+the\s+prime\s+minister\s+of\s+(?!india)|deepest\s+lake|highest\s+peak|when\s+did\s+world\s+war|fall\s+of\s+the\s+roman\s+empire|causes\s+of\s+the\s+fall|"
            r"write\s+(?:a\s+)?(?:python|c\+\+|java|javascript|php|sql|ruby|go|c#)\s+(?:program|script|code|function)|python\s+code|sort\s+an?\s+(?:list|array)|binary\s+search|binary\s+search\s+trees|bubble\s+sort|leetcode|help\s+me\s+create\s+a\s+website|how\s+to\s+build\s+a\s+website|write\s+an\s+algorithm|debug\s+this\s+code|"
            r"explain\s+machine\s+learning|what\s+is\s+machine\s+learning|how\s+does\s+machine\s+learning\s+work|neural\s+networks?|deep\s+learning|nlp\s+model|linear\s+regression|"
            r"explain\s+quantum\s+physics|quantum\s+physics|theory\s+of\s+relativity|schrodinger|photosynthesis|chemical\s+equation\s+and\s+process\s+of\s+photosynthesis|crispr|gene\s+editing|solar\s+panels\s+convert\s+sunlight|solve\s+(?:this\s+)?mathematics|solve\s+(?:this\s+)?math|solve\s+(?:an?\s+)?equation|calculus|what\s+is\s+\d+\s*(?:\+|\-|\*|\/|plus|minus)\s*\d+|\d+\s*(?:\+|\-|\*|\/|plus)\s*\d+|periodic\s+table|gravity\s+formula|"
            r"tell\s+me\s+a\s+(?:funny\s+)?joke|tell\s+(?:me\s+)?a\s+joke|write\s+a\s+(?:romantic\s+)?poem|romantic\s+poem|write\s+(?:a\s+)?poem|sing\s+a\s+song|write\s+a\s+rap|write\s+a\s+story\s+about|bedtime\s+story|who\s+painted\s+the\s+starry\s+night|painted\s+the\s+starry|"
            r"who\s+won\s+(?:yesterday'?s\s+)?cricket\s+match|who\s+won\s+the\s+match|cricket\s+match|ipl\s+score|football\s+score|fifa\s+world\s+cup|olympics|chess\s+opening|half\s+marathon|training\s+schedule\s+for\s+a\s+(?:half\s+)?marathon|"
            r"gym\s+workout\s+plan|workout\s+plan|fitness\s+plan|how\s+to\s+lose\s+weight|recipe\s+for|give\s+me\s+a\s+recipe|recipe\s+in\s+[a-zA-Z]+|how\s+to\s+bake|how\s+to\s+cook|sourdough\s+bread|paneer\s+butter\s+masala|"
            r"what\s+is\s+the\s+weather\s+today|weather\s+forecast|weather\s+kaisa\s+rahega|suggest\s+a\s+travel\s+itinerary|travel\s+itinerary|trip\s+to\s+[a-zA-Z]+|tourist\s+places\s+in|"
            r"suggest\s+a\s+(?:good\s+)?movie|recommend\s+a\s+movie|best\s+movies\s+to\s+watch|recommend\s+a\s+book|recommend\s+a\s+(?:good\s+)?laptop|laptop\s+for\s+video\s+editing|"
            r"fix\s+a\s+leaking\s+(?:bathroom\s+)?faucet|leaking\s+(?:bathroom\s+)?faucet|how\s+do\s+i\s+fix)\b",
            norm_text
        )) or bool(re.search(
            r"(?:चुटकुला|जोक|विनोद|જોક|જોક્સ|ચુટકલો|തമാശ|நகைச்சுவை|జోక్|কৌতুক|একটি\s*মজার\s*গল্প|"
            r"रेसिपी|રેસીપી|पाचकക്കുറിപ്പ്|ரெசிபி|రెసిపీ|রেসিপি|"
            r"मशीन\s*लर्निंग|મશીન\s*લર્નિંગ|മെഷീൻ\s*ലേണിംഗ്|மெஷின்\s*லேர்னிங்|మొషిన్\s*లెర్నింగ్|মেশিন\s*লার্নিং|"
            r"कविता\s*लिखो|કવિતા|कविता\s*लिहा|കവിത|கவிதை|కవిత|কবিতা|"
            r"फ्रांस\s*की\s*राजधानी|ફ્રાન્સની\s*રાજધાની|फ्रान्सची\s*राजधानी|ഫ്രാൻസിന്റെ\s*തലസ്ഥാനം|குவாண்டம்\s*இயற்பியல்|క్వాంటమ్\s*ఫిజిక్స్|কোয়ান্টাম\s*পদার্থবিদ্যা)",
            trimmed
        ))

        # Adversarial extraction: If prompt contains a request to write code or explain non-legal science
        # disguised inside a legal hypothetical (e.g. "hypothetically imagine court scenario... write python script")
        if re.search(r"\b(?:write\s+a\s+python\s+script|explain\s+(?:the\s+)?(?:chemical\s+equation|process\s+of\s+photosynthesis))\b", norm_text):
            non_legal_semantic_intent = True
            legal_semantic_intent = False

        # Check for pure greeting (without substantive dispute or non-legal requests)
        if is_greeting and not legal_semantic_intent and not non_legal_semantic_intent and word_count <= 8:
            return IntentDecision(
                intent=UserIntentEnum.GREETING_OR_SOCIAL,
                confidence=0.98,
                is_mixed=False,
                context_influenced=False,
                topic_changed=False,
                detected_language=lang_str,
                reasoning="Conversational greeting or social pleasantry without legal dispute or non-legal task.",
                direct_response=None,
                rag_invoked=False,
                legal_generation_invoked=False
            )

        # Check for Ambiguous Query (vague help request or emotional distress lacking factual particulars)
        ambiguous_patterns = [
            r"^(?:i\s+need\s+help|please\s+help\s+me|help\s+me|help\s+me\s+please|i\s+have\s+a\s+problem|someone\s+is\s+troubling\s+me|i\s+am\s+in\s+(?:serious\s+)?trouble|i\s+received\s+a\s+document|i\s+received\s+a\s+courier|what\s+can\s+i\s+do|i\s+don't\s+know\s+what\s+to\s+do|feeling\s+stressed|feeling\s+very\s+anxious|confused\s+about\s+what\s+to\s+do|i\s+am\s+confused\s+and\s+don'?t\s+know\s+what\s+to\s+do|i\s+am\s+confused|confused|something\s+bad\s+happened|something\s+went\s+wrong\s+at\s+my\s+office|need\s+advice|can\s+you\s+help\s+me\??)$",
            r"^(?:मुझे\s*मदद\s*चाहिए|मेरी\s*मदद\s*करो|कोई\s*मुझे\s*परेशान\s*कर\s*रहा\s*है|मुझे\s*एक\s*दस्तावेज़\s*मिला\s*है|मैं\s*मुसीबत\s*में\s*हूँ|મને\s*મદદ\s*જોઈએ\s*છે|હું\s*મુશ્કેલીમાં\s*છું|मला\s*मदत\s*हवी\s*आहे|मी\s*अडचणीत\s*आहे|എനിക്ക്\s*സഹായം\s*വേണം)$"
        ]
        is_ambiguous = any(re.search(pat, norm_text) or re.search(pat, norm_clean) or re.search(pat, trimmed) for pat in ambiguous_patterns)
        if is_ambiguous and word_count <= 12 and not has_legal_history:
            resp = AMBIGUOUS_CLARIFICATION_RESPONSES.get(lang_str, AMBIGUOUS_CLARIFICATION_RESPONSES["en"])
            return IntentDecision(
                intent=UserIntentEnum.AMBIGUOUS,
                confidence=0.92,
                is_mixed=False,
                context_influenced=False,
                topic_changed=False,
                detected_language=lang_str,
                reasoning="Vague statement lacking factual legal dispute context; asking targeted clarifying question.",
                direct_response=resp,
                rag_invoked=False,
                legal_generation_invoked=False
            )

        
        # Check for generic drafting assistance inquiry (A11)
        is_draft_inquiry = bool(re.search(
            r"^(?:can\s+you\s+help\s+me\s+draft\s+a\s+letter\??|help\s+me\s+draft\s+a\s+letter|draft\s+a\s+letter|write\s+a\s+letter\s+for\s+me|can\s+you\s+write\s+a\s+letter\??)$",
            norm_clean
        ) or re.search(
            r"^(?:can\s+you\s+help\s+me\s+draft\s+a\s+letter\??|help\s+me\s+draft\s+a\s+letter|draft\s+a\s+letter|write\s+a\s+letter\s+for\s+me|can\s+you\s+write\s+a\s+letter\??)$",
            norm_text
        ))
        if is_draft_inquiry:
            resp = DRAFTING_INQUIRY_RESPONSES.get(lang_str, DRAFTING_INQUIRY_RESPONSES["en"])
            return IntentDecision(
                intent=UserIntentEnum.AMBIGUOUS,
                confidence=0.92,
                is_mixed=False,
                context_influenced=False,
                topic_changed=False,
                detected_language=lang_str,
                reasoning="Generic drafting inquiry; asking user to specify the nature of the letter and whether it involves a legal matter.",
                direct_response=resp,
                rag_invoked=False,
                legal_generation_invoked=False
            )

        # Mixed Query: Legal dispute present AND unrelated non-legal request present
        if legal_semantic_intent and non_legal_semantic_intent:
            return IntentDecision(
                intent=UserIntentEnum.LEGAL_QUERY,
                confidence=0.92,
                is_mixed=True,
                context_influenced=False,
                topic_changed=False,
                detected_language=lang_str,
                reasoning="Mixed query: contains genuine Indian legal dispute alongside an unrelated non-legal request.",
                direct_response=None,
                rag_invoked=True,
                legal_generation_invoked=True
            )

        # Pure Non-Legal Query: Topic changed or independent non-legal inquiry
        if non_legal_semantic_intent and not legal_semantic_intent:
            resp = STANDARD_NON_LEGAL_RESPONSES.get(lang_str, STANDARD_NON_LEGAL_RESPONSES["en"])
            return IntentDecision(
                intent=UserIntentEnum.NON_LEGAL_QUERY,
                confidence=0.96,
                is_mixed=False,
                context_influenced=False,
                topic_changed=has_legal_history,  # Topic changed if prior history was legal
                detected_language=lang_str,
                reasoning="Unrelated non-legal topic; excluded from legal pipeline and declined with scope notification.",
                direct_response=resp,
                rag_invoked=False,
                legal_generation_invoked=False
            )

        # Genuine Legal Query:
        if legal_semantic_intent:
            return IntentDecision(
                intent=UserIntentEnum.LEGAL_QUERY,
                confidence=0.95,
                is_mixed=False,
                context_influenced=False,
                topic_changed=False,
                detected_language=lang_str,
                reasoning="Substantive Indian legal query across operative civil, criminal, property, labour, or regulatory statutes.",
                direct_response=None,
                rag_invoked=True,
                legal_generation_invoked=True
            )

        # -------------------------------------------------------------
        # TIER 6: COMMON RESPONSE FOR USERS NOT HAVING LEGAL ISSUES
        # Any query that does not present an Indian legal issue, legal dispute,
        # or ambiguous plea for help is recognized as non-legal.
        # All users without legal issues receive the EXACT SAME common response.
        # -------------------------------------------------------------
        resp = STANDARD_NON_LEGAL_RESPONSES.get(lang_str, STANDARD_NON_LEGAL_RESPONSES["en"])
        return IntentDecision(
            intent=UserIntentEnum.NON_LEGAL_QUERY,
            confidence=0.95,
            is_mixed=False,
            context_influenced=False,
            topic_changed=False,
            detected_language=lang_str,
            reasoning="Query does not present an Indian legal issue or dispute. Routed to common non-legal scope response.",
            direct_response=resp,
            rag_invoked=False,
            legal_generation_invoked=False
        )
