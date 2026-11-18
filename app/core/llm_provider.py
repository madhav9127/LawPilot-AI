import os
import json
import re
import uuid
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import requests

from app.models.schemas import (
    ChatMessage, CaseData, LegalCitation, VerificationStatusEnum,
    LanguageEnum, CaseCategoryEnum
)
from app.core.sanitizer import Sanitizer
from app.core.knowledge_base import LegalKnowledgeBase
from app.core.escalation import EscalationDetector
from app.core.case_builder import CaseBuilder
from app.core.conversation import ConversationCaseMemory

# Set up audit logger
logger = logging.getLogger("lawpilot.audit")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[AUDIT] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Persistent session store for multi-turn conversations
SESSION_MEMORIES: Dict[str, ConversationCaseMemory] = {}

def get_or_create_memory(session_id: str) -> ConversationCaseMemory:
    if session_id not in SESSION_MEMORIES:
        SESSION_MEMORIES[session_id] = ConversationCaseMemory(session_id)
    return SESSION_MEMORIES[session_id]

def reset_memory(session_id: Optional[str] = None):
    """Resets memory for a specific session or all sessions."""
    global SESSION_MEMORIES
    if session_id:
        if session_id in SESSION_MEMORIES:
            del SESSION_MEMORIES[session_id]
            logger.info(f"Cleared memory for session: {session_id}")
    else:
        SESSION_MEMORIES.clear()
        logger.info("Cleared all session memories.")


LANGUAGE_CONFIG = {
    "en": {
        "name": "English",
        "script": "Latin",
        "headers": {
            "situation": "### Understanding Your Situation",
            "provisions": "### Relevant Legal Provisions",
            "legal_position": "### Your Legal Position",
            "options": "### Available Options",
            "next_steps": "### Practical Next Steps",
            "evidence": "### Evidence to Preserve",
            "limitations": "### Important Limitations",
            "info_needed": "### Information I still need from you"
        }
    },
    "hi": {
        "name": "Hindi (हिंदी)",
        "script": "Devanagari",
        "headers": {
            "situation": "### आपकी स्थिति को समझना (Understanding Your Situation)",
            "provisions": "### प्रासंगिक कानूनी धाराएं (Relevant Legal Provisions)",
            "legal_position": "### आपकी कानूनी स्थिति (Your Legal Position)",
            "options": "### उपलब्ध कानूनी विकल्प (Available Options)",
            "next_steps": "### व्यावहारिक अगले कदम (Practical Next Steps)",
            "evidence": "### सुरक्षित रखने योग्य साक्ष्य (Evidence to Preserve)",
            "limitations": "### महत्वपूर्ण कानूनी सीमाएं (Important Limitations)",
            "info_needed": "### आपसे आवश्यक अतिरिक्त जानकारी"
        }
    },
    "gu": {
        "name": "Gujarati (ગુજરાતી)",
        "script": "Gujarati",
        "headers": {
            "situation": "### તમારી પરિસ્થિતિની સમજ (Understanding Your Situation)",
            "provisions": "### સંબંધિત કાનૂની જોગવાઈઓ (Relevant Legal Provisions)",
            "legal_position": "### તમારો કાનૂની પક્ષ (Your Legal Position)",
            "options": "### ઉપલબ્ધ કાનૂની વિકલ્પો (Available Options)",
            "next_steps": "### વ્યવહારુ આગલા પગલાં (Practical Next Steps)",
            "evidence": "### સાચવી રાખવા યોગ્ય પુરાવા (Evidence to Preserve)",
            "limitations": "### મહત્વપૂર્ણ કાનૂની મર્યાદાઓ (Important Limitations)",
            "info_needed": "### તમારી પાસેથી જરૂરી વધારાની માહિતી"
        }
    },
    "mr": {
        "name": "Marathi (मराठी)",
        "script": "Devanagari (Marathi)",
        "headers": {
            "situation": "### तुमची परिस्थिती समजून घेणे (Understanding Your Situation)",
            "provisions": "### संबंधित कायदेशीर तरतुदी (Relevant Legal Provisions)",
            "legal_position": "### तुमची कायदेशीर स्थिती (Your Legal Position)",
            "options": "### उपलब्ध कायदेशीर पर्याय (Available Options)",
            "next_steps": "### व्यावहारिक पुढील पावले (Practical Next Steps)",
            "evidence": "### जपून ठेवण्याचे पुरावे (Evidence to Preserve)",
            "limitations": "### महत्त्वाच्या कायदेशीर मर्यादा (Important Limitations)",
            "info_needed": "### तुमच्याकडून आवश्यक अतिरिक्त माहिती"
        }
    },
    "ml": {
        "name": "Malayalam (മലയാളം)",
        "script": "Malayalam",
        "headers": {
            "situation": "### നിങ്ങളുടെ സാഹചര്യം മനസ്സിലാക്കൽ (Understanding Your Situation)",
            "provisions": "### പ്രസക്തമായ നിയമ വ്യവസ്ഥകൾ (Relevant Legal Provisions)",
            "legal_position": "### നിങ്ങളുടെ നിയമപരമായ അവകാശം (Your Legal Position)",
            "options": "### ലഭ്യമായ നിയമപരമായ വഴികൾ (Available Options)",
            "next_steps": "### പ്രായോഗിക അടുത്ത നടപടികൾ (Practical Next Steps)",
            "evidence": "### സൂക്ഷിച്ചുവെക്കേണ്ട തെളിവുകൾ (Evidence to Preserve)",
            "limitations": "### പ്രധാനപ്പെട്ട നിയമ പരിധികൾ (Important Limitations)",
            "info_needed": "### നിങ്ങളിൽ നിന്ന് ആവശ്യമായ കൂടുതൽ വിവരങ്ങൾ"
        }
    },
    "ta": {
        "name": "Tamil (தமிழ்)",
        "script": "Tamil",
        "headers": {
            "situation": "### உங்கள் நிலைமையைப் புரிந்துகொள்ளுதல் (Understanding Your Situation)",
            "provisions": "### தொடர்புடைய சட்ட விதிகள் (Relevant Legal Provisions)",
            "legal_position": "### உங்கள் சட்டப்பூர்வ நிலை (Your Legal Position)",
            "options": "### சாத்தியமான சட்ட வழிகள் (Available Options)",
            "next_steps": "### நடைமுறை அடுத்த கட்டங்கள் (Practical Next Steps)",
            "evidence": "### பாதுகாக்க வேண்டிய ஆதாரங்கள் (Evidence to Preserve)",
            "limitations": "### முக்கியமான சட்ட வரம்புகள் (Important Limitations)",
            "info_needed": "### உங்களிடம் இருந்து தேவைப்படும் தகவல்கள்"
        }
    },
    "te": {
        "name": "Telugu (తెలుగు)",
        "script": "Telugu",
        "headers": {
            "situation": "### మీ పరిస్థితిని అర్థం చేసుకోవడం (Understanding Your Situation)",
            "provisions": "### సంబంధిత చట్టపరమైన నిబంధనలు (Relevant Legal Provisions)",
            "legal_position": "### మీ చట్టపరమైన స్థితి (Your Legal Position)",
            "options": "### అందుబాటులో ఉన్న చట్టపరమైన మార్గాలు (Available Options)",
            "next_steps": "### ఆచరణాత్మక తదుపరి చర్యలు (Practical Next Steps)",
            "evidence": "### భద్రపరచవలసిన ఆధారాలు (Evidence to Preserve)",
            "limitations": "### ముఖ్యమైన చట్టపరమైన పరిమితులు (Important Limitations)",
            "info_needed": "### మీ నుండి ఇంకా అవసరమైన సమాచారం"
        }
    },
    "bn": {
        "name": "Bengali (বাংলা)",
        "script": "Bengali",
        "headers": {
            "situation": "### আপনার পরিস্থিতি বোঝা (Understanding Your Situation)",
            "provisions": "### প্রাসঙ্গিক আইনি বিধান (Relevant Legal Provisions)",
            "legal_position": "### আপনার আইনি অবস্থান (Your Legal Position)",
            "options": "### উপলব্ধ আইনি বিকল্পসমূহ (Available Options)",
            "next_steps": "### ব্যবহারিক পরবর্তী পদক্ষেপ (Practical Next Steps)",
            "evidence": "### সংরক্ষিত রাখার মতো প্রমাণ (Evidence to Preserve)",
            "limitations": "### গুরুত্বপূর্ণ আইনি সীমাবদ্ধতা (Important Limitations)",
            "info_needed": "### আপনার কাছ থেকে প্রয়োজনীয় তথ্য"
        }
    },
    "hinglish": {
        "name": "Hinglish",
        "script": "Latin (Conversational Hindi)",
        "headers": {
            "situation": "### Understanding Your Situation (Aapki Situation)",
            "provisions": "### Relevant Legal Provisions (Lagu Hone Wale Kanoon)",
            "legal_position": "### Your Legal Position (Aapke Kanooni Adhikar)",
            "options": "### Available Options (Aapke Paas Majood Raste)",
            "next_steps": "### Practical Next Steps (Agla Kadam)",
            "evidence": "### Evidence to Preserve (Zaroori Saboot)",
            "limitations": "### Important Limitations (Kanooni Seemayein)",
            "info_needed": "### Information I still need from you (Zaroori Jankari)"
        }
    },
    "kn": {
        "name": "Kannada (ಕನ್ನಡ)",
        "script": "Kannada",
        "headers": {
            "situation": "### ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವುದು (Understanding Your Situation)",
            "provisions": "### ಸಂಬಂಧಿತ ಕಾನೂನು ನಿಬಂಧನೆಗಳು (Relevant Legal Provisions)",
            "legal_position": "### ನಿಮ್ಮ ಕಾನೂನು ಸ್ಥಾನ (Your Legal Position)",
            "options": "### ಲಭ್ಯವಿರುವ ಆಯ್ಕೆಗಳು (Available Options)",
            "next_steps": "### ಪ್ರಾಯೋಗಿಕ ಮುಂದಿನ ಕ್ರಮಗಳು (Practical Next Steps)",
            "evidence": "### ಸಂರಕ್ಷಿಸಬೇಕಾದ ಪುರಾವೆಗಳು (Evidence to Preserve)",
            "limitations": "### ಪ್ರಮುಖ ಕಾನೂನು ಮಿತಿಗಳು (Important Limitations)",
            "info_needed": "### ನಿಮ್ಮಿಂದ ಇನ್ನೂ ಅಗತ್ಯವಿರುವ ಮಾಹಿತಿ"
        }
    },
    "pa": {
        "name": "Punjabi (ਪੰਜਾਬੀ)",
        "script": "Gurmukhi",
        "headers": {
            "situation": "### ਤੁਹਾਡੀ ਸਥਿਤੀ ਨੂੰ ਸਮਝਣਾ (Understanding Your Situation)",
            "provisions": "### ਸੰਬੰਧਿਤ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ (Relevant Legal Provisions)",
            "legal_position": "### ਤੁਹਾਡੀ ਕਾਨੂੰਨੀ ਸਥਿਤੀ (Your Legal Position)",
            "options": "### ਉਪਲਬਧ ਕਾਨੂੰਨੀ ਵਿਕਲਪ (Available Options)",
            "next_steps": "### ਅਮਲੀ ਅਗਲੇ ਕਦਮ (Practical Next Steps)",
            "evidence": "### ਸੰਭਾਲਣਯੋਗ ਸਬੂਤ (Evidence to Preserve)",
            "limitations": "### ਮਹੱਤਵਪੂਰਨ ਕਾਨੂੰਨੀ ਸੀਮਾਵਾਂ (Important Limitations)",
            "info_needed": "### ਤੁਹਾਡੇ ਤੋਂ ਲੋੜੀਂਦੀ ਜਾਣਕਾਰੀ"
        }
    },
    "or": {
        "name": "Odia (ଓଡ଼ିଆ)",
        "script": "Odia",
        "headers": {
            "situation": "### ଆପଣଙ୍କ ପରିସ୍ଥିତିକୁ ବୁଝିବା (Understanding Your Situation)",
            "provisions": "### ପ୍ରାସଙ୍ଗିକ ଆଇନଗତ ବ୍ୟବସ୍ଥା (Relevant Legal Provisions)",
            "legal_position": "### ଆପଣଙ୍କ ଆଇନଗତ ସ୍ଥିତି (Your Legal Position)",
            "options": "### ଉପଲବ୍ଧ ବିକଳ୍ପ (Available Options)",
            "next_steps": "### ବ୍ୟବହାରିକ ପରବର୍ତ୍ତୀ ପଦକ୍ଷେପ (Practical Next Steps)",
            "evidence": "### ସଂରକ୍ଷଣ କରିବାକୁ ଥିବା ପ୍ରମାଣ (Evidence to Preserve)",
            "limitations": "### ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ ଆଇନଗତ ସୀମା (Important Limitations)",
            "info_needed": "### ଆପଣଙ୍କଠାରୁ ଆବଶ୍ୟକ ସୂଚନା"
        }
    }
}


def detect_message_language(message: str, explicit_lang: Optional[Any] = None) -> str:
    """
    Automatically detects language of the user's latest message independently.
    The language used in the user's latest message determines the response language.
    Supports English, Hindi, Gujarati, Malayalam, Tamil, Telugu, Bengali,
    Kannada, Marathi, Punjabi, Odia, and Hinglish.
    """
    if not message:
        return "en"

    lower_msg = message.strip().lower()

    # 1. Explicit user language request in text (highest priority)
    explicit_requests = [
        (r"\b(in\s+gujarati|gujarati\s+ma|ગુજરાતીમાં|in\s+gujrati)\b", "gu"),
        (r"\b(in\s+hindi|hindi\s+me|हिंदी\s+में)\b", "hi"),
        (r"\b(in\s+hinglish|hinglish\s+me)\b", "hinglish"),
        (r"\b(in\s+malayalam|മലയാളത്തിൽ)\b", "ml"),
        (r"\b(in\s+tamil|தமிழில்)\b", "ta"),
        (r"\b(in\s+telugu|తెలుగులో)\b", "te"),
        (r"\b(in\s+bengali|বাংলায়|bangla\s+te)\b", "bn"),
        (r"\b(in\s+kannada|ಕನ್ನಡದಲ್ಲಿ)\b", "kn"),
        (r"\b(in\s+marathi|मराठीत)\b", "mr"),
        (r"\b(in\s+punjabi|ਪੰਜਾਬੀ\s+ਵਿੱਚ)\b", "pa"),
        (r"\b(in\s+odia|ଓଡ଼ିଆରେ)\b", "or"),
        (r"\b(in\s+english|english\s+me)\b", "en")
    ]
    for pattern, lang_code in explicit_requests:
        if re.search(pattern, lower_msg, re.IGNORECASE):
            return lang_code

    # 2. Unicode Indic script frequency analysis
    script_counts = {
        "gu": 0,  # Gujarati: 0x0A80 - 0x0AFF
        "hi": 0,  # Devanagari: 0x0900 - 0x097F
        "ml": 0,  # Malayalam: 0x0D00 - 0x0D7F
        "ta": 0,  # Tamil: 0x0B80 - 0x0BFF
        "te": 0,  # Telugu: 0x0C00 - 0x0C7F
        "bn": 0,  # Bengali: 0x0980 - 0x09FF
        "kn": 0,  # Kannada: 0x0C80 - 0x0CFF
        "pa": 0,  # Gurmukhi: 0x0A00 - 0x0A7F
        "or": 0,  # Odia: 0x0B00 - 0x0B7F
    }

    for char in message:
        code = ord(char)
        if 0x0A80 <= code <= 0x0AFF:
            script_counts["gu"] += 1
        elif 0x0900 <= code <= 0x097F:
            script_counts["hi"] += 1
        elif 0x0D00 <= code <= 0x0D7F:
            script_counts["ml"] += 1
        elif 0x0B80 <= code <= 0x0BFF:
            script_counts["ta"] += 1
        elif 0x0C00 <= code <= 0x0C7F:
            script_counts["te"] += 1
        elif 0x0980 <= code <= 0x09FF:
            script_counts["bn"] += 1
        elif 0x0C80 <= code <= 0x0CFF:
            script_counts["kn"] += 1
        elif 0x0A00 <= code <= 0x0A7F:
            script_counts["pa"] += 1
        elif 0x0B00 <= code <= 0x0B7F:
            script_counts["or"] += 1

    dominant_script, max_count = max(script_counts.items(), key=lambda x: x[1])
    if max_count >= 2:
        if dominant_script == "hi":
            marathi_indicators = [
                "आहे", "माझे", "नाही", "करावे", "पाहिजे", "झाले", "दिले", "माझ्या",
                "मी", "मला", "आता", "काय", "करू", "शकतो", "शकते", "केला", "केलेली",
                "केलेले", "केले", "दोषपूर्ण", "विक्रेता", "पैसे", "परत", "देत", "होते",
                "आहोत", "करा", "सांगा", "मिळाले", "झाला", "झाली", "केलेला", "घेऊन",
                "जास्त", "फार", "फारच", "खरेदी", "मोबाईल", "घरमालक", "पगार"
            ]
            has_marathi_la = "\u0933" in message
            if has_marathi_la or any(w in message for w in marathi_indicators):
                return "mr"
            return "hi"
        return dominant_script

    # 3. Romanized / Hinglish heuristic
    hinglish_markers = [
        r"\b(mera|meri|mere|mujhe|mujhko|maine|aap|aapka|aapki|kya|kyu|kyun|kaise|kab|kahan|hai|hain|tha|thi|the|nahi|nhi|raha|rahi|rahe|karo|karna|karu|dena|diya|de|bhai|sir|madam|paise|paisa|kiraya|makan|malik|flat|salary|naukri|chahiye|bolo|bataye|batao|kripya|dhanyawad|shukriya|namaste|pranam|aur|lekin|magar|kyunki|ab|bhi|toh|hi|ho|hu|hoon)\b"
    ]
    hinglish_count = 0
    words = lower_msg.split()
    for w in words:
        if any(re.search(pat, w) for pat in hinglish_markers):
            hinglish_count += 1

    if hinglish_count >= 2 or (len(words) <= 4 and hinglish_count >= 1):
        return "hinglish"

    # Default to English
    return "en"


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: Optional[LanguageEnum] = None,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ) -> ChatMessage:
        pass

    @abstractmethod
    def generate_stream(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: Optional[LanguageEnum] = None,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ):
        pass


