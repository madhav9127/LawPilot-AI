"""
LawPilot AI — Legal Domain Specialisation & Scope Guardrail
Enforces specialized Indian legal scope (Tenancy, Consumer, Employment, Legal Docs).
Politely redirects general-purpose inquiries (trivia, math, coding, jokes, sports)
while intelligently supporting greetings, ambiguous distress, follow-ups, and mixed legal queries.
"""

import re
from typing import Tuple, Optional, List, Dict

OUT_OF_SCOPE_RESPONSES = {
    "en": (
        "I am LawPilot AI, an assistant specialising in everyday legal problems in India. "
        "I can help you understand your legal rights, organise your case, identify possible options and prepare legal documents. "
        "I cannot assist with general topics outside my legal-assistance scope. Is there a legal issue I can help you with?"
    ),
    "hi": (
        "मैं LawPilot AI हूँ, जो भारत में रोजमर्रा की कानूनी समस्याओं के लिए एक विशेष कानूनी सहायक है। "
        "मैं आपके कानूनी अधिकारों को समझने, आपके मामले को व्यवस्थित करने और कानूनी दस्तावेज तैयार करने में मदद कर सकता हूँ। "
        "मैं अपने कानूनी दायरे से बाहर के सामान्य विषयों में सहायता नहीं कर सकता। क्या कोई कानूनी समस्या है जिसमें मैं आपकी मदद कर सकता हूँ?"
    ),
    "gu": (
        "હું LawPilot AI છું, ભારતમાં રોજિંદા કાનૂની અધિકારો માટે વિશેષ કાનૂની સહાયક. "
        "હું તમને તમારા કાનૂની અધિકારો સમજવામાં, કેસ ગોઠવવામાં અને કાનૂની દસ્તાવેજો તૈયાર કરવામાં મદદ કરી શકું છું. "
        "હું મારા કાનૂની કાર્યક્ષેત્ર બહારના સામાન્ય વિષયોમાં સહાય કરી શકતો નથી. શું કોઈ કાનૂની બાબત છે જેમાં હું તમને મદદ કરી શકું?"
    ),
    "mr": (
        "मी LawPilot AI आहे, भारतातील दैनंदिन नागरी कायदेशीर समस्यांसाठी एक विशेष कायदेशीर सहाय्यक. "
        "मी तुमचे कायदेशीर हक्क समजून घेण्यास, तुमचा खटला तयार करण्यास आणि कायदेशीर कागदपत्रे तयार करण्यास मदत करू शकतो. "
        "मी माझ्या कायदेशीर कार्यक्षेत्राबाहेरील सामान्य विषयांमध्ये मदत करू शकत नाही. मी तुम्हाला मदत करू शकेन असा कोणताही कायदेशीर प्रश्न आहे का?"
    ),
    "ml": (
        "ഞാൻ LawPilot AI ആണ്, ഇന്ത്യയിലെ ദൈനംദിന നിയമ പ്രശ്നങ്ങളിൽ സഹായിക്കുന്ന ഒരു പ്രത്യേക നിയമ സഹായി. "
        "നിങ്ങളുടെ നിയമപരമായ അവകാശങ്ങൾ മനസിലാക്കാനും രേഖകൾ തയ്യാറാക്കാനും ഞാൻ സഹായിക്കാം. "
        "നിയമ സഹായ പരിധിക്ക് പുറത്തുള്ള പൊതുവായ വിഷയങ്ങളിൽ എനിക്ക് സഹായിക്കാനാകില്ല. ഞാൻ സഹായിക്കേണ്ട എന്തെങ്കിലും നിയമപരമായ പ്രശ്നമുണ്ടോ?"
    ),
    "ta": (
        "நான் LawPilot AI, இந்தியாவில் அன்றாட சட்டப் பிரச்சனைகளுக்கான சிறப்பு சட்ட உதவியாளர். "
        "உங்கள் சட்டப்பூர்வ உரிமைகளைப் புரிந்து கொள்ளவும் சட்ட ஆவணங்களைத் தயாரிக்கவும் நான் உங்களுக்கு உதவ முடியும். "
        "சட்ட எல்லைக்கு அப்பாற்பட்ட பொதுவான தலைப்புகளில் என்னால் உதவ முடியாது. நான் உதவக்கூடிய சட்டப் பிரச்சனை ஏதேனும் உள்ளதா?"
    ),
    "te": (
        "నేను LawPilot AI, భారతదేశంలో రోజువారీ చట్టపరమైన సవాళ్ల కోసం ప్రత్యేక సహాయకుడిని. "
        "మీ చట్టపరమైన హక్కులను అర్థం చేసుకోవడానికి మరియు చట్టపరమైన పత్రాలను సిద్ధం చేయడానికి నేను సహాయపడగలను. "
        "నా చట్టపరమైన పరిధికి వెలుపల ఉన్న సాధారణ అంశాలలో నేను సహాయం చేయలేను. నేను మీకు సహాయం చేయగల చట్టపరమైన సమస్య ఏదైనా ఉందా?"
    ),
    "bn": (
        "আমি LawPilot AI, ভারতে দৈনন্দিন নাগরিক আইনি সমস্যার জন্য একটি বিশেষ আইনি সহায়ক। "
        "আমি আপনাকে আপনার অধিকার বুঝতে এবং আইনি নথি তৈরি করতে সাহায্য করতে পারি। "
        "আমার আইনি সহায়তার পরিধির বাইরের সাধারণ বিষয়ে আমি সাহায্য করতে পারি না। এমন কোনো আইনি সমস্যা আছে যাতে আমি সাহায্য করতে পারি?"
    ),
    "hinglish": (
        "Main LawPilot AI hoon, India me everyday legal problems ke liye aapka specialised legal assistant. "
        "Main aapko legal rights samjhne, case organize karne aur legal documents draft karne me madad kar sakta hoon. "
        "Main legal scope ke bahar general topics me help nahi kar sakta. Kya koi legal issue hai jisme main aapki madad karu?"
    )
}