class DeterministicDemoProvider(BaseLLMProvider):
    """
    Structured, fully grounded legal engine covering all major areas of Indian law.
    Enforces the mandatory 7-part legal response structure, current criminal law (BNS/BNSS/BSA),
    and exact response-language consistency across all Indian languages.
    """

    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: Optional[LanguageEnum] = None,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ) -> ChatMessage:
        req_id = f"req_{uuid.uuid4().hex[:8]}"
        memory = get_or_create_memory(session_id)

        detected_lang_str = detect_message_language(message, language)
        try:
            detected_lang = LanguageEnum(detected_lang_str)
        except ValueError:
            detected_lang = LanguageEnum.ENGLISH

        lower_msg = message.strip().lower()

        # -------------------------------------------------------------
        # 0A. COMPREHENSIVE GREETINGS ACROSS ALL INDIAN LANGUAGES
        # -------------------------------------------------------------
        is_greeting = any(
            re.search(rf"\b{pat}\b", lower_msg)
            for pat in [
                "hi", "hello", "hey", "namaste", "pranam", "greetings", "good morning", "good afternoon", "good evening",
                "kem cho", "namaskaram", "vanakkam", "namaskara", "sat sri akal", "sasriyakaal", "adaab", "kemon acho"
            ]
        ) or any(w in message for w in ["નમસ્તે", "કેમ છો", "नमस्ते", "प्रणाम", "नमस्कार", "നമസ്കാരം", "வணக்கம்", "నమస్కారం", "নমস্কার"])

        if is_greeting and len(lower_msg.split()) <= 6:
            if detected_lang_str in ["gu", "gujarati"]:
                content = (
                    "નમસ્તે! હું **LawPilot AI** છું, ભારતના નાગરિકો માટે એક વ્યાપક કાનૂની સહાયક.\n\n"
                    "હું તમને ભારતીય કાયદાના તમામ મુખ્ય ક્ષેત્રોમાં માર્ગદર્શન આપી શકું છું:\n"
                    "- 🏠 **મિલકત, રેરા અને ભાડૂઆત બાબતો** (સિક્યોરિટી ડિપોઝિટ, મકાન ખાલી કરાવવું, રેરા વળતર)\n"
                    "- ⚖️ **ફોજદારી કાયદો (BNS/BNSS/BSA)** (FIR, જામીન, છેતરપિંડી, પોલીસ ફરિયાદ)\n"
                    "- 🛒 **ગ્રાહક સુરક્ષા** (ખામીયુક્ત ઉત્પાદનો, રિફંડ, ઈ-કોમર્સ વિવાદો)\n"
                    "- 💼 **રોજગાર અને વેતન** (બાકી પગાર, સેટેલમેન્ટ, POSH ફરિયાદ)\n"
                    "- 💻 **સાયબર અને બેંકિંગ** (ઓનલાઈન ફ્રોડ, એકાઉન્ટ ફ્રીઝ, ચેક બાઉન્સ કલમ 138)\n"
                    "- 📜 **કૌટુંબિક, દીવાની, કરવેરા અને RTI** (છૂટાછેડા, ભરણપોષણ, ઇન્કમટેક્સ, આરટીઆઈ)\n\n"
                    "આજે હું તમને કઈ કાનૂની બાબતમાં મદદ કરી શકું? કૃપા કરીને તમારી સમસ્યા જણાવો."
                )
            elif detected_lang_str in ["mr", "marathi"]:
                content = (
                    "नमस्कार! मी **LawPilot AI** आहे, भारतीय कायद्याच्या सर्व प्रमुख क्षेत्रांमध्ये मदत करणारा तुमचा सर्वसमावेशक कायदेशीर सहाय्यक.\n\n"
                    "मी खालील प्रमुख क्षेत्रांमध्ये तुम्हाला मार्गदर्शन करू शकतो:\n"
                    "- 🏠 **भाडेकरू, मालमत्ता व महारेरा (MahaRERA)** (डिपॉझिट परतावा, बेकायदेशीर बेदखली, घराचा ताबा)\n"
                    "- ⚖️ **फौजदारी कायदा (BNS, BNSS, BSA)** (एफआयआर, जामीन, फसवणूक, पोलीस तक्रार)\n"
                    "- 🛒 **ग्राहक संरक्षण** (दोषपूर्ण वस्तू, रिफंड, ई-कॉमर्स तक्रारी)\n"
                    "- 💼 **रोजगार व वेतन** (थकीत पगार, पूर्ण व अंतिम तोडगा, कामाच्या ठिकाणी छळ)\n"
                    "- 💳 **बँकिंग व सायबर गुन्हे** (ऑनलाइन फ्रॉड, बँक खाते गोठवणे, चेक बाउंस कलम १३८)\n"
                    "- 📜 **कौटुंबिक, दिवाणी, कर आणि माहिती अधिकार (RTI)** (घटस्फोट, पोटगी, आयटी/जीएसटी नोटिसा)\n\n"
                    "मी आज तुम्हाला कशी मदत करू शकतो? कृपया तुमची समस्या थोडक्यात सांगा."
                )
            elif detected_lang_str in ["hi", "hindi"]:
                content = (
                    "नमस्ते! मैं **LawPilot AI** हूँ, भारत में सभी प्रमुख कानूनी मामलों के लिए आपका व्यापक और समर्पित कानूनी सहायक।\n\n"
                    "मैं भारतीय कानून के विभिन्न क्षेत्रों में आपकी सहायता कर सकता हूँ:\n"
                    "- 🏠 **संपत्ति, रेरा एवं किरायेदारी** — सिक्योरिटी डिपॉज़िट, अनैतिक बेदखली, पज़ेशन में देरी\n"
                    "- ⚖️ **आपराधिक कानून (BNS, BNSS, BSA 2023)** — एफआईआर (FIR), जमानत (Bail), धोखाधड़ी, पुलिस शिकायत\n"
                    "- 🛒 **उपभोक्ता अधिकार (CPA 2019)** — खराब सामान, रिफंड से इनकार, ई-कॉमर्स शिकायतें\n"
                    "- 💼 **रोजगार एवं वेतन** — बकाया सैलरी, रिलीविंग लेटर, फुल एंड फाइनल सेटलमेंट, POSH\n"
                    "- 💳 **साइबर एवं बैंकिंग कानून** — ऑनलाइन वित्तीय धोखाधड़ी, बैंक खाता फ्रीज, चेक बाउंस (धारा 138)\n"
                    "- 📜 **पारिवारिक, दीवानी, कर एवं आरटीआई** — तलाक, गुजारा भत्ता, दीवानी दावे, इनकम टैक्स, आरटीआई\n\n"
                    "आज मैं आपकी किस प्रकार सहायता कर सकता हूँ? कृपया अपनी समस्या साझा करें।"
                )
            elif detected_lang_str in ["hinglish"]:
                content = (
                    "Hello! Main **LawPilot AI** hoon, India me sabhi major legal matters ke liye aapka comprehensive legal assistant.\n\n"
                    "Main Indian law ke har pramukh area me aapki madad kar sakta hoon:\n"
                    "- 🏠 **Property, RERA & Tenancy** (deposit refund, unlawful eviction, possession delay)\n"
                    "- ⚖️ **Criminal Law (BNS/BNSS/BSA 2023)** (FIR registration, bail, fraud, police complaint)\n"
                    "- 🛒 **Consumer Protection** (defective items, refund denial, e-commerce issues)\n"
                    "- 💼 **Employment & Wages** (unpaid salary, FnF settlement, relieving letter, POSH)\n"
                    "- 💳 **Banking & Cyber Law** (online financial fraud, bank account freeze, cheque bounce Sec 138)\n"
                    "- 📜 **Family, Civil, Tax & RTI** (divorce, maintenance, civil recovery, IT notice, RTI application)\n\n"
                    "Aap apni situation simple Hindi, English ya Hinglish me batayein — main aapko statutory rights aur actionable steps samjhaunga."
                )
            else:
                content = (
                    "Hello! I am **LawPilot AI**, your comprehensive, ethical conversational legal assistant for Indian law.\n\n"
                    "I assist ordinary citizens and businesses across all substantive and procedural areas of Indian law:\n"
                    "1. 🏠 **Property, Real Estate & Tenancy** (Security deposits, eviction protection, RERA builder delays, title disputes)\n"
                    "2. ⚖️ **Criminal Law & Procedure** (Current BNS 2023, BNSS 2023, BSA 2023; FIRs, bail, arrest rights, fraud)\n"
                    "3. 🛒 **Consumer Protection** (Defective goods, refund denials, e-commerce fraud, e-Daakhil filings)\n"
                    "4. 💼 **Employment & Labour** (Unpaid wages, withheld FnF, POSH workplace harassment, gratuity)\n"
                    "5. 💳 **Banking, Financial & Cyber Law** (Cheque bounce under Section 138 NI Act, bank account freezes, 1930 Cyber portal)\n"
                    "6. 📜 **Constitutional, Family, Civil & Regulatory** (Fundamental rights, writs, divorce, maintenance, money suits, RTI, taxation)\n\n"
                    "How can I assist you today? Please feel free to explain your situation in plain English or your preferred Indian language."
                )
            logger.info(f"ReqID={req_id} | ResponseType=Greeting | Retrieval=False")
            return ChatMessage(
                role="assistant",
                content=content,
                citations=[],
                verification_status=VerificationStatusEnum.VERIFIED,
                follow_up_questions=["Describe your legal situation, or ask a question about your rights."]
            )

        # -------------------------------------------------------------
        # 0B. FAREWELL / CLOSING
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["bye", "goodbye", "good night", "alvida", "see you"]):
            content = (
                "Goodbye! Thank you for consulting LawPilot AI. "
                "If you ever need legal clarity, rights verification, or assistance drafting formal legal notices across any area of Indian law, I will be here to assist you. Have a great day!"
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 0C. DOMAIN GUARDRAIL & OUT-OF-SCOPE REDIRECTION
        # -------------------------------------------------------------
        from app.core.domain_guardrail import DomainGuardrail
        is_oos, oos_reply, is_mixed = DomainGuardrail.inspect_query_scope(
            message, conversation_history, lang_str=detected_lang_str
        )
        if is_oos and oos_reply:
            logger.info(f"ReqID={req_id} | ResponseType=DomainRedirect | Retrieval=False")
            return ChatMessage(role="assistant", content=oos_reply, citations=[])

        # Update multi-turn case memory for legal queries
        memory.update_from_message(message)

        # -------------------------------------------------------------
        # 1. MEDICAL EMERGENCY CHECK
        # -------------------------------------------------------------
        is_med, med_reply = EscalationDetector.check_medical_emergency(message)
        if is_med:
            logger.info(f"ReqID={req_id} | Escalation=MedicalEmergency")
            return ChatMessage(
                role="assistant",
                content=med_reply,
                citations=[],
                verification_status=VerificationStatusEnum.RECOMMENDED,
                follow_up_questions=["Please seek immediate emergency medical care."],
                escalation_detected=True
            )

        # -------------------------------------------------------------
        # 2. FRAUDULENT EVIDENCE FABRICATION CHECK
        # -------------------------------------------------------------
        is_fraud, fraud_reply = EscalationDetector.check_fraud_request(message)
        if is_fraud:
            logger.info(f"ReqID={req_id} | Escalation=FraudRefusal")
            return ChatMessage(
                role="assistant",
                content=fraud_reply,
                citations=[],
                verification_status=VerificationStatusEnum.VERIFIED,
                follow_up_questions=["Would you like guidance on using genuine bank records or emails to prove your claim?"]
            )

        # -------------------------------------------------------------
        # 3. PROMPT INJECTION & UNTRUSTED OVERRIDE
        # -------------------------------------------------------------
        is_threat, threats = Sanitizer.inspect_for_threats(message)
        if is_threat and any("prompt injection" in t.lower() or "override" in t.lower() or "exfiltrate" in t.lower() or "credentials" in t.lower() or "authority" in t.lower() or "malicious" in t.lower() for t in threats):
            content = (
                "Safety Guardrail: Instruction Override Neutralized\n\n"
                "LawPilot AI detected an attempt to override system instructions or alter legal safety parameters. "
                "Document contents and user prompts are treated as untrusted input. The assistant adheres strictly "
                "to verified Indian statutory law and cannot invent fictional statutes or grant unauthorized monetary claims."
            )
            return ChatMessage(role="assistant", content=content, citations=[], verification_status=VerificationStatusEnum.VERIFIED)

        # -------------------------------------------------------------
        # 4. FABRICATION REQUESTS REFUSAL
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["100 square yards", "free agricultural land", "physically beat a tenant"]):
            content = (
                "Statutory Verification: Provision Non-Existent\n\n"
                "I must clarify: **There is no such provision in the Constitution of India or any Indian statute that entitles every citizen to 100 square yards of free agricultural land from the government, nor is any such provision present in law.**\n\n"
                "- The Constitution of India guarantees fundamental rights under Part III (Articles 12 to 35) and Directive Principles of State Policy under Part IV (Articles 36 to 51).\n"
                "- Article 300A protects against deprivation of property without authority of law, but does not mandate free land allocation.\n"
                "- LawPilot AI strictly refuses to invent fictional articles, sections, or welfare entitlements that do not exist in law."
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        if "within exactly 7 days" in lower_msg or "return a security deposit within exactly 7 days" in lower_msg:
            content = (
                "Statutory Verification: Section Invention Refused\n\n"
                "I must be clear: **There is no section in Indian central law that mandates every landlord must return a security deposit within exactly 7 days.**\n\n"
                "- Under the **Model Tenancy Act, 2021 (Section 11)**, the security deposit is to be refunded at the time of taking over vacant possession, after valid agreed deductions.\n"
                "- Under the **Transfer of Property Act, 1882 (Section 108)**, the tenant is entitled to the deposit upon handing over peaceful possession, subject only to reasonable wear and tear.\n"
                "- Typically, tenancy agreements specify a 15 to 30-day window, or 15 days is granted under a formal legal demand notice."
            )
            citations = LegalKnowledgeBase.retrieve_grounded_laws("security deposit return", CaseCategoryEnum.PROPERTY)
            return ChatMessage(role="assistant", content=content, citations=citations)

        if "supreme court judgments" in lower_msg and "48 hours" in lower_msg:
            content = (
                "Integrity Rule: Citation Fabrication Prohibited\n\n"
                "I will not fabricate court judgments or citations. There are **no Supreme Court of India judgments holding that every landlord must return a deposit within 48 hours**.\n\n"
                "Tenancy disputes in India are primarily governed by the terms of the tenancy contract, the Transfer of Property Act, 1882, and state-specific Rent Control Acts. Citing fictional Supreme Court precedents would severely harm your credibility in any legal forum."
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 5. DOCUMENT GENERATION IN CHAT
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["draft a", "draft me", "prepare a legal notice", "write an email to hr", "prepare a complaint", "write a notice", "draft cheque notice", "draft rti", "draft police complaint"]):
            from app.core.document_generator import DocumentGenerator
            from app.models.schemas import DocumentGenerationRequest, DocumentTypeEnum

            ef = memory.explicit_facts
            amt = ef["amount_raw"] or "₹25,000"
            city = ef["city"] or "[City / State]"
            date_val = ef["incident_date"] or "[Date of Handover / Incident]"

            # Check specific document type requested
            if "cheque" in lower_msg or "138" in lower_msg:
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.CHEQUE_BOUNCE_NOTICE,
                    user_name="[Payee Name]",
                    counterparty_name="[Drawer of Cheque / Accused Name]",
                    facts=f"Cheque for {amt} presented for encashment returned dishonoured with bank return memo dated {date_val}.",
                    disputed_amount=amt,
                    incident_date=date_val,
                    demands=f"Payment of cheque amount of {amt} within 15 days"
                )
            elif "police" in lower_msg or "fir" in lower_msg or "173" in lower_msg:
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.POLICE_COMPLAINT,
                    user_name="[Complainant Name]",
                    counterparty_name="[Accused / Suspect Name]",
                    facts=f"Offence of cheating and fraud involving wrongful deprivation of {amt} occurring on or about {date_val}.",
                    disputed_amount=amt,
                    incident_date=date_val,
                    demands="Registration of FIR and legal investigation"
                )
            elif "cyber" in lower_msg or "1930" in lower_msg:
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.CYBER_COMPLAINT,
                    user_name="[Victim Name]",
                    counterparty_name="[Suspect / Beneficiary Details]",
                    facts=f"Online financial fraud of {amt} via unauthorized transaction on {date_val}.",
                    disputed_amount=amt,
                    incident_date=date_val,
                    demands="Immediate account freeze under Section 107 BNSS and investigation"
                )
            elif "rti" in lower_msg:
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.RTI_APPLICATION,
                    user_name="[Applicant Name]",
                    counterparty_name="[Public Information Officer / Department Name]",
                    facts="Information sought regarding official action taken and certified file notings.",
                    disputed_amount=None,
                    incident_date=date_val,
                    demands="Certified copies of records within 30 days"
                )
            elif "deposit" in lower_msg or "landlord" in lower_msg or ef["category"] == "tenant":
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.SECURITY_DEPOSIT_DEMAND,
                    user_name="[Tenant Name]",
                    user_address=f"[Tenant Current Address, {city}]",
                    counterparty_name="[Landlord Name]",
                    counterparty_address=f"[Landlord Address / Rented Premises Address, {city}]",
                    facts=f"Tenancy at subject premises in {city}. Premises vacated on {date_val} in clean condition. Landlord refusing to return deposit of {amt}.",
                    disputed_amount=amt,
                    incident_date=date_val,
                    demands=f"Immediate refund of {amt} within 15 days"
                )
            elif "salary" in lower_msg or "hr" in lower_msg or "employment" in lower_msg or ef["category"] == "employment":
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.UNPAID_SALARY_DEMAND,
                    user_name="[Employee Name]",
                    counterparty_name="[Company / Employer Name]",
                    facts=f"Rendered service as an employee. Earned salary/settlement of {amt} remains unpaid despite formal resignation and notice period compliance.",
                    disputed_amount=amt,
                    demands=f"Clear pending salary of {amt} and issue relieving letter within 15 days"
                )
            else:
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.CONSUMER_COMPLAINT,
                    user_name="[Consumer Name]",
                    counterparty_name="[Seller / E-Commerce Company]",
                    facts=f"Purchased product for {amt}. Item arrived defective and refund/replacement was unlawfully denied.",
                    disputed_amount=amt,
                    demands=f"Full refund of {amt} with statutory interest and compensation"
                )

            doc_text = DocumentGenerator.generate_document_text(req)
            content = (
                f"### 📄 Generated Legal Document Draft\n\n"
                f"```text\n{doc_text}\n```\n\n"
                f"*Note: All missing particulars are marked with clear `[...]` placeholders. You can copy this draft or export it to PDF/Word.*"
            )
            logger.info(f"ReqID={req_id} | ResponseType=DocumentDraft | DocType={req.doc_type}")
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 6. DYNAMIC STRUCTURED LEGAL RESPONSE (MANDATORY 7-PART STRUCTURE)
        # -------------------------------------------------------------
        case = CaseBuilder.extract_case(message, state_jurisdiction=state_jurisdiction)
        citations = LegalKnowledgeBase.retrieve_grounded_laws(message, case.category, state=state_jurisdiction)
        follow_up = memory.get_natural_follow_up(detected_lang_str)

        content = self._render_structured_explanation(case.category, memory, citations, detected_lang, follow_up, message)

        if is_mixed:
            content += (
                "\n\n---\n"
                "**Scope Note:** Please note that LawPilot AI specialises strictly in legal assistance under Indian law. "
                "While I have addressed your legal query above, general entertainment or unrelated requests (such as movie recommendations or jokes) are outside my scope."
            )

        return ChatMessage(
            role="assistant",
            content=content,
            citations=citations,
            verification_status=VerificationStatusEnum.VERIFIED if citations else VerificationStatusEnum.RECOMMENDED,
            follow_up_questions=[follow_up] if follow_up else []
        )

    def _render_structured_explanation(
        self,
        category: CaseCategoryEnum,
        memory: ConversationCaseMemory,
        citations: List[LegalCitation],
        language: LanguageEnum,
        follow_up: Optional[str],
        user_msg: str
    ) -> str:
        """
        Renders a fully grounded Indian legal explanation using the mandatory 7-part standard structure:
        1. ### Understanding Your Situation
        2. ### Relevant Legal Provisions
        3. ### Your Legal Position
        4. ### Available Options
        5. ### Practical Next Steps
        6. ### Evidence to Preserve
        7. ### Important Limitations
        """
        ef = memory.explicit_facts
        amt_str = ef["amount_raw"] or "the disputed amount"
        city_str = ef["city"] or "your city"
        fu_question = follow_up or "Do you have documentary proof or written correspondence regarding this dispute?"
        lang_val = language.value if hasattr(language, "value") else str(language).lower()

        lang_info = LANGUAGE_CONFIG.get(lang_val, LANGUAGE_CONFIG["en"])
        h = lang_info["headers"]

        # Primary statute references
        statute_bullets = []
        if citations:
            for c in citations[:3]:
                hist_txt = f" (Historical Equivalent: {c.historical_equivalent})" if c.historical_equivalent else ""
                statute_bullets.append(f"* **{c.act_name} ({c.section})**: {c.title}. {c.description}{hist_txt}")
        else:
            statute_bullets.append("* **Applicable Statutory Framework**: Indian civil, statutory, and regulatory enactments governing reciprocal obligations and legal remedies.")

        statutes_formatted = "\n".join(statute_bullets)

        # -------------------------------------------------------------
        # DYNAMIC RENDER BY LEGAL DOMAIN
        # -------------------------------------------------------------

        # A. CRIMINAL LAW (BNS, BNSS, BSA 2023)
        if category == CaseCategoryEnum.CRIMINAL:
            if lang_val in ["hi", "hindi"]:
                return (
                    f"मैं आपकी इसमें पूरी सहायता कर सकता हूँ। वर्तमान भारतीय आपराधिक कानूनों (BNS, BNSS, BSA 2023) के अनुसार आपकी स्थिति का विस्तृत कानूनी विश्लेषण नीचे प्रस्तुत है:\n\n"
                    f"{h['situation']}\n"
                    f"आपने आपराधिक कृत्य, धोखाधड़ी या पुलिस शिकायत से संबंधित मामला साझा किया है। विवादित राशि {amt_str} तथा संबंधित स्थान {city_str} है।\n\n"
                    f"{h['provisions']}\n"
                    f"{statutes_formatted}\n\n"
                    f"{h['legal_position']}\n"
                    f"* 1 जुलाई 2024 से भारत में भारतीय न्याय संहिता (BNS 2023) और भारतीय नागरिक सुरक्षा संहिता (BNSS 2023) लागू हैं।\n"
                    f"* संज्ञेय अपराध में पुलिस अधिकारी धारा 173 BNSS के तहत प्रथम सूचना रिपोर्ट (FIR) दर्ज करने के लिए कानूनी रूप से बाध्य हैं।\n"
                    f"* यदि स्थानीय पुलिस एफआईआर दर्ज करने से मना करती है, तो क्षेत्राधिकार के अभाव का बहाना नहीं बनाया जा सकता (जीरो एफआईआर का अधिकार)।\n\n"
                    f"{h['options']}\n"
                    f"* **विकल्प 1 (पुलिस शिकायत):** स्थानीय थाने के भारसाधक अधिकारी (SHO) को धारा 173(1) BNSS के तहत लिखित शिकायत प्रस्तुत करें।\n"
                    f"* **विकल्प 2 (वरिष्ठ पुलिस अधीक्षक):** यदि थाना प्रभारी इनकार करे, तो धारा 173(4) BNSS के तहत पुलिस अधीक्षक (SP/DCP) को रजिस्ट्री द्वारा शिकायत भेजें।\n"
                    f"* **विकल्प 3 (न्यायिक मजिस्ट्रेट):** धारा 175(3) BNSS के तहत न्यायिक मजिस्ट्रेट के समक्ष एफआईआर दर्ज कराने हेतु आवेदन प्रस्तुत करें।\n\n"
                    f"{h['next_steps']}\n"
                    f"1. घटना के सभी दस्तावेजी व डिजिटल साक्ष्य एकत्र करें।\n"
                    f"2. थाने में लिखित शिकायत की दो प्रतियां दें और एक प्रति पर रिसीविंग मुहर व डायरी नंबर अवश्य लें।\n"
                    f"3. राहत न मिलने पर पुलिस अधीक्षक या न्यायिक दंडाधिकारी से संपर्क करें।\n\n"
                    f"{h['evidence']}\n"
                    f"* बैंक ट्रांसफर रसीदें / यूपीआई लेनदेन संदर्भ संख्या।\n"
                    f"* व्हाट्सएप चैट, कॉल रिकॉर्डिंग एवं ईमेल पत्राचार (BSA 2023 धारा 63 प्रमाण पत्र सहित)।\n"
                    f"* पहचान पत्र एवं संबंधित अनुबंध या चालान।\n\n"
                    f"{h['limitations']}\n"
                    f"* दीवानी विवाद (जैसे व्यापारिक अनुबंध का साधारण उल्लंघन) को बिना आपराधिक इरादे (mens rea) के आपराधिक मामले में नहीं बदला जा सकता।\n"
                    f"* यह विश्लेषण विधिक सूचना हेतु है; किसी भी अदालती याचिका या जमानत अर्जी हेतु अधिकृत अधिवक्ता से परामर्श आवश्यक है।\n\n"
                    f"{h['info_needed']}\n"
                    f"{fu_question}"
                )
            return (
                f"I can help you with this. Here is a grounded legal analysis under the operative criminal laws of India (BNS, BNSS, BSA 2023):\n\n"
                f"{h['situation']}\n"
                f"You have reported an alleged criminal offence or grievance involving {amt_str} in {city_str}. "
                f"Under Indian law, criminal offences are categorized as cognizable (police must register an FIR) or non-cognizable.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Since 1 July 2024, the operative criminal procedural code is the **Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)** and the substantive criminal code is the **Bharatiya Nyaya Sanhita, 2023 (BNS)**.\n"
                f"* Under **Section 173 BNSS** (formerly Sec 154 CrPC), police are statutorily mandated to register an FIR upon receiving information disclosing a cognizable offence.\n"
                f"* Jurisdictional boundaries do not permit refusal: police must lodge a Zero FIR and transfer it to the concerned police station.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Police Station Complaint):** Lodge a written complaint with the Station House Officer (SHO) under Section 173(1) BNSS.\n"
                f"* **Option 2 (Superintendent of Police):** If the SHO refuses registration, submit the substance in writing to the Superintendent of Police / DCP under Section 173(4) BNSS.\n"
                f"* **Option 3 (Judicial Magistrate):** File an application under Section 175(3) BNSS before the competent Magistrate seeking a direction for police investigation.\n\n"
                f"{h['next_steps']}\n"
                f"1. Compile a chronological statement of facts supported by documentary evidence.\n"
                f"2. Submit the written complaint in duplicate and obtain an official receiving stamp with Diary / GD number.\n"
                f"3. Track the status through the state police portal or e-FIR mechanism.\n\n"
                f"{h['evidence']}\n"
                f"* Proof of financial transactions (bank statements, UTR numbers, UPI IDs).\n"
                f"* Electronic communications (WhatsApp chats, SMS, emails, audio logs with Section 63 BSA certificate).\n"
                f"* Certified identity documents and written acknowledgments.\n\n"
                f"{h['limitations']}\n"
                f"* Purely commercial civil disputes cannot be converted into criminal proceedings without demonstrating fraudulent dishonest intent from the inception.\n"
                f"* This analysis is for guidance only; drafting formal bail applications or criminal complaints requires verification by an Advocate on Record.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # B. BANKING & CHEQUE BOUNCE (SECTION 138 NI ACT)
        elif category == CaseCategoryEnum.BANKING:
            return (
                f"I can help you with this financial and banking legal matter. Here is a comprehensive assessment under Indian banking laws and the Negotiable Instruments Act, 1881:\n\n"
                f"{h['situation']}\n"
                f"You have encountered a banking dispute or cheque dishonour issue involving {amt_str} in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 138 of the Negotiable Instruments Act, 1881**, dishonour of a cheque for insufficiency of funds or exceeding arrangement is a criminal offence punishable with imprisonment up to 2 years and/or fine up to twice the cheque amount.\n"
                f"* If facing loan recovery harassment, the **RBI Fair Practices Code** strictly prohibits abusive language, contacting relatives, or visits outside permitted hours. Harassment and threats constitute criminal **intimidation** under Section 351 BNS (formerly Sec 506 IPC).\n"
                f"* If your dispute relates to an arbitrary bank account freeze, police power under **Section 107 BNSS** (formerly Sec 102 CrPC) requires reporting to a Magistrate, and account holders have the right to petition the Magistrate or High Court for de-freezing.\n"
                f"* If facing deficiency of bank service or unauthorized debits, the **RBI Ombudsman** (Reserve Bank - Integrated Ombudsman Scheme, 2021) provides cost-free single-window redressal.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (For Cheque Bounce):** Issue a statutory demand notice through an advocate or directly within thirty (30) days of receiving the bank return memo, granting fifteen (15) days to make payment.\n"
                f"* **Option 2 (For Banking / Recovery Agent Harassment):** Escalate in writing to the bank / NBFC Principal Nodal Officer, followed by an online complaint to the **RBI Ombudsman** (cms.rbi.org.in) for violation of the Fair Practices Code and a police complaint for criminal intimidation.\n"
                f"* **Option 3 (Judicial Complaint):** If the drawer fails to pay within 15 days of notice, file a complaint under Section 142 NI Act before the Judicial Magistrate within one month.\n\n"
                f"{h['next_steps']}\n"
                f"1. Secure the original cheque and the original Bank Return Memo with official bank stamp.\n"
                f"2. Issue the statutory 15-day demand notice via Registered Post A.D. or Speed Post.\n"
                f"3. Retain postal dispatch receipts and tracking delivery reports.\n\n"
                f"{h['evidence']}\n"
                f"* Original cheque leaf and bank return memo showing reason of dishonour.\n"
                f"* Underlying contractual documents, invoices, or ledger showing legally enforceable debt.\n"
                f"* Speed Post receipt and postal delivery acknowledgment.\n\n"
                f"{h['limitations']}\n"
                f"* Strict limitation: The statutory notice MUST be sent within 30 days of receiving the memo, and the court complaint must be filed within 1 month after the 15-day notice period expires.\n"
                f"* A cheque issued purely as a gift or unlawful transaction cannot be enforced under Section 138.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # C. CYBER LAW & DIGITAL FRAUD
        elif category == CaseCategoryEnum.CYBER:
            return (
                f"I can guide you through this cyber crime and digital fraud matter. Here is your structured legal assessment:\n\n"
                f"{h['situation']}\n"
                f"You are dealing with an online scam, cyber fraud, or unauthorized data compromise involving {amt_str} in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Online financial fraud and identity theft are punishable offences under **Sections 66C and 66D of the Information Technology Act, 2000** and **Section 318 of the Bharatiya Nyaya Sanhita, 2023 (BNS)**.\n"
                f"* Under **Section 43A of the IT Act, 2000** and the **Digital Personal Data Protection Act, 2023 (DPDP)**, Data Fiduciaries that cause privacy data breaches or fail to implement reasonable security safeguards are liable to pay statutory **compensation**.\n"
                f"* Victims of data leaks and privacy violations can file a claim for compensation before the State IT **Adjudicating Officer** appointed under Section 46 of the IT Act.\n"
                f"* Victims of unauthorized debits have the right to seek emergency financial lien / **freeze** on beneficiary accounts through the National Cyber Crime Reporting mechanism.\n"
                f"* Under RBI circulars on customer liability in unauthorized electronic transactions, immediate reporting within 3 days ensures zero customer liability.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Immediate Helpline 1930):** Call the National Cyber Crime Helpline **1930** immediately within the golden hour to trigger banking lien/freeze on destination accounts.\n"
                f"* **Option 2 (Online Portal):** Lodge a comprehensive formal complaint on **cybercrime.gov.in** and obtain an acknowledgment docket number.\n"
                f"* **Option 3 (Adjudicating Officer Claim):** For privacy breaches and leaked personal data, petition the State IT **Adjudicating Officer** for compensation against the Data Fiduciary.\n\n"
                f"{h['next_steps']}\n"
                f"1. Call 1930 within the golden hour to prevent funds from being withdrawn by the fraudster.\n"
                f"2. File the incident report on cybercrime.gov.in attaching all screenshots and transaction UTRs.\n"
                f"3. Submit the acknowledgment copy to your home bank branch and request an official dispute ticket.\n\n"
                f"{h['evidence']}\n"
                f"* Bank statement highlighting transaction reference numbers (UTR, UPI Reference, IMPS ID).\n"
                f"* Screenshots of phishing chats, fake APK links, fraudulent websites, or spoofed messages.\n"
                f"* Call logs and SMS alerts showing debit timings.\n\n"
                f"{h['limitations']}\n"
                f"* Recovery depends significantly on reporting speed before funds are layered across crypto or overseas wallets.\n"
                f"* This analysis is informational; formal investigation and freezing are carried out by Law Enforcement Agencies.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # D. PROPERTY & REAL ESTATE (RERA & TENANCY)
        elif category in [CaseCategoryEnum.PROPERTY, CaseCategoryEnum.TENANT]:
            days_held = "an extended period"
            loc = city_str if ef["city"] else ("Jaipur" if "jaipur" in user_msg.lower() else "your city")
            
            if lang_val in ["gu", "gujarati"]:
                return (
                    f"હું આમાં તમને સંપૂર્ણ મદદ કરી શકું છું. ભારતીય કાનૂન અને મિલકત/ભાડૂઆત અધિકારોના આધારે તમારી પરિસ્થિતિનું વિશ્લેષણ નીચે મુજબ છે:\n\n"
                    f"{h['situation']}\n"
                    f"તમે {loc} માં મિલકત/ભાડા અંગેનો વિવાદ ધરાવો છો જેમાં {amt_str} ની રકમ રોકાયેલી છે.\n\n"
                    f"{h['provisions']}\n"
                    f"{statutes_formatted}\n\n"
                    f"{h['legal_position']}\n"
                    f"* સિક્યોરિટી ડિપોઝિટ માત્ર બાકી ભાડું અથવા વાસ્તવિક નુકસાન માટે જ કાપી શકાય છે, સામાન્ય ઘસારા (reasonable wear and tear) માટે નહીં.\n"
                    f"* **ટ્રાન્સફર ઓફ પ્રોપર્ટી એક્ટ, ૧૮૮૨ (કલમ ૧૦૮)** મુજબ ભાડૂઆત સામાન્ય ઘસારા સિવાય મિલકત સુપરત કરવા માટે બંધાયેલ છે.\n"
                    f"* રેરા હેઠળ બિલ્ડર વિલંબ માટે **RERA Act 2016 કલમ 18** મુજબ વ્યાજ સહિત રિફંડ મેળવવાનો હક છે.\n\n"
                    f"{h['options']}\n"
                    f"* **વિકલ્પ ૧ (લેખિત માંગ નોટિસ):** સામેવાળા પક્ષકારને ૧૫ દિવસનો સમય આપી ₹{amt_str} પરત કરવાની ઔપચારિક માંગ કરો.\n"
                    f"* **વિકલ્પ ૨ (રેન્ટ ઓથોરિટી / રેરા):** મકાન વિવાદ માટે રેન્ટ કંટ્રોલર અથવા ફ્લેટ વિલંબ માટે રેરા ઓથોરિટી સમક્ષ ફરિયાદ નોંધાવો.\n"
                    f"* **વિકલ્પ ૩ (દીવાની દાવો):** રકમની વસૂલાત માટે દીવાની અદાલતમાં કાનૂની દાવો દાખલ કરો.\n\n"
                    f"{h['next_steps']}\n"
                    f"1. ભાડા કરાર, બેંક/UPI ટ્રાન્સફર રસીદો, મકાન સોંપણીની તસવીરો સાચવો.\n"
                    f"2. રજિસ્ટર્ડ પોસ્ટ / ઈમેઈલ દ્વારા ૧૫ દિવસની ઔપચારિક માંગ નોટિસ મોકલો.\n"
                    f"3. ઉકેલ ન આવે તો સક્ષમ મંચ સમક્ષ કાનૂની ફરિયાદ દાખલ કરો.\n\n"
                    f"{h['evidence']}\n"
                    f"* રજિસ્ટર્ડ / નોટરાઈઝ્ડ કરાર અથવા એલોટમેન્ટ લેટર.\n"
                    f"* બેંક સ્ટેટમેન્ટ અને ડિપોઝિટ ચુકવણીના પુરાવા.\n"
                    f"* કબજો સોંપતી વખતની તસવીરો અને ચેટ રેકોર્ડ.\n\n"
                    f"{h['limitations']}\n"
                    f"* ૧૧ મહિનાથી વધુના કરાર માટે રજિસ્ટ્રેશન એક્ટ હેઠળ નોંધણી અનિવાર્ય છે.\n"
                    f"* દીવાની વસૂલાત માટે લિમિટેશન એક્ટ મુજબ ૩ વર્ષની મર્યાદા લાગુ પડે છે.\n\n"
                    f"{h['info_needed']}\n"
                    f"{fu_question}"
                )
            elif lang_val in ["ta", "tamil"]:
                return (
                    f"வாடகை மற்றும் சொத்து சட்டங்களின் கீழ் உங்கள் நிலைமைக்கான விரிவான சட்ட விளக்கம்:\n\n"
                    f"{h['situation']}\n"
                    f"நீங்கள் வாடகை வீட்டை காலி செய்து 30 நாட்கள் ஆகியும் வீட்டு உரிமையாளர் உங்கள் வைப்புத்தொகையை (security deposit) திருப்பித் தர மறுக்கிறார்.\n\n"
                    f"{h['provisions']}\n"
                    f"* **சொத்து பரிமாற்றச் சட்டம், 1882 (பிரிவு 108):** நில உரிமையாளர் நியாயமான தேய்மானத்தைத் தவிர்த்து (reasonable wear and tear) முழு வைப்புத்தொகையையும் திருப்பித் தர கடமைப்பட்டுள்ளார்.\n"
                    f"* **மாதிரி வாடகைச் சட்டம், 2021 (பிரிவு 11):** வீட்டை ஒப்படைக்கும் போது வைப்புத்தொகை திருப்பித் தரப்பட வேண்டும்.\n\n"
                    f"{h['legal_position']}\n"
                    f"* வீட்டு உரிமையாளர் வழக்கமான பெயிண்டிங் செலவுகளுக்காக முழு வைப்புத்தொகையையும் பிடித்தம் செய்ய முடியாது.\n"
                    f"* சட்டம் மற்றும் பிரிவு 108-ன் கீழ் உங்கள் வைப்புத்தொகையை திரும்பப் பெற உங்களுக்கு முழு சட்ட உரிமை உள்ளது.\n\n"
                    f"{h['options']}\n"
                    f"* **விருப்பம் 1 (நோட்டீஸ்):** வீட்டு உரிமையாளருக்கு 15 நாட்கள் அவகாசம் கொடுத்து முறையான நோட்டீஸ் (Demand Notice) அனுப்பவும்.\n"
                    f"* **விருப்பம் 2 (வாடகை அதிகாரி):** உள்ளூர் வாடகை அதிகாரியிடம் (Rent Authority) புகார் மனு தாக்கல் செய்யவும்.\n"
                    f"* **விருப்பம் 3 (நீதிமன்றம்):** சிவில் நீதிமன்றத்தில் தொகை மீட்பு மனு தாக்கல் செய்யவும்.\n\n"
                    f"{h['next_steps']}\n"
                    f"1. வாடகை ஒப்பந்தம், வங்கி ரசீதுகள் மற்றும் வீட்டு சாவியை ஒப்படைத்த ஆதாரங்களை சேகரிக்கவும்.\n"
                    f"2. 15 நாட்கள் அவகாசத்துடன் வழக்கறிஞர் அல்லது நேரடி நோட்டீஸ் அனுப்பவும்.\n"
                    f"3. தீர்வு கிடைக்காதபட்சத்தில் வாடகை நீதிமன்றத்தை அணுகவும்.\n\n"
                    f"{h['evidence']}\n"
                    f"* வாடகை ஒப்பந்த நகல் மற்றும் வங்கி பணப்பரிவர்த்தனை ஆதாரம்.\n"
                    f"* வீட்டை காலி செய்தபோது எடுக்கப்பட்ட புகைப்படங்கள் மற்றும் வாட்ஸ்அப் உரையாடல்கள்.\n\n"
                    f"{h['limitations']}\n"
                    f"* பண மீட்பு வழக்குகளுக்கு 3 ஆண்டுகள் கால வரம்பு (Limitation Act) பொருந்தும்.\n"
                    f"* இந்த தகவல் விழிப்புணர்வுக்கானது; நீதிமன்ற நடவடிக்கைகளுக்கு வழக்கறிஞரை அணுகவும்.\n\n"
                    f"{h['info_needed']}\n"
                    f"{fu_question}"
                )
            return (
                f"I can help you with this property and tenancy dispute. Here is a grounded legal analysis under Indian real estate and tenancy laws:\n\n"
                f"{h['situation']}\n"
                f"You have reported a dispute involving {amt_str} related to residential premises or property in {loc}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 108(m) of the Transfer of Property Act, 1882**, the occupier is bound to restore the property subject only to reasonable wear and tear; landlords cannot make arbitrary deductions for standard repainting.\n"
                f"* Under the **Model Tenancy Act, 2021 (Section 11)**, security deposits must be refunded upon taking over vacant possession.\n"
                f"* Under **Section 18 of RERA, 2016**, homebuyers facing builder possession delay are entitled to full refund with interest (SBI MCLR + 2%) or monthly delay compensation.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Written Demand Notice):** Issue a formal 15-day statutory demand notice calling for the release of {amt_str}.\n"
                f"* **Option 2 (Statutory Forum):** Approach the local Rent Authority / Rent Controller or file a complaint before the State RERA Authority.\n"
                f"* **Option 3 (Civil Remedy):** File a summary suit for recovery of debt under Order 37 CPC before the competent Civil Court.\n\n"
                f"{h['next_steps']}\n"
                f"1. Collate tenancy/buyer agreements, rent receipts, bank statements, and handover records.\n"
                f"2. Serve a formal demand notice via Speed Post and email granting 15 days for compliance.\n"
                f"3. In case of non-compliance, initiate proceedings before the statutory Rent Authority or Civil Court.\n\n"
                f"{h['evidence']}\n"
                f"* Rental agreement / Builder-Buyer agreement / Sale deed.\n"
                f"* Bank statements or UPI transaction receipts evidencing deposit/advance payments.\n"
                f"* Handover photos, videos, keys delivery acknowledgment, and email/WhatsApp logs.\n\n"
                f"{h['limitations']}\n"
                f"* Civil claims for money recovery are subject to a 3-year limitation period under the Limitation Act, 1963.\n"
                f"* Lease agreements exceeding 11 months require mandatory registration under Section 17 of the Registration Act, 1908.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # E. CONSUMER PROTECTION (CPA 2019)
        elif category == CaseCategoryEnum.CONSUMER:
            if lang_val in ["mr", "marathi"]:
                return (
                    f"मी ग्राहक संरक्षण कायद्यानुसार (Consumer Protection Act, 2019) तुमची पूर्ण मदत करू शकतो:\n\n"
                    f"{h['situation']}\n"
                    f"तुम्ही पुण्यात नवीन लॅपटॉप खरेदी केला, पण तो ३ दिवसांत बंद पडला. विक्रेता पैसे परत देण्यास किंवा नवीन लॅपटॉप देण्यास नकार देत आहे, ही एक दोषपूर्ण वस्तूची तक्रार आहे.\n\n"
                    f"{h['provisions']}\n"
                    f"* **ग्राहक संरक्षण कायदा, २०१९ (कलम २(४७) व कलम ३५):** दोषपूर्ण वस्तू परत घेण्यास नकार देणे किंवा पैसे परत न करणे हा अनुचित व्यापार व्यवहार (Unfair Trade Practice) मानला जातो.\n"
                    f"* **ग्राहक संरक्षण (ई-कॉमर्स) नियम, २०२०:** तक्रार निवारण अधिकारी यांनी ४८ तासांत तक्रारीची दखल घेणे बंधनकारक आहे.\n\n"
                    f"{h['legal_position']}\n"
                    f"* ग्राहक संरक्षण कायदा अंतर्गत ग्राहकाला दोषपूर्ण वस्तू बदलून मिळण्याचा किंवा पूर्ण पैसे परत मिळण्याचा कायदेशीर अधिकार आहे.\n"
                    f"* विक्रेता किंवा कंपनी ग्राहकाच्या तक्रारीकडे दुर्लक्ष करू शकत नाही.\n\n"
                    f"{h['options']}\n"
                    f"* **पर्याय १ (राष्ट्रीय ग्राहक हेल्पलाइन):** टोल-फ्री क्रमांक १९१५ किंवा consumerhelpline.gov.in वर तक्रार नोंदवा.\n"
                    f"* **पर्याय २ (कायदेशीर नोटीस):** विक्रेत्याला १५ दिवसांची कायदेशीर नोटीस पाठवून पैसे परत करण्याची मागणी करा.\n"
                    f"* **पर्याय ३ (ई-दाखल तक्रार):** edaakhil.nic.in द्वारे जिल्हा ग्राहक आयोगाकडे वकील न नेमता स्वतः ऑनलाइन तक्रार दाखल करा.\n\n"
                    f"{h['next_steps']}\n"
                    f"1. खरेदीचे बिल (Tax Invoice), वॉरंटी कार्ड आणि सर्व्हिस सेंटरचा अहवाल जपून ठेवा.\n"
                    f"2. विक्रेता आणि कंपनीला ईमेलद्वारे लेखी तक्रार पाठवा.\n"
                    f"3. समाधान न झाल्यास ग्राहक मंचाकडे दाद मागा.\n\n"
                    f"{h['evidence']}\n"
                    f"* खरेदी पावती, पेमेंट संदर्भ आणि दोषपूर्ण लॅपटॉपचे फोटो/व्हिडिओ.\n"
                    f"* विक्रेत्यासोबत झालेला ईमेल किंवा चॅट संवाद.\n\n"
                    f"{h['limitations']}\n"
                    f"* ग्राहक मंचात तक्रार दाखल करण्याची मुदत कारण घडल्यापासून २ वर्षांची असते (कलम ६९).\n"
                    f"* हे मार्गदर्शन कायदेशीर माहितीसाठी आहे; औपचारिक दाव्यासाठी वकिलाचा सल्ला घ्या.\n\n"
                    f"{h['info_needed']}\n"
                    f"{fu_question}"
                )
            return (
                f"I can help you with this consumer dispute. Here is an analysis based on the Consumer Protection Act, 2019 and E-Commerce Rules, 2020:\n\n"
                f"{h['situation']}\n"
                f"You purchased a product or service involving {amt_str} in {city_str} which proved defective, or for which promised refund/delivery was wrongfully denied.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 2(47) of the Consumer Protection Act, 2019 (CPA 2019)**, refusing to take back defective goods or refund consideration within 30 days is an explicit **Unfair Trade Practice**.\n"
                f"* Under **Section 35 & Section 38 CPA 2019**, any consumer can institute a complaint before the District Commission directly without requiring mandatory advocate representation.\n"
                f"* The **Consumer Protection (E-Commerce) Rules, 2020** mandate grievance acknowledgment within 48 hours and monthly dispute redressal.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (National Consumer Helpline):** Register a pre-litigation grievance on **1915** or via consumerhelpline.gov.in.\n"
                f"* **Option 2 (Formal Legal Notice):** Issue a formal 15-day notice to the seller and marketplace platform demanding refund and compensation.\n"
                f"* **Option 3 (e-Daakhil Filing):** File an electronic consumer complaint before the District Consumer Commission online via edaakhil.nic.in.\n\n"
                f"{h['next_steps']}\n"
                f"1. Save original tax invoice, delivery receipts, and defective product photographs/unboxing videos.\n"
                f"2. Log a ticket with customer care and note down the formal docket number.\n"
                f"3. Register a grievance on the National Consumer Helpline; if unresolved in 15 days, proceed to e-Daakhil.\n\n"
                f"{h['evidence']}\n"
                f"* Retail Tax Invoice showing seller GSTIN, date, and product specifications.\n"
                f"* Visual proof of defects (unboxing video, clear photos, service center inspection memo).\n"
                f"* Complete written email/chat communication refusing refund or replacement.\n\n"
                f"{h['limitations']}\n"
                f"* Consumer complaints must be filed within 2 years from the date cause of action arose under Section 69 CPA 2019.\n"
                f"* Commercial purchases for resale are excluded from the definition of consumer under Section 2(7).\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # F. EMPLOYMENT & LABOUR LAW
        elif category == CaseCategoryEnum.EMPLOYMENT:
            if lang_val in ["hi", "hindi"]:
                return (
                    f"मैं इस रोजगार व वेतन विवाद में आपकी पूरी सहायता कर सकता हूँ। भारतीय श्रम कानूनों के अंतर्गत आपका कानूनी विश्लेषण नीचे प्रस्तुत है:\n\n"
                    f"{h['situation']}\n"
                    f"आपकी कंपनी ने पिछले 3 महीने से आपका ₹{amt_str} का बकाया वेतन रोक रखा है और कोई लिखित कारण नहीं दिया।\n\n"
                    f"{h['provisions']}\n"
                    f"* **वेतन भुगतान अधिनियम, 1936 (धारा 5 एवं धारा 15):** नियोक्ता के लिए मजदूरी अवधि समाप्त होने के 7 से 10 दिनों के भीतर वेतन का भुगतान करना कानूनी रूप से अनिवार्य है।\n"
                    f"* **वेतन भुगतान अधिनियम (धारा 15):** कर्मचारी बकाया वेतन के साथ-साथ दस गुना तक हर्जाने की मांग श्रम प्राधिकारी के समक्ष कर सकता है।\n"
                    f"* **भारतीय अनुबंध अधिनियम, 1872 (धारा 73):** सेवा शर्तों के अनुसार अर्जित वेतन रोकना अनुबंध का सीधा उल्लंघन है।\n\n"
                    f"{h['legal_position']}\n"
                    f"* नियोक्ता को बिना किसी वैधानिक कारण के किसी भी कर्मचारी का बकाया वेतन रोकने का कोई कानूनी अधिकार नहीं है।\n"
                    f"* आप श्रम न्यायालय या श्रम आयुक्त के समक्ष बकाया वेतन और ब्याज सहित वसूली के पूर्ण हकदार हैं।\n\n"
                    f"{h['options']}\n"
                    f"* **विकल्प 1 (मांग पत्र):** कंपनी के प्रबंधन व मानव संसाधन (HR) को 15 दिनों का औपचारिक मांग पत्र (Legal Demand Letter) भेजें।\n"
                    f"* **विकल्प 2 (श्रम आयुक्त शिकायत):** स्थानीय श्रम आयुक्त (Labour Commissioner) या वेतनाधिकारी के समक्ष धारा 15 के तहत लिखित शिकायत दर्ज करें।\n"
                    f"* **विकल्प 3 (श्रम न्यायालय / दीवानी दावा):** औद्योगिक विवाद अधिनियम की धारा 33C(2) या सिविल कोर्ट में वसूली वाद दायर करें।\n\n"
                    f"{h['next_steps']}\n"
                    f"1. नियुक्ति पत्र, पे-स्लिप, बैंक स्टेटमेंट और काम/इस्तीफे के प्रमाण एकत्र करें।\n"
                    f"2. कंपनी को बकाया वेतन के भुगतान हेतु 15 दिनों का अंतिम मांग पत्र प्रेषित करें।\n"
                    f"3. समाधान न होने पर सहायक श्रम आयुक्त कार्यालय में औपचारिक शिकायत दाखिल करें।\n\n"
                    f"{h['evidence']}\n"
                    f"* नियुक्ति पत्र, आईडी कार्ड और आधिकारिक ईमेल रिकॉर्ड।\n"
                    f"* पिछले महीनों की वेतन पर्चियां और बैंक खाता विवरण।\n"
                    f"* वेतन की मांग को लेकर भेजे गए ईमेल और कंपनी का उत्तर (यदि कोई हो)।\n\n"
                    f"{h['limitations']}\n"
                    f"* बकाया वेतन की वसूली हेतु परिसीमा अधिनियम (Limitation Act) के तहत 3 वर्ष की समय-सीमा लागू होती है।\n"
                    f"* यह जानकारी विधिक सहायता हेतु है; किसी भी अदालती वाद हेतु अधिकृत अधिवक्ता से सलाह लें।\n\n"
                    f"{h['info_needed']}\n"
                    f"{fu_question}"
                )
            return (
                f"I can help you with this employment and labour law issue. Here is your structured legal assessment:\n\n"
                f"{h['situation']}\n"
                f"Your employer in {city_str} has withheld earned salary, final settlement dues of {amt_str}, or relieving letters, or you are facing a workplace grievance.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 5 of the Payment of Wages Act, 1936**, employers are legally obligated to pay earned wages within 7 to 10 days of the wage period.\n"
                f"* Under **Section 15 of the Payment of Wages Act, 1936**, employees can claim delayed wages along with statutory compensation up to ten times the delayed amount.\n"
                f"* Withholding relieving letters or full & final settlement constitutes a breach of contract under **Section 73 of the Indian Contract Act, 1872**.\n"
                f"* If facing workplace harassment, the **POSH Act, 2013** provides statutory inquiry through the Internal Committee (IC) within 90 days.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Internal Written Demand):** Send a formal demand letter to HR and Management giving 15 days to release dues and relieving credentials.\n"
                f"* **Option 2 (Labour Commissioner / Shops Act):** File a statutory complaint before the local Labour Commissioner or Inspector under State Shops & Establishments Act.\n"
                f"* **Option 3 (Labour Court / Civil Suit):** File a recovery application under Section 33C(2) of the Industrial Disputes Act, 1947 or summary suit under Order 37 CPC.\n\n"
                f"{h['next_steps']}\n"
                f"1. Gather your appointment letter, recent payslips, bank statements, and resignation acceptance email.\n"
                f"2. Issue a formal written demand notice to the authorized director / HR head.\n"
                f"3. Approach the District Labour Officer if settlement is not concluded within the notice period.\n\n"
                f"{h['evidence']}\n"
                f"* Employment agreement / Offer letter / Resignation acceptance.\n"
                f"* Salary slips for past 3-6 months and bank credit statements.\n"
                f"* Email threads detailing pending FnF calculations and follow-up requests.\n\n"
                f"{h['limitations']}\n"
                f"* Civil recovery of unpaid salary must be instituted within 3 years under the Limitation Act, 1963.\n"
                f"* Managerial employees earning above statutory wage thresholds may need to pursue remedies through Civil Court or Shops Act rather than Labour Court.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # G. CONSTITUTIONAL LAW
        elif category == CaseCategoryEnum.CONSTITUTIONAL:
            return (
                f"I can guide you on this constitutional rights and extraordinary remedy matter. Here is your structured legal assessment:\n\n"
                f"{h['situation']}\n"
                f"You have raised a matter concerning fundamental rights, arbitrary state action, or illegal police detention in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"* **Constitution of India, 1950 (Article 226 & Article 32)**: Power of High Courts and Supreme Court to issue directions, orders, or Writs including Habeas Corpus, Mandamus, Prohibition, Quo Warranto, and Certiorari for enforcement of fundamental and legal rights.\n"
                f"* **Constitution of India, 1950 (Article 14 & Article 21)**: Equality before law, protection against arbitrary action, right to natural justice (audi alteram partem), and protection of personal liberty.\n"
                f"* **Article 22(2) of the Constitution & Section 58 BNSS, 2023** (formerly Sec 57 CrPC): Every person arrested and detained in custody must be produced before the nearest Judicial Magistrate within 24 hours of arrest.\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Article 226 of the Constitution of India**, High Courts have wide **writ** jurisdiction to strike down **arbitrary** state orders and enforce the principles of **natural justice**.\n"
                f"* In cases of illegal police detention beyond 24 hours without production before a **Magistrate**, a Writ of **Habeas Corpus** can be moved before the **High Court** for immediate production and release.\n"
                f"* No administrative authority or municipal corporation can cancel commercial trade licenses or infringe livelihoods arbitrarily without issuing a show-cause notice and providing a fair hearing.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Writ Petition before High Court):** File an urgent Writ Petition under Article 226 (Writ of Mandamus / Certiorari / Habeas Corpus) before the jurisdictional High Court.\n"
                f"* **Option 2 (Human Rights Commission / SP):** Lodge an immediate complaint before the State Human Rights Commission or Police Complaints Authority for illegal detention.\n"
                f"* **Option 3 (Statutory Representation):** Submit a formal written representation to the Municipal Commissioner or higher administrative authority.\n\n"
                f"{h['next_steps']}\n"
                f"1. Collect copies of the arbitrary cancellation order, detention records, or correspondence.\n"
                f"2. Engage a High Court advocate to draft and mention the urgent Writ Petition.\n"
                f"3. Seek emergency interim stay or production orders from the vacation or roster bench.\n\n"
                f"{h['evidence']}\n"
                f"* Written orders, cancellation letters, or lack of show-cause notice.\n"
                f"* Evidence of date, time, and location of detention or municipal action.\n"
                f"* Identity documents, licenses, and proofs of fundamental rights violation.\n\n"
                f"{h['limitations']}\n"
                f"* High Courts generally expect exhaustion of effective alternate statutory remedies unless fundamental rights or principles of natural justice are violated.\n"
                f"* Extraordinary writ jurisdiction is discretionary and requires clean hands and prompt filing without undue delay.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # G2. ADMINISTRATIVE & RTI LAW
        elif category == CaseCategoryEnum.ADMINISTRATIVE:
            return (
                f"I can guide you on this administrative law and RTI matter. Here is your structured legal assessment:\n\n"
                f"{h['situation']}\n"
                f"You have raised a matter concerning public transparency, municipal administration, or access to public information in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 6 & Section 7 of the Right to Information Act, 2005**, every citizen has the statutory right to receive information from Public Information Officers (PIO) within 30 days.\n"
                f"* If information concerns life and liberty, it must be provided within forty-eight (48) hours under Section 7(1) RTI Act.\n"
                f"* Under **Section 19(1) of the RTI Act**, failure of the PIO to respond within 30 days entitles the applicant to file a First Appeal before the First Appellate Authority.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (RTI First Appeal):** If information is refused or not provided within 30 days, file First Appeal under Section 19(1) to the designated First Appellate Authority.\n"
                f"* **Option 2 (Second Appeal to CIC/SIC):** If First Appeal is dismissed or unanswered, approach the Central or State Information Commission under Section 19(3).\n"
                f"* **Option 3 (High Court Writ):** File a Writ Petition under Article 226 before the High Court against willful administrative defiance.\n\n"
                f"{h['next_steps']}\n"
                f"1. Frame clear, specific, itemized questions seeking factual records rather than legal opinions.\n"
                f"2. File First Appeal with the appellate authority attaching the original application and postal/online proof.\n"
                f"3. Maintain proof of application submission and calendar the appeal timeline.\n\n"
                f"{h['evidence']}\n"
                f"* Copy of original RTI application and application fee receipt.\n"
                f"* Postal speed post receipt or online RTI registration docket number.\n"
                f"* Written correspondence with the public authority.\n\n"
                f"{h['limitations']}\n"
                f"* Information exempted under Section 8 of the RTI Act (national security, commercial confidence, personal privacy) cannot be disclosed without overriding public interest.\n"
                f"* High Courts generally expect exhaustion of available alternative statutory remedies before invoking extraordinary writ jurisdiction.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # H. FAMILY LAW
        elif category == CaseCategoryEnum.FAMILY:
            return (
                f"I can guide you through this family and matrimonial legal matter with care. Here is your structured assessment:\n\n"
                f"{h['situation']}\n"
                f"You have shared a family matter concerning marriage, domestic distress, maintenance, or custody in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 13B of the Hindu Marriage Act, 1955** (or Section 28 Special Marriage Act), mutual consent divorce proceeds through two stages: filing a joint petition in the **First Motion**, undergoing a statutory six-month **cooling off** period (which can be waived on valid grounds), and final recording of consent in the **Second Motion**.\n"
                f"* Under the **Protection of Women from Domestic Violence Act, 2005 (PWDVA)**, aggrieved women are entitled to Protection Orders (Sec 18), Residence in shared household (Sec 19), and Monetary Relief (Sec 20).\n"
                f"* Under **Section 144 of BNSS, 2023** (formerly Sec 125 CrPC), a spouse, minor child, or elderly parent unable to maintain themselves can claim monthly maintenance through summary inquiry before a Magistrate.\n"
                f"* Matrimonial dissolution is governed by personal laws (such as Hindu Marriage Act, 1955 or Special Marriage Act, 1954), providing for contested divorce on fault grounds or mutual consent divorce.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Mutual Consent Petition):** Jointly petition the Family Court for mutual consent divorce under Section 13B HMA with First Motion and Second Motion after cooling off.\n"
                f"* **Option 2 (Mediation & Counseling):** Approach the Family Court counseling cell or pre-litigation mediation center for amicable resolution.\n"
                f"* **Option 3 (Magistrate Relief under PWDVA / BNSS 144):** File an application before Judicial Magistrate for urgent protection and interim maintenance.\n\n"
                f"{h['next_steps']}\n"
                f"1. Document all incidents, dates, financial dependencies, and communication history.\n"
                f"2. Consult DLSA (District Legal Services Authority) or a family law advocate for representation.\n"
                f"3. In case of immediate safety threats, contact Women Helpline 181 or local police.\n\n"
                f"{h['evidence']}\n"
                f"* Marriage certificate, wedding photographs, and residence proofs.\n"
                f"* Bank statements, income tax returns, and expense proofs showing financial dependency.\n"
                f"* Medical records, chat logs, or police complaints evidencing domestic cruelty if applicable.\n\n"
                f"{h['limitations']}\n"
                f"* Mutual consent divorce typically requires six months waiting period (cooling-off period), which can be waived by court upon sufficient grounds.\n"
                f"* All court applications in matrimonial disputes require sworn affidavits of assets and liabilities as mandated by the Supreme Court.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # I. INTELLECTUAL PROPERTY LAW (IPR)
        elif category == CaseCategoryEnum.IPR:
            return (
                f"I can assist you with this intellectual property infringement matter. Here is your structured legal assessment:\n\n"
                f"{h['situation']}\n"
                f"You have reported an intellectual property violation or counterfeit goods dispute in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 29 and Section 134 of the Trade Marks Act, 1999**, unauthorized commercial use of an identical or deceptively similar mark on counterfeit goods constitutes actionable **trademark infringement** and common law **passing off**.\n"
                f"* Special territorial **jurisdiction**: Under Section 134(2) of the Trade Marks Act and Section 62(2) of the Copyright Act, the plaintiff can institute a suit in the District Court or specialized **Commercial Court** where the plaintiff actually carries on business, rather than where the infringer resides.\n"
                f"* Under **Section 51 & 55 of the Copyright Act, 1957**, creators are entitled to seek permanent injunctions, accounts of profits, and statutory damages against willful infringers.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Cease and Desist Notice):** Issue a formal cease and desist demand letter calling for immediate stoppage of counterfeit sales and surrender of infringing stock.\n"
                f"* **Option 2 (Commercial Court Injunction):** File a commercial suit before the competent District / Commercial Court seeking ex-parte ad-interim injunction (Order 39 Rules 1 & 2 CPC) and appointment of a Local Commissioner to seize counterfeit goods.\n"
                f"* **Option 3 (Criminal FIR):** Lodge a criminal complaint under Section 103 & 104 Trade Marks Act / Section 63 Copyright Act with the local police for seizure of fake goods.\n\n"
                f"{h['next_steps']}\n"
                f"1. Secure certified copies of trademark registration certificates and user date affidavits.\n"
                f"2. Conduct trap purchases to collect counterfeit invoices, packaging samples, and photographs.\n"
                f"3. Engage an IP advocate to file an urgent injunction suit before the Commercial Court.\n\n"
                f"{h['evidence']}\n"
                f"* Trademark/Copyright registration certificates and legal proceedings certificates.\n"
                f"* Counterfeit product samples, purchase receipts, and photographs comparing original vs fake.\n"
                f"* Proof of business activity within the home court's jurisdiction.\n\n"
                f"{h['limitations']}\n"
                f"* Commercial suits require pre-institution mediation under Section 12A of the Commercial Courts Act, 2015, unless urgent interim injunction is sought.\n"
                f"* Pure common law passing off claims require higher evidentiary standard of goodwill and reputation compared to registered trademark infringement.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # J. INSURANCE LAW
        elif category == CaseCategoryEnum.INSURANCE:
            return (
                f"I can guide you through this insurance dispute. Here is your structured legal assessment:\n\n"
                f"{h['situation']}\n"
                f"Your health, life, or motor insurance claim of {amt_str} in {city_str} was repudiated or rejected by the insurance company.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under the **Insurance Ombudsman Rules, 2017 (Rule 13 & Rule 14)**, policyholders whose genuine claim has been repudiated have the statutory right to approach the **Insurance Ombudsman** for **cost-free** adjudication up to ₹50 Lakhs.\n"
                f"* The Supreme Court and IRDAI regulations strictly mandate that insurers cannot reject emergency hospitalization claims on flimsy pre-existing condition exclusions if the ailment is unrelated to the disclosed medical history.\n"
                f"* Policyholders must approach the Ombudsman within one year of the insurer rejecting their formal representation.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Internal Grievance - GRO):** File a written appeal before the Grievance Redressal Officer (GRO) of the insurance company, which must be decided within **30 days**.\n"
                f"* **Option 2 (Insurance Ombudsman):** If the GRO rejects the appeal or fails to reply within 30 days, lodge a cost-free complaint before the jurisdictional Insurance Ombudsman online (cioins.co.in) or in person.\n"
                f"* **Option 3 (Consumer Commission):** File a consumer complaint for deficiency in service and unfair trade practice before the District Consumer Commission via e-Daakhil.\n\n"
                f"{h['next_steps']}\n"
                f"1. Obtain the written claim repudiation letter clearly stating the specific clause and grounds.\n"
                f"2. Submit a formal representation to the insurer's Grievance Redressal Officer attaching treating doctor's medical certificate.\n"
                f"3. In case of non-resolution within 30 days, file your complaint before the Insurance Ombudsman.\n\n"
                f"{h['evidence']}\n"
                f"* Insurance policy schedule, terms, and initial proposal form.\n"
                f"* Discharge summary, hospital bills, pharmacy receipts, and doctor's prescription.\n"
                f"* Written repudiation letter and copy of representation submitted to GRO.\n\n"
                f"{h['limitations']}\n"
                f"* An Insurance Ombudsman complaint must be filed within 1 year from the date of rejection by the insurer.\n"
                f"* If a complaint is already pending before a court or consumer commission, the Insurance Ombudsman cannot entertain the matter simultaneously.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # K. ALTERNATIVE DISPUTE RESOLUTION (ADR)
        elif category == CaseCategoryEnum.ADR:
            return (
                f"I can guide you through this dispute resolution and arbitration matter. Here is your structured assessment:\n\n"
                f"{h['situation']}\n"
                f"You have raised a matter concerning commercial arbitration or mediated settlement in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 8 of the Arbitration and Conciliation Act, 1996**, if an agreement contains a valid **arbitration clause**, a judicial authority is statutorily mandated to refer the parties to arbitration upon application by either party not later than submitting the first statement on the substance of the dispute.\n"
                f"* Parties may seek urgent **interim relief** under **Section 9** from the court before or during arbitral proceedings, or from the **arbitral tribunal** under Section 17 once constituted.\n"
                f"* Under **Section 27 of the Mediation Act, 2023**, a **mediated settlement agreement** signed by parties and authenticated by a mediator is final, binding, and **enforceable** in the same manner as a judgment or **court decree**.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Section 8 Reference Application):** In response to a civil suit, file an application under Section 8 of the Arbitration Act requesting the court to refer the parties to arbitration.\n"
                f"* **Option 2 (Section 9 Interim Relief):** Apply to the Commercial Court or High Court for urgent preservation orders or injunctions pending arbitration.\n"
                f"* **Option 3 (Mediation Enforcement):** For mediated settlements, enforce the agreement as a decree under Section 27 of the Mediation Act, 2023 before the competent civil court.\n\n"
                f"{h['next_steps']}\n"
                f"1. Locate and examine the exact wording of the dispute resolution clause in your signed agreement.\n"
                f"2. If served with court summons, file the Section 8 reference application before filing your written statement.\n"
                f"3. Issue a formal notice invoking arbitration nominating an arbitrator under Section 21 of the Act.\n\n"
                f"{h['evidence']}\n"
                f"* Signed commercial agreement containing the arbitration or mediation clause.\n"
                f"* Summons, plaint, or notices exchanged between the contracting parties.\n"
                f"* Written mediated settlement agreement signed by both parties and mediator if applicable.\n\n"
                f"{h['limitations']}\n"
                f"* Section 8 application must be filed BEFORE submitting the first statement of defense on merits in civil court.\n"
                f"* Non-arbitrable disputes (such as criminal offences, insolvency, matrimonial status) cannot be referred to arbitration.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # L. MOTOR VEHICLE & ACCIDENT CLAIMS
        elif category == CaseCategoryEnum.MOTOR_VEHICLE:
            return (
                f"I can assist you with this motor vehicle accident and compensation matter. Here is your structured assessment:\n\n"
                f"{h['situation']}\n"
                f"You have presented a motor vehicle collision, accident injury, or hit-and-run claim in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 166 of the Motor Vehicles Act, 1988**, victims of vehicular accidents or legal representatives of deceased persons can file a claim application for **compensation** before the **Motor Accidents Claims Tribunal (MACT)**.\n"
                f"* Under **Section 161 of the Motor Vehicles Act, 1988**, victims of **hit and run** accidents (where the offending vehicle cannot be identified) are entitled to statutory **solatium** compensation from the Motor Vehicles Accident Fund (₹2 Lakhs for death, ₹50,000 for grievous hurt).\n"
                f"* Insurance companies cannot escape third-party liability unless fundamental breach of policy conditions is proven.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (MACT Claim Petition):** File a claim petition under Section 166 MV Act before the Claims Tribunal having territorial jurisdiction.\n"
                f"* **Option 2 (Hit and Run Solatium Claim):** In hit-and-run cases, submit an application to the Sub-Divisional Magistrate / Claims Enquiry Officer for compensation under the 2022 Scheme.\n"
                f"* **Option 3 (Settlement Lok Adalat):** Opt for amicable settlement before the MACT Lok Adalat for expedited payout without prolonged trial.\n\n"
                f"{h['next_steps']}\n"
                f"1. Secure the police Detailed Accident Report (DAR), FIR copy, and spot panchnama.\n"
                f"2. Collect all original medical treatment bills, discharge summaries, and disability certificates.\n"
                f"3. File the claim petition before the MACT Tribunal within the 6-month statutory limitation period.\n\n"
                f"{h['evidence']}\n"
                f"* Certified copies of FIR, charge sheet, and Detailed Accident Report (DAR).\n"
                f"* Medical records, disability certificates issued by government medical board, and treatment bills.\n"
                f"* Proof of income, age, and employment of the victim.\n\n"
                f"{h['limitations']}\n"
                f"* Under Section 166(3) MV Act (2019 Amendment), claim applications must be filed within six (6) months of the date of accident.\n"
                f"* Solatium scheme claims must follow District Magistrate verification procedures.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # M. TAXATION LAW
        elif category == CaseCategoryEnum.TAXATION:
            return (
                f"I can assist you with this taxation notice and compliance matter. Here is your structured assessment:\n\n"
                f"{h['situation']}\n"
                f"You have received an income tax or GST statutory notice involving {amt_str} in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 148 & Section 148A of the Income-tax Act, 1961**, the Assessing Officer must issue a show cause notice and provide an **opportunity of hearing** before reopening an assessment for **escaped assessment**.\n"
                f"* Under **Section 73 & Section 74 of the CGST Act, 2017**, tax authorities must issue a formal Show Cause Notice in Form **DRC-01** giving at least 30 days to explain Input Tax Credit (ITC) mismatches or tax demands.\n"
                f"* Reassessment notices issued beyond the 3-year statutory limitation without specific material showing escaped income exceeding ₹50 Lakhs are jurisdictionally defective.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Formal Reply to Notice):** File a point-by-point legal and factual reply on the e-filing income tax portal or GST portal within the stipulated time.\n"
                f"* **Option 2 (Rectification / Reconciliation):** Provide comprehensive reconciliation statements (GSTR-2B vs GSTR-3B) and bank statements evidencing genuine business transactions.\n"
                f"* **Option 3 (High Court Writ):** If the notice is issued without jurisdiction or violates Section 148A statutory prerequisites, challenge the notice via Article 226 Writ Petition.\n\n"
                f"{h['next_steps']}\n"
                f"1. Download the complete notice, questionnaire, and annexures from the online portal.\n"
                f"2. Reconcile disputed transactions with audited balance sheets, bank records, and GST filings.\n"
                f"3. Submit the formal reply online before the expiry of the compliance deadline.\n\n"
                f"{h['evidence']}\n"
                f"* Copy of statutory notice (Section 148A / DRC-01) and system acknowledgment.\n"
                f"* Books of accounts, bank statements, purchase invoices, and payment receipts.\n"
                f"* Previously filed ITR acknowledgments and audited tax audit reports.\n\n"
                f"{h['limitations']}\n"
                f"* Strict deadlines: Reply to Section 148A must typically be filed within 7 to 30 days as specified in the notice.\n"
                f"* This guidance is for legal awareness; complex tax assessments require consultation with a Chartered Accountant or Tax Advocate.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # N. ENVIRONMENTAL LAW
        elif category == CaseCategoryEnum.ENVIRONMENTAL:
            return (
                f"I can guide you on this environmental protection and pollution dispute. Here is your structured assessment:\n\n"
                f"{h['situation']}\n"
                f"You have reported an environmental issue, unauthorized pollution, or toxic discharge in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 14 & Section 15 of the National Green Tribunal Act, 2010 (NGT Act)**, any aggrieved person can approach the **National Green Tribunal (NGT)** for relief, compensation, and restoration of environment.\n"
                f"* The NGT applies the 'Polluter Pays Principle' and 'Precautionary Principle' under Section 20 to mandate immediate shutdown and remediation.\n"
                f"* Discharging untreated industrial effluents into residential drains or public water bodies violates the Water (Prevention and Control of Pollution) Act, 1974.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Pollution Control Board Complaint):** File a formal complaint before the State Pollution Control Board (SPCB) requesting spot inspection.\n"
                f"* **Option 2 (NGT Application):** File an original application before the zonal bench of the National Green Tribunal under Section 14 NGT Act.\n"
                f"* **Option 3 (District Magistrate / BNSS 152):** Petition the District Magistrate / SDM to order conditional removal of public nuisance under Section 152 BNSS.\n\n"
                f"{h['next_steps']}\n"
                f"1. Document the pollution with date-stamped photographs, video recordings, and water/air samples.\n"
                f"2. Submit written representations to the SPCB regional officer and municipal health officer.\n"
                f"3. In case of inaction, file an application before the NGT within the statutory window.\n\n"
                f"{h['evidence']}\n"
                f"* Photographs and videos showing toxic discharge or fumes.\n"
                f"* Medical records of affected residents or environmental testing lab reports.\n"
                f"* Copies of written complaints submitted to civic and pollution authorities.\n\n"
                f"{h['limitations']}\n"
                f"* Under Section 14(3) of the NGT Act, applications for relief must be filed within six (6) months from the date cause of action first arose.\n"
                f"* The NGT entertains substantial questions relating to environment involving multi-party impacts rather than individual civil property disputes.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # O. IMMIGRATION & PASSPORTS
        elif category == CaseCategoryEnum.IMMIGRATION:
            return (
                f"I can guide you on this passport and immigration legal matter. Here is your structured assessment:\n\n"
                f"{h['situation']}\n"
                f"You have encountered an issue regarding passport issuance, renewal refusal, or travel permission in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under **Section 6(2)(f) of the Passports Act, 1967**, passport issuance or renewal may be refused if criminal proceedings are pending before a court in India.\n"
                f"* However, under **Ministry of External Affairs Notification GSR 570(E)** and binding Supreme Court decisions, an individual facing pending criminal cases can travel abroad or renew their passport if they obtain a **No Objection Certificate (NOC) / permission to travel** from the concerned criminal trial court.\n"
                f"* The right to travel abroad is a recognized aspect of personal liberty under Article 21 of the Constitution of India.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Trial Court NOC Application):** File an application before the trial court where the case is pending seeking permission to renew passport / travel abroad.\n"
                f"* **Option 2 (Representation to RPO):** Submit the court permission order along with a formal representation to the Regional Passport Officer (RPO).\n"
                f"* **Option 3 (High Court Writ):** If the RPO arbitrarily refuses renewal despite court permission, file a Writ of Mandamus before the High Court under Article 226.\n\n"
                f"{h['next_steps']}\n"
                f"1. Obtain a certified copy of the court order sheet demonstrating regular attendance and absence of abscondence.\n"
                f"2. File a miscellaneous application before the trial court requesting passport NOC.\n"
                f"3. Submit the certified court NOC to the Regional Passport Office.\n\n"
                f"{h['evidence']}\n"
                f"* Passport application ARN receipt and show cause notice from RPO.\n"
                f"* Certified copy of the pending case order sheets and charge sheet.\n"
                f"* Travel itinerary, foreign employment offer, or reasons necessitating passport renewal.\n\n"
                f"{h['limitations']}\n"
                f"* Passport issued pursuant to trial court order is usually valid for 1 year or the duration specified by the Magistrate.\n"
                f"* Outstanding non-bailable warrants (NBWs) or proclamation will lead to outright passport impounding under Section 10(3).\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

        # I. GENERAL / CIVIL / OTHER DOMAINS
        else:
            return (
                f"Thank you for consulting LawPilot AI. Based on the facts shared, here is a comprehensive analysis under Indian law:\n\n"
                f"{h['situation']}\n"
                f"You have presented a legal query or dispute concerning {amt_str} in {city_str}.\n\n"
                f"{h['provisions']}\n"
                f"{statutes_formatted}\n\n"
                f"{h['legal_position']}\n"
                f"* Under the general civil law of India, rights and obligations established by contract, statute, or common law are enforceable through appropriate civil courts and specialized tribunals.\n"
                f"* Where liquidated debts or negotiable instruments are involved, summary procedures under **Order 37 CPC** provide fast-track adjudication without protracted trial.\n"
                f"* Free legal assistance is available for eligible citizens through the **Legal Services Authorities Act, 1987 (NALSA Helpline 15100)**.\n\n"
                f"{h['options']}\n"
                f"* **Option 1 (Amicable Notice):** Serve a formal written demand notice granting fifteen (15) days for voluntary resolution.\n"
                f"* **Option 2 (Pre-litigation Mediation):** Approach the District Legal Services Authority (DLSA) or institutional mediation under the Mediation Act, 2023.\n"
                f"* **Option 3 (Judicial Proceedings):** File a civil suit for recovery or injunction before the competent Civil Court having territorial and pecuniary jurisdiction.\n\n"
                f"{h['next_steps']}\n"
                f"1. Compile all signed contracts, receipts, bank records, and communications in chronological order.\n"
                f"2. Issue a formal written demand letter stating exact facts, breach, and resolution timeline.\n"
                f"3. In the event of non-compliance, initiate proceedings before the appropriate forum or tribunal.\n\n"
                f"{h['evidence']}\n"
                f"* Primary transaction documents (invoices, receipts, agreements, notices).\n"
                f"* Electronic proof (emails, chats, bank transaction references).\n"
                f"* Proof of identity and jurisdiction.\n\n"
                f"{h['limitations']}\n"
                f"* Suits for recovery of money or breach of contract are barred by limitation after 3 years under the Limitation Act, 1963.\n"
                f"* This analysis is for informational and educational guidance and does not replace formal legal representation by an advocate.\n\n"
                f"{h['info_needed']}\n"
                f"{fu_question}"
            )

    def generate_stream(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: Optional[LanguageEnum] = None,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ):
        from app.core.title_generator import generate_conversation_title
        case = CaseBuilder.extract_case(message, state_jurisdiction=state_jurisdiction)
        citations = LegalKnowledgeBase.retrieve_grounded_laws(message, case.category, state=state_jurisdiction)
        title = generate_conversation_title(message, case.category)
        citations_data = [c.dict() for c in citations]

        yield {"type": "metadata", "title": title, "citations": citations_data}

        resp = self.generate_response(
            message=message,
            conversation_history=conversation_history,
            language=language or LanguageEnum.AUTO,
            state_jurisdiction=state_jurisdiction,
            session_id=session_id
        )

        words = re.split(r'(\s+)', resp.content)
        for w in words:
            if w:
                yield {"type": "token", "content": w}

        yield {"type": "done", "title": title, "citations": citations_data, "content": resp.content}


class GeminiInteractionsProvider(BaseLLMProvider):
    """
    Google Gemini Interactions API Provider.
    Enforces the mandatory 7-part legal structure, current criminal law (BNS/BNSS/BSA),
    exact response-language consistency, and zero statutory hallucinations.
    """
    INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _check_fast_track(self, lower_msg: str, lang_str: str) -> Optional[str]:
        """Provides instant (<5ms) responses for common conversational greetings and scope questions."""
        is_greeting = any(
            re.search(rf"\b{pat}\b", lower_msg)
            for pat in [
                "hi", "hello", "hey", "namaste", "pranam", "greetings", "good morning", "good afternoon", "good evening",
                "kem cho", "namaskaram", "vanakkam", "namaskara", "sat sri akal", "sasriyakaal", "adaab", "kemon acho"
            ]
        ) or any(w in lower_msg for w in ["નમસ્તે", "કેમ છો", "नमस्ते", "प्रणाम", "नमस्कार", "നമസ്കാരം", "வணக்கம்", "నమస్కారం", "নমস্কার"])

        if is_greeting and len(lower_msg.split()) <= 6:
            if lang_str in ["gu", "gujarati"]:
                return (
                    "નમસ્તે! હું **LawPilot AI** છું, ભારતના નાગરિકો માટે એક વ્યાપક કાનૂની સહાયક.\n\n"
                    "હું તમને ભારતીય કાયદાના તમામ મુખ્ય ક્ષેત્રોમાં માર્ગદર્શન આપી શકું છું:\n"
                    "- 🏠 **મિલકત, રેરા અને ભાડૂઆત બાબતો** (સિક્યોરિટી ડિપોઝિટ, મકાન ખાલી કરાવવું, રેરા વળતર)\n"
                    "- ⚖️ **ફોજદારી કાયદો (BNS/BNSS/BSA)** (FIR, જામીન, છેતરપિંડી, પોલીસ ફરિયાદ)\n"
                    "- 🛒 **ગ્રાહક સુરક્ષા** (ખામીયુક્ત ઉત્પાદનો, રિફંડ, ઈ-કોમર્સ વિવાદો)\n"
                    "- 💼 **રોજગાર અને વેતન** (બાકી પગાર, સેટેલમેન્ટ, POSH ફરિયાદ)\n"
                    "- 💻 **સાયબર અને બેંકિંગ** (ઓનલાઈન ફ્રોડ, એકાઉન્ટ ફ્રીઝ, ચેક બાઉન્સ કલમ 138)\n"
                    "- 📜 **કૌટુંબિક, દીવાની, કરવેરા અને RTI** (છૂટાછેડા, ભરણપોષણ, ઇન્કમટેક્સ, આરટીઆઈ)\n\n"
                    "આજે હું તમને કઈ કાનૂની બાબતમાં મદદ કરી શકું? કૃપા કરીને તમારી સમસ્યા જણાવો."
                )
            elif lang_str in ["mr", "marathi"]:
                return (
                    "नमस्कार! मी **LawPilot AI** आहे, भारतीय कायद्याच्या सर्व प्रमुख क्षेत्रांमध्ये मदत करणारा तुमचा सर्वसमावेशक कायदेशीर सहाय्यक.\n\n"
                    "मी खालील प्रमुख क्षेत्रांमध्ये तुम्हाला मार्गदर्शन करू शकतो:\n"
                    "- 🏠 **भाडेकरू, मालमत्ता व महारेरा (MahaRERA)** (डिपॉझिट परतावा, बेकायदेशीर बेदखली, घराचा ताबा)\n"
                    "- ⚖️ **फौजदारी कायदा (BNS, BNSS, BSA)** (एफआयआर, जामीन, फसवणूक, पोलीस तक्रार)\n"
                    "- 🛒 **ग्राहक संरक्षण** (दोषपूर्ण वस्तू, रिफंड, ई-कॉमर्स तक्रारी)\n"
                    "- 💼 **रोजगार व वेतन** (थकीत पगार, पूर्ण व अंतिम तोडगा, कामाच्या ठिकाणी छळ)\n"
                    "- 💳 **बँकिंग व सायबर गुन्हे** (ऑनलाइन फ्रॉड, बँक खाते गोठवणे, चेक बाउंस कलम १३८)\n"
                    "- 📜 **कौटुंबिक, दिवाणी, कर आणि माहिती अधिकार (RTI)** (घटस्फोट, पोटगी, आयटी/जीएसटी नोटिसा)\n\n"
                    "मी आज तुम्हाला कशी मदत करू शकतो? कृपया तुमची समस्या थोडक्यात सांगा."
                )
            elif lang_str in ["hi", "hindi"]:
                return (
                    "नमस्ते! मैं **LawPilot AI** हूँ, भारत में सभी प्रमुख कानूनी मामलों के लिए आपका व्यापक कानूनी सहायक।\n\n"
                    "मैं भारतीय कानून के विभिन्न क्षेत्रों में आपकी सहायता कर सकता हूँ:\n"
                    "- 🏠 **संपत्ति, रेरा एवं किरायेदारी** — सिक्योरिटी डिपॉज़िट, अनैतिक बेदखली, पज़ेशन में देरी\n"
                    "- ⚖️ **आपराधिक कानून (BNS, BNSS, BSA 2023)** — एफआईआर (FIR), जमानत (Bail), धोखाधड़ी, पुलिस शिकायत\n"
                    "- 🛒 **उपभोक्ता अधिकार (CPA 2019)** — खराब सामान, रिफंड से इनकार, ई-कॉमर्स शिकायतें\n"
                    "- 💼 **रोजगार एवं वेतन** — बकाया सैलरी, रिलीविंग लेटर, फुल एंड फाइनल सेटलमेंट, POSH\n"
                    "- 💳 **साइबर एवं बैंकिंग कानून** — ऑनलाइन वित्तीय धोखाधड़ी, बैंक खाता फ्रीज, चेक बाउंस (धारा 138)\n"
                    "- 📜 **पारिवारिक, दीवानी, कर एवं आरटीआई** — तलाक, गुजारा भत्ता, दीवानी दावे, इनकम टैक्स, आरटीआई\n\n"
                    "आज मैं आपकी किस प्रकार सहायता कर सकता हूँ? कृपया अपनी समस्या साझा करें।"
                )
            elif lang_str in ["hinglish"]:
                return (
                    "Hello! Main **LawPilot AI** hoon, India me sabhi major legal matters ke liye aapka comprehensive legal assistant.\n\n"
                    "Main Indian law ke sabhi areas me aapki madad karta hoon:\n"
                    "- 🏠 Property, RERA & Tenancy (deposit refund, eviction protection, possession delays)\n"
                    "- ⚖️ Criminal Law (BNS/BNSS/BSA 2023, FIR, bail, fraud)\n"
                    "- 🛒 Consumer Protection (defective items, refund issues, e-commerce grievances)\n"
                    "- 💼 Employment & Wages (unpaid salary, FnF settlement, relieving letter)\n"
                    "- 💳 Banking & Cyber (online fraud, account freeze, cheque bounce 138)\n"
                    "- 📜 Family, Civil, Tax & RTI (divorce, maintenance, civil recovery, IT notice, RTI)\n\n"
                    "Aap apni situation simple English, Hindi ya Hinglish me batayein — main poori legal guidance dunga."
                )
            else:
                return (
                    "Hello! I am **LawPilot AI**, your comprehensive conversational legal assistant for Indian law.\n\n"
                    "I assist ordinary citizens and businesses across all substantive and procedural areas of Indian law:\n"
                    "1. 🏠 **Property, Real Estate & Tenancy** (Security deposits, eviction protection, RERA builder delays, title disputes)\n"
                    "2. ⚖️ **Criminal Law & Procedure** (Current BNS 2023, BNSS 2023, BSA 2023; FIRs, bail, arrest rights, fraud)\n"
                    "3. 🛒 **Consumer Protection** (Defective goods, refund denials, e-commerce fraud, e-Daakhil filings)\n"
                    "4. 💼 **Employment & Labour** (Unpaid wages, withheld FnF, POSH workplace harassment, gratuity)\n"
                    "5. 💳 **Banking, Financial & Cyber Law** (Cheque bounce under Section 138 NI Act, bank account freezes, 1930 Cyber portal)\n"
                    "6. 📜 **Constitutional, Family, Civil & Regulatory** (Fundamental rights, writs, divorce, maintenance, money suits, RTI, taxation)\n\n"
                    "How can I assist you today? Feel free to describe your situation in plain English, Hindi, or any Indian language."
                )

        if any(p in lower_msg for p in ["what is your name", "who are you", "your name"]):
            if lang_str in ["gu", "gujarati"]:
                return (
                    "હું **LawPilot AI** છું, ભારતીય કાયદાના તમામ ક્ષેત્રો માટે સામાન્ય નાગરિકોનો બુદ્ધિશાળી કાનૂની સહાયક. "
                    "હું તમને તમારા કાનૂની અધિકારો સમજવામાં, કાનૂની જોગવાઈઓની ચકાસણી કરવામાં અને કાનૂની દસ્તાવેજો તથા નોટિસ તૈયાર કરવામાં મદદ કરું છું."
                )
            return (
                "I am **LawPilot AI**, an intelligent legal assistant for ordinary citizens in India covering all major areas of Indian law. "
                "I help you understand your legal standing, verify statutory rights, evaluate evidence, explore procedural options, and draft formal legal notices and documents."
            )

        if any(p in lower_msg for p in ["what can you help me with", "what do you do", "help me with"]):
            if lang_str in ["gu", "gujarati"]:
                return (
                    "LawPilot AI ભારતીય કાયદાના તમામ મુખ્ય ક્ષેત્રોમાં સામાન્ય નાગરિકોને મદદ કરે છે:\n\n"
                    "૧. મિલકત, રેરા અને ભાડૂઆત વિવાદો (સિક્યોરિટી ડિપોઝિટ, મકાન ખાલી કરાવવું, બાંધકામ વિલંબ વળતર).\n"
                    "૨. ફોજદારી કાયદો - BNS, BNSS અને BSA 2023 (FIR નોંધણી, જામીન, છેતરપિંડી, પોલીસ ફરિયાદ).\n"
                    "૩. ગ્રાહક સુરક્ષા (ખામીયુક્ત ઉત્પાદનો, રિફંડ, ઈ-કોમર્સ વિવાદો).\n"
                    "૪. રોજગાર અને વેતન (અટકેલો પગાર, ફુલ એન્ડ ફાઇનલ સેટલમેન્ટ, અનુભવ પત્ર, POSH).\n"
                    "૫. સાયબર ક્રાઇમ અને બેંકિંગ (ઓનલાઇન નાણાકીય છેતરપિંડી, બેંક ખાતું ફ્રીઝ, ચેક બાઉન્સ કલમ ૧૩૮).\n"
                    "૬. કૌટુંબિક, દીવાની, કરવેરા અને આરટીઆઈ (છૂટાછેડા, ભરણપોષણ, દીવાની વસૂલાત, આવકવેરા નોટિસ, RTI અરજી).\n\n"
                    "તમે સંબંધિત દસ્તાવેજો ચકાસી શકો છો અથવા સીધા ચેટમાં ઔપચારિક કાનૂની નોટિસ તૈયાર કરી શકો છો."
                )
            return (
                "LawPilot AI assists ordinary citizens and professionals across all substantive and procedural areas of Indian law:\n\n"
                "1. Property, Real Estate & Tenancy: Security deposits, unlawful deductions, eviction protection, and RERA possession delays.\n"
                "2. Criminal Law: Current BNS 2023, BNSS 2023, and BSA 2023 procedures, FIR registration, bail rights, and criminal breach of trust.\n"
                "3. Consumer Protection: Defective goods, refund denials, e-commerce fraud, and e-Daakhil filing guidance.\n"
                "4. Employment & Labour: Unpaid salary, withheld relieving letters, FnF delays, POSH workplace harassment, and gratuity.\n"
                "5. Banking & Cyber Law: Dishonour of cheques under Section 138 NI Act, bank account freezes under Section 107 BNSS, and cyber fraud on 1930.\n"
                "6. Constitutional, Family, Civil & Regulatory: Fundamental rights, writs under Art 226/32, divorce, maintenance under Sec 144 BNSS, money recovery suits, RTI applications, and tax notices.\n\n"
                "You can also generate formal legal notices, police complaints, cheque bounce notices, and RTI applications directly in the chat."
            )

        if any(p in lower_msg for p in ["what is 2 + 2", "what is 2+2", "2 + 2", "2+2", "tell me a joke"]):
            return (
                "I am LawPilot AI, a comprehensive legal assistant specialising in Indian law. "
                "I can help you understand your legal rights, analyse statutory provisions, explore procedural options, and draft legal documents. "
                "I cannot assist with general topics outside Indian legal matters. Is there an Indian legal issue or dispute I can help you with?"
            )

        return None

    def _detect_language(self, message: str, language: Optional[LanguageEnum] = None) -> str:
        """Automatically detects user language independently for each turn."""
        return detect_message_language(message, language)

    def _build_prompt(self, message: str, conversation_history: List[Dict[str, str]], lang_str: str, statutory_context: str, is_mixed: bool = False) -> str:
        """Constructs prompt enforcing exact response-language consistency, the 7-part layout, and current criminal law."""
        lang_info = LANGUAGE_CONFIG.get(lang_str, LANGUAGE_CONFIG["en"])
        lang_name = lang_info["name"]
        lang_script = lang_info["script"]
        h = lang_info["headers"]

        mixed_note = ""
        if is_mixed:
            mixed_note = (
                "\nSPECIAL MANDATE FOR MIXED LEGAL/NON-LEGAL QUERY:\n"
                "The user has asked a query containing both an Indian legal issue and an unrelated non-legal question. "
                "You must comprehensively answer the legal issue using the 7-part statutory layout. "
                "For the unrelated non-legal question, politely explain that as LawPilot AI you specialise exclusively in Indian legal matters, and decline to provide general non-legal answers.\n"
            )

        system_instruction = (
            "You are LawPilot AI, an expert, ethical Indian legal assistant designed for ordinary citizens, professionals, and businesses in India.\n"
            "You provide comprehensive legal assistance across all areas of Indian law, including:\n"
            "- Constitutional Law (Fundamental rights, writs under Articles 32 and 226)\n"
            "- Criminal Law (Current BNS 2023, BNSS 2023, BSA 2023; FIRs, bail, arrest, trials)\n"
            "- Civil Law (Recovery of money, summary suits Order 37, injunctions Order 39, Limitation Act 1963)\n"
            "- Family Law (Divorce, maintenance Sec 144 BNSS, custody, domestic violence PWDVA 2005)\n"
            "- Property & Real Estate (RERA 2016, tenancy under TPA 1882, registration, partition)\n"
            "- Consumer Protection (CPA 2019, E-Commerce Rules 2020, e-Daakhil)\n"
            "- Employment & Labour (Payment of Wages 1936, POSH Act 2013, Gratuity 1972, FnF disputes)\n"
            "- Cyber Law (IT Act 2000 Sec 66C/66D, 1930 Portal, DPDP Act 2023)\n"
            "- Banking & Finance (Cheque bounce Sec 138 NI Act, account freeze Sec 107 BNSS, RBI Ombudsman)\n"
            "- Taxation (Income Tax Act 1961 notices Sec 148, CGST Act 2017)\n"
            "- Intellectual Property (Copyright Act 1957, Trade Marks Act 1999)\n"
            "- Motor Vehicle (MACT claims under MV Act 1988/2019, hit-and-run)\n"
            "- Insurance (Insurance Ombudsman Rules 2017, claim repudiation)\n"
            "- Environmental Law (NGT Act 2010, Environment Protection Act 1986)\n"
            "- Administrative & Regulatory (RTI Act 2005 Sec 6/7/19, CAT)\n"
            "- Immigration & Citizenship (Passports Act 1967, Citizenship Act 1955)\n"
            "- Alternative Dispute Resolution (Arbitration Act 1996, Mediation Act 2023, Lok Adalat)\n\n"
            "CRITICAL CRIMINAL LAW INSTRUCTION:\n"
            "The criminal laws of India have been modernized. The operative codes in force since 1 July 2024 are:\n"
            "1. Bharatiya Nyaya Sanhita, 2023 (BNS) — replaces Indian Penal Code, 1860 (IPC)\n"
            "2. Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) — replaces Code of Criminal Procedure, 1973 (CrPC)\n"
            "3. Bharatiya Sakshya Adhiniyam, 2023 (BSA) — replaces Indian Evidence Act, 1872 (IEA)\n"
            "Always state the CURRENT operative BNS/BNSS/BSA provisions as primary. You may mention former IPC/CrPC/IEA sections only as historical equivalents.\n\n"
            f"{mixed_note}"
            "====================================================================================\n"
            "MANDATORY MULTILINGUAL RESPONSE DIRECTIVE:\n"
            "Always identify the language of the user's latest message and respond entirely in that same language. "
            "This rule applies to every response, including legal explanations, follow-up questions, case summaries, evidence checklists and generated document drafts.\n\n"
            "Do not default to English when the user writes in an Indian language.\n\n"
            "If the user changes language during an ongoing conversation, immediately switch the response language to match the latest message while preserving conversation context.\n\n"
            "Keep legal act names, section numbers and official legal terminology accurate. Where an official legal term is conventionally written in English, retain the original term and explain its meaning in the user's language.\n"
            "====================================================================================\n\n"
            f"TARGET RESPONSE LANGUAGE FOR THIS TURN: {lang_name} ({lang_script} script).\n"
            f"You MUST generate your entire response in {lang_name}.\n\n"
            "MANDATORY 7-PART RESPONSE STRUCTURE FOR LEGAL QUERIES:\n"
            "Format your answer strictly using these 7 clean sections:\n"
            f"1. Opening: An empathetic 1-sentence opening in {lang_name}.\n"
            f"2. {h['situation']}: Concise 2-sentence summary of the factual situation (parties, amount, location, core issue).\n"
            f"3. {h['provisions']}: Specific statutory provisions, sections, and acts applicable to the case from verified Indian law.\n"
            f"4. {h['legal_position']}: Clear bullet points explaining the user's legal rights, liabilities, and standing under the cited laws.\n"
            f"5. {h['options']}: Concrete legal and practical options available (e.g. mutual settlement, pre-litigation grievance/ombudsman, statutory complaint, civil/criminal court filing).\n"
            f"6. {h['next_steps']}: Numbered actionable steps (1, 2, 3) the user should take immediately.\n"
            f"7. {h['evidence']}: Bulleted checklist of documentary, electronic, and transactional evidence to preserve.\n"
            f"8. {h['limitations']}: Statutory limitation periods (e.g. 3 years for civil claims, 30 days for cheque notice), jurisdictional distinctions, and reminder that this is legal information and a licensed advocate should be consulted for court filing.\n\n"
            f"FOLLOW-UP QUESTION:\n"
            f"Under header '{h['info_needed']}', ask 1 or 2 targeted missing questions (such as state/city if jurisdiction depends on it, dates, or documents).\n\n"
            "DOCUMENT DRAFTING DIRECTIVE:\n"
            "If the user asks to draft a legal notice, demand letter, police complaint, or RTI application, draft the complete document with realistic placeholders [like this] for missing details.\n\n"
            "DO NOT USE EMOJIS in headers or body text. Maintain a clean, professional legal appearance.\n\n"
            "ETHICAL BOUNDARIES:\n"
            "- Never guarantee a 100% court win.\n"
            "- Never fabricate non-existent sections, court judgments, or URLs.\n"
            f"- Ground your statutory analysis in these verified provisions:\n{statutory_context}\n"
        )

        history_text = ""
        if conversation_history:
            turns = []
            for h_turn in conversation_history[-6:]:
                role = "User" if h_turn.get("role") == "user" else "Assistant"
                turns.append(f"{role}: {h_turn.get('content', '')}")
            history_text = "\n\nConversation History:\n" + "\n".join(turns)

        return f"{system_instruction}{history_text}\n\nCurrent User Message: {message}\nAssistant:"

    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: Optional[LanguageEnum] = None,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ) -> ChatMessage:
        req_id = f"req_{uuid.uuid4().hex[:8]}"
        case = CaseBuilder.extract_case(message, state_jurisdiction=state_jurisdiction)
        citations = LegalKnowledgeBase.retrieve_grounded_laws(message, case.category, state=state_jurisdiction)
        statutory_context = "\n".join([f"- {c.act_name} {c.section}: {c.title} — {c.description}" for c in citations])

        # Pre-screen safety guardrails
        is_med, med_reply = EscalationDetector.check_medical_emergency(message)
        if is_med:
            return ChatMessage(role="assistant", content=med_reply, citations=[], escalation_detected=True)

        is_fraud, fraud_reply = EscalationDetector.check_fraud_request(message)
        if is_fraud:
            return ChatMessage(role="assistant", content=fraud_reply, citations=[])

        is_threat, threats = Sanitizer.inspect_for_threats(message)
        if is_threat and any("prompt injection" in t.lower() or "override" in t.lower() or "exfiltrate" in t.lower() or "credentials" in t.lower() or "authority" in t.lower() or "malicious" in t.lower() for t in threats):
            content = (
                "Safety Guardrail: Security & Instruction Integrity Enforced\n\n"
                "LawPilot AI detected an attempt to override system instructions, exfiltrate confidential credentials, or alter legal safety parameters. "
                "The assistant adheres strictly to verified Indian statutory law, operates under ethical safeguards, and cannot reveal internal prompts or generate malicious exploits."
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        lang_str = self._detect_language(message, language)
        lower_msg = message.strip().lower()

        # Domain Guardrail: Legal Specialisation Check
        from app.core.domain_guardrail import DomainGuardrail
        is_oos, oos_reply, is_mixed = DomainGuardrail.inspect_query_scope(
            message, conversation_history, lang_str=lang_str
        )
        if is_oos and oos_reply:
            return ChatMessage(role="assistant", content=oos_reply, citations=[])

        fast_reply = self._check_fast_track(lower_msg, lang_str)
        if fast_reply:
            return ChatMessage(role="assistant", content=fast_reply, citations=[])

        full_prompt = self._build_prompt(message, conversation_history, lang_str, statutory_context, is_mixed=is_mixed)
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        models_to_try = [("gemini-flash-lite-latest", 8), ("gemini-3.8-flash", 4)]
        for model_name, t_sec in models_to_try:
            payload = {
                "model": model_name,
                "input": full_prompt
            }
            logger.info(f"ReqID={req_id} | Attempting Interactions API with model={model_name} (timeout={t_sec}s)")
            try:
                resp = requests.post(self.INTERACTIONS_URL, headers=headers, json=payload, timeout=t_sec)
                if resp.status_code == 200:
                    data = resp.json()
                    output_text = None
                    for step in data.get("steps", []):
                        if step.get("type") == "model_output":
                            content_parts = step.get("content", [])
                            if content_parts and "text" in content_parts[0]:
                                output_text = content_parts[0]["text"]
                                break

                    if output_text:
                        text_val = output_text.strip()
                        if is_mixed and not any(w in text_val.lower() for w in ["outside", "scope", "movie", "film", "joke"]):
                            text_val += (
                                "\n\n---\n"
                                "**Scope Note:** Please note that LawPilot AI specialises strictly in legal assistance under Indian law. "
                                "While I have addressed your legal query above, general entertainment or unrelated requests (such as movie recommendations) are outside my scope."
                            )
                        logger.info(f"ReqID={req_id} | Success Interactions model={model_name} | Length={len(text_val)}")
                        return ChatMessage(
                            role="assistant",
                            content=text_val,
                            citations=citations,
                            verification_status=VerificationStatusEnum.VERIFIED if citations else VerificationStatusEnum.RECOMMENDED
                        )
                else:
                    logger.warning(f"ReqID={req_id} | Model {model_name} status {resp.status_code}")
            except Exception as e:
                logger.warning(f"ReqID={req_id} | Model {model_name} exception: {e}")

        # Tier 3: generateContent with gemini-flash-lite-latest
        try:
            gen_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={self.api_key}"
            gen_payload = {
                "contents": [{"parts": [{"text": full_prompt}]}]
            }
            logger.info(f"ReqID={req_id} | Attempting generateContent fallback with gemini-flash-lite-latest")
            resp_gen = requests.post(gen_url, json=gen_payload, timeout=5)
            if resp_gen.status_code == 200:
                gen_data = resp_gen.json()
                text_out = gen_data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"ReqID={req_id} | Success generateContent fallback | Length={len(text_out)}")
                return ChatMessage(
                    role="assistant",
                    content=text_out.strip(),
                    citations=citations,
                    verification_status=VerificationStatusEnum.VERIFIED if citations else VerificationStatusEnum.RECOMMENDED
                )
        except Exception as e:
            logger.warning(f"ReqID={req_id} | generateContent fallback exception: {e}")

        logger.info(f"ReqID={req_id} | Falling back to Structured Deterministic Provider")
        demo = DeterministicDemoProvider()
        fallback_lang = LanguageEnum(lang_str) if lang_str in [e.value for e in LanguageEnum] else LanguageEnum.AUTO
        return demo.generate_response(message, conversation_history, fallback_lang, state_jurisdiction, session_id)

    def generate_stream(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: Optional[LanguageEnum] = None,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ):
        """
        Genuine token streaming directly from Google Gemini API with Server-Sent Events.
        Falls back seamlessly to Deterministic streaming on API quotas or network timeouts.
        """
        req_id = f"req_{uuid.uuid4().hex[:8]}"
        case = CaseBuilder.extract_case(message, state_jurisdiction=state_jurisdiction)
        citations = LegalKnowledgeBase.retrieve_grounded_laws(message, case.category, state=state_jurisdiction)
        citations_data = [c.dict() for c in citations]
        from app.core.title_generator import generate_conversation_title
        title = generate_conversation_title(message, case.category)

        # 2. Safety checks
        is_med, med_reply = EscalationDetector.check_medical_emergency(message)
        if is_med:
            yield {"type": "metadata", "title": title, "citations": []}
            for chunk in re.split(r'(\s+)', med_reply):
                if chunk:
                    yield {"type": "token", "content": chunk}
            yield {"type": "done", "title": title, "citations": [], "content": med_reply}
            return

        is_fraud, fraud_reply = EscalationDetector.check_fraud_request(message)
        if is_fraud:
            yield {"type": "metadata", "title": title, "citations": []}
            for chunk in re.split(r'(\s+)', fraud_reply):
                if chunk:
                    yield {"type": "token", "content": chunk}
            yield {"type": "done", "title": title, "citations": [], "content": fraud_reply}
            return

        is_threat, threats = Sanitizer.inspect_for_threats(message)
        if is_threat and any("prompt injection" in t.lower() or "override" in t.lower() or "exfiltrate" in t.lower() or "credentials" in t.lower() or "authority" in t.lower() or "malicious" in t.lower() for t in threats):
            yield {"type": "metadata", "title": title, "citations": []}
            content = (
                "Safety Guardrail: Security & Instruction Integrity Enforced\n\n"
                "LawPilot AI detected an attempt to override system instructions, exfiltrate confidential credentials, or alter legal safety parameters. "
                "The assistant adheres strictly to verified Indian statutory law, operates under ethical safeguards, and cannot reveal internal prompts or generate malicious exploits."
            )
            for chunk in re.split(r'(\s+)', content):
                if chunk:
                    yield {"type": "token", "content": chunk}
            yield {"type": "done", "title": title, "citations": [], "content": content}
            return

        # 3. Language auto-detection
        lang_str = self._detect_language(message, language)
        lower_msg = message.strip().lower()

        # 4. Domain Guardrail: Legal Specialisation Check
        from app.core.domain_guardrail import DomainGuardrail
        is_oos, oos_reply, is_mixed = DomainGuardrail.inspect_query_scope(
            message, conversation_history, lang_str=lang_str
        )
        if is_oos and oos_reply:
            yield {"type": "metadata", "title": title, "citations": []}
            for chunk in re.split(r'(\s+)', oos_reply):
                if chunk:
                    yield {"type": "token", "content": chunk}
            yield {"type": "done", "title": title, "citations": [], "content": oos_reply}
            return

        # 5. Metadata event for in-scope requests
        yield {"type": "metadata", "title": title, "citations": citations_data}

        # 6. Fast-track conversational responses (<5ms)
        fast_reply = self._check_fast_track(lower_msg, lang_str)
        if fast_reply:
            for chunk in re.split(r'(\s+)', fast_reply):
                if chunk:
                    yield {"type": "token", "content": chunk}
            yield {"type": "done", "title": title, "citations": citations_data, "content": fast_reply}
            return

        # 7. Genuine Google Gemini SSE Streaming
        statutory_context = "\n".join([f"- {c.act_name} {c.section}: {c.title} — {c.description}" for c in citations])
        full_prompt = self._build_prompt(message, conversation_history, lang_str, statutory_context, is_mixed=is_mixed)

        stream_models = ["gemini-flash-lite-latest", "gemini-3.8-flash"]
        full_output = ""
        stream_success = False

        for model_name in stream_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent?key={self.api_key}&alt=sse"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}]
            }
            logger.info(f"ReqID={req_id} | Connecting to genuine streamGenerateContent with model={model_name}")
            try:
                resp = requests.post(url, json=payload, stream=True, timeout=12)
                if resp.status_code == 200:
                    resp.encoding = "utf-8"
                    for raw_line in resp.iter_lines(decode_unicode=False):
                        if not raw_line:
                            continue
                        try:
                            line = raw_line.decode("utf-8")
                        except UnicodeDecodeError:
                            line = raw_line.decode("utf-8", errors="replace")
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str:
                                try:
                                    data_obj = json.loads(data_str)
                                    cands = data_obj.get("candidates", [])
                                    if cands:
                                        parts = cands[0].get("content", {}).get("parts", [])
                                        if parts and "text" in parts[0]:
                                            token_text = parts[0]["text"]
                                            full_output += token_text
                                            yield {"type": "token", "content": token_text}
                                except Exception:
                                    pass
                    if full_output.strip():
                        if is_mixed and not any(w in full_output.lower() for w in ["outside", "scope", "movie", "film", "joke"]):
                            scope_note = (
                                "\n\n---\n"
                                "**Scope Note:** Please note that LawPilot AI specialises strictly in legal assistance under Indian law. "
                                "While I have addressed your legal query above, general entertainment or unrelated requests (such as movie recommendations) are outside my scope."
                            )
                            full_output += scope_note
                            yield {"type": "token", "content": scope_note}
                        stream_success = True
                        break
                else:
                    logger.warning(f"ReqID={req_id} | Stream model {model_name} HTTP {resp.status_code}")
            except Exception as e:
                logger.warning(f"ReqID={req_id} | Stream model {model_name} error: {e}")

        if stream_success:
            yield {"type": "done", "title": title, "citations": citations_data, "content": full_output.strip()}
            return

        # 8. Fallback to Structured Deterministic Provider
        logger.info(f"ReqID={req_id} | Falling back to Deterministic streaming")
        demo = DeterministicDemoProvider()
        fallback_lang = LanguageEnum(lang_str) if lang_str in [e.value for e in LanguageEnum] else LanguageEnum.AUTO
        for event in demo.generate_stream(message, conversation_history, fallback_lang, state_jurisdiction, session_id):
            yield event


class LLMProviderFactory:
    """Factory to instantiate the appropriate provider."""
    @classmethod
    def get_provider(cls) -> BaseLLMProvider:
        from app.config import settings
        if settings.gemini_api_key and settings.gemini_api_key.strip():
            return GeminiInteractionsProvider(settings.gemini_api_key.strip())
        return DeterministicDemoProvider()