class DomainGuardrail:
    """
    Evaluates whether user input falls within LawPilot AI's legal assistance scope.
    """

    # Unambiguous out-of-scope triggers (trivia, coding, jokes, science, sports, creative)
    OUT_OF_SCOPE_PATTERNS = [
        # Geography / Trivia
        r"\b(?:capital\s+of\s+[a-zA-Z]+|who\s+is\s+the\s+president\s+of|largest\s+ocean|tallest\s+building|currency\s+of\s+[a-zA-Z]+)\b",
        # Coding / Programming / IT non-legal
        r"\b(?:write\s+a\s+(?:python|c\+\+|java|javascript|php|sql|ruby|go)\s+(?:program|script|code)|python\s+code|how\s+to\s+build\s+a\s+website|sort\s+a\s+(?:list|array)|sort\s+an\s+array|binary\s+search|bubble\s+sort|leetcode)\b",
        # General Science / Physics / Math
        r"\b(?:explain\s+quantum\s+physics|quantum\s+physics|theory\s+of\s+relativity|schrodinger|photosynthesis|solve\s+(?:math|calculus|equation|algebra)|solve\s+a\s+mathematics|what\s+is\s+2\s*\+\s*2|2\s*\+\s*2)\b",
        # Entertainment / Creative writing
        r"\b(?:tell\s+me\s+a\s+(?:funny\s+)?joke|tell\s+me\s+a\s+joke|write\s+a\s+(?:romantic\s+)?poem|sing\s+a\s+song|write\s+a\s+rap|write\s+a\s+story\s+about)\b",
        # Sports / Current events
        r"\b(?:cricket\s+match|who\s+won\s+yesterday|who\s+won\s+the\s+match|cricket|football\s+score|ipl\s+score|fifa\s+world\s+cup|olympics)\b",
        # Lifestyle / Gym / Cooking
        r"\b(?:gym\s+workout\s+plan|workout\s+plan|how\s+to\s+lose\s+weight|recipe\s+for|how\s+to\s+bake)\b",
        # General recommendations
        r"\b(?:suggest\s+a\s+movie|recommend\s+a\s+movie|best\s+movies|recommend\s+a\s+book)\b"
    ]

    # Explicit legal indicators
    LEGAL_INDICATORS = [
        r"\b(?:deposit|salary|wages|employer|landlord|tenant|evict|eviction|rent|refund|defective|notice|court|lawyer|advocate|police|fir|cheating|agreement|lease|painting|consumer|flat|workplace|commissioner|cheque|cheque bounce|dues|payslip|relieving)\b",
        r"(?:डिपॉज़िट|वेतन|किराया|मकान\s*मालिक|सैलरी|रिफंड|दोषपूर्ण|नोटीस|સિક્યોરિટી|પગાર|ભાડું|મકાનમાલિક|રિફંડ|ખામીયુક્ત|ડિપોઝિટ|ശമ്പളം|വാടക|തൊഴിലുടമ|റീഫണ്ട്|சம்பளம்|வாடகை|நிறுவனம்|ஜீతం|అద్దె|డిపాజిట్|বেতন|ভাড়া|রিফান্ড|घरमालक)"
    ]

    # Conversational in-scope messages (greetings, general help, distress)
    CONVERSATIONAL_IN_SCOPE = [
        r"^(?:hi|hello|hey|namaste|pranam|greetings|good\s*(?:morning|afternoon|evening))\b",
        r"^(?:who\s+are\s+you|what\s+is\s+your\s+name|what\s+can\s+you\s+help\s+me\s+with|what\s+do\s+you\s+do|can\s+you\s+help\s+me)\b",
        r"\b(?:i\s+am\s+confused|don't\s+know\s+what\s+to\s+do|i\s+need\s+help|feeling\s+stressed|help\s+me\s+please)\b",
        r"\b(?:thank\s+you|thanks|bye|goodbye|alvida|shukriya|dhanyawad)\b",
        r"\b(?:received\s+a\s+notice|court\s+summons|legal\s+word|what\s+does\s+this\s+mean|draft\s+a\s+letter|prepare\s+for\s+a\s+hearing)\b"
    ]

    @classmethod
    def inspect_query_scope(cls, message: str, conversation_history: Optional[List[Dict[str, str]]] = None, lang_str: str = "en") -> Tuple[bool, Optional[str], bool]:
        """
        Inspects message scope.
        Returns: (is_out_of_scope: bool, redirect_response: Optional[str], is_mixed: bool)
        """
        if not message or not message.strip():
            return False, None, False

        lower = message.strip().lower()

        # Check for conversational in-scope messages first
        for pat in cls.CONVERSATIONAL_IN_SCOPE:
            if re.search(pat, lower):
                return False, None, False

        has_legal = any(re.search(pat, lower) for pat in cls.LEGAL_INDICATORS)
        is_unrelated = any(re.search(pat, lower) for pat in cls.OUT_OF_SCOPE_PATTERNS)

        # Contextual exception: if ongoing conversation already has active legal context
        has_history_context = False
        if conversation_history:
            for turn in conversation_history[-4:]:
                txt = turn.get("content", "").lower()
                if any(re.search(pat, txt) for pat in cls.LEGAL_INDICATORS):
                    has_history_context = True
                    break

        # Mixed query: has legal content AND unrelated content
        if has_legal and is_unrelated:
            return False, None, True

        # Purely unrelated query without legal content or prior legal history
        if is_unrelated and not has_legal and not has_history_context:
            resp_text = OUT_OF_SCOPE_RESPONSES.get(lang_str, OUT_OF_SCOPE_RESPONSES["en"])
            return True, resp_text, False

        # In-scope or ambiguous (err on the side of helping the user)
        return False, None, False
