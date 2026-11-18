"""
LawPilot AI — Legal Domain Specialisation & Scope Guardrail
Enforces comprehensive Indian legal scope covering all substantive and procedural
areas of Indian law (Constitutional, Criminal, Civil, Family, Property, Consumer,
Employment, Cyber, Banking, Tax, IPR, Motor Accident, Insurance, Environment, RTI, Immigration, ADR).
Politely redirects purely general-purpose non-legal inquiries (trivia, math, coding, jokes, sports)
while intelligently supporting greetings, ambiguous distress, follow-ups, and mixed queries.
"""

import re
from typing import Tuple, Optional, List, Dict

OUT_OF_SCOPE_RESPONSES = {
    "en": (
        "I am LawPilot AI, a comprehensive legal assistant specialising in Indian law across constitutional, "
        "criminal, civil, family, property, consumer, employment, cyber, banking, taxation, and administrative matters. "
        "I can help you understand your legal rights, assess statutory provisions, explore procedural options, and draft legal documents. "
        "I cannot assist with general topics outside Indian legal matters (such as general trivia, coding, or entertainment). "
        "Is there an Indian legal issue or question I can help you with?"
    ),
    "hi": (
        "मैं LawPilot AI हूँ, जो भारतीय कानून के सभी प्रमुख क्षेत्रों (संवैधानिक, आपराधिक, दीवानी, पारिवारिक, संपत्ति, उपभोक्ता, रोजगार, साइबर, बैंकिंग, कराधान आदि) में सहायता प्रदान करने वाला एक व्यापक कानूनी सहायक है। "
        "मैं आपके कानूनी अधिकारों को समझने, प्रासंगिक कानूनी धाराओं का विश्लेषण करने और कानूनी दस्तावेज तैयार करने में मदद कर सकता हूँ। "
        "मैं भारतीय कानून के दायरे से बाहर के सामान्य विषयों (जैसे कोडिंग, सामान्य ज्ञान या मनोरंजन) में सहायता नहीं कर सकता। क्या कोई कानूनी समस्या है जिसमें मैं आपकी मदद कर सकता हूँ?"
    ),
    "gu": (
        "હું LawPilot AI છું, ભારતીય કાયદાના તમામ મુખ્ય ક્ષેત્રો (બંધારણીય, ફોજદારી, દીવાની, કૌટુંબિક, મિલકત, ગ્રાહક સુરક્ષા, રોજગાર, સાયબર, બેંકિંગ, કરવેરા વગેરે) માટેનો એક વ્યાપક કાનૂની સહાયક. "
        "હું તમને તમારા કાનૂની અધિકારો સમજવામાં, કાનૂની જોગવાઈઓની ચકાસણી કરવામાં અને કાનૂની દસ્તાવેજો તૈયાર કરવામાં મદદ કરી શકું છું. "
        "હું ભારતીય કાનૂની ક્ષેત્ર બહારના સામાન્ય વિષયોમાં સહાય કરી શકતો નથી. શું કોઈ કાનૂની બાબત છે જેમાં હું તમને મદદ કરી શકું?"
    ),
    "mr": (
        "मी LawPilot AI आहे, भारतीय कायद्याच्या सर्व प्रमुख क्षेत्रांमध्ये (घटनात्मक, फौजदारी, दिवाणी, कौटुंबिक, मालमत्ता, ग्राहक संरक्षण, रोजगार, सायबर, बँकिंग, कर इत्यादी) सहाय्य करणारा एक व्यापक कायदेशीर सहाय्यक. "
        "मी तुमचे कायदेशीर हक्क समजून घेण्यास, वैधानिक तरतुदींचे विश्लेषण करण्यास आणि कायदेशीर कागदपत्रे तयार करण्यास मदत करू शकतो. "
        "मी भारतीय कायद्याच्या बाहेरील सामान्य विषयांमध्ये मदत करू शकत नाही. मी तुम्हाला मदत करू शकेन असा कोणताही कायदेशीर प्रश्न आहे का?"
    ),
    "ml": (
        "ഞാൻ LawPilot AI ആണ്, ഭരണഘടനാപരമായ, ക്രിമിനൽ, സിവിൽ, കുടുംബം, വസ്തുവകകൾ, ഉപഭോക്തൃ സംരക്ഷണം, തൊഴിൽ, സൈബർ, ബാങ്കിംഗ് തുടങ്ങി ഇന്ത്യൻ നിയമത്തിന്റെ എല്ലാ പ്രധാന മേഖലകളിലും സഹായിക്കുന്ന സമഗ്ര നിയമ സഹായി. "
        "നിയമപരമായ വിഷയങ്ങളല്ലാത്ത പൊതുവായ കാര്യങ്ങളിൽ എനിക്ക് സഹായിക്കാനാകില്ല. ഞാൻ സഹായിക്കേണ്ട എന്തെങ്കിലും നിയമപരമായ പ്രശ്നമുണ്ടോ?"
    ),
    "ta": (
        "நான் LawPilot AI, அரசியலமைப்பு, குற்றவியல், சிவில், குடும்பம், சொத்து, நுகர்வோர் பாதுகாப்பு, வேலைவாய்ப்பு, சைபர், வங்கி மற்றும் வரி உள்ளிட்ட அனைத்து இந்திய சட்டப் பிரிவுகளிலும் உதவும் ஒரு விரிவான சட்ட உதவியாளர். "
        "இந்திய சட்டம் சாராத பொதுவான தலைப்புகளில் என்னால் உதவ முடியாது. நான் உதவக்கூடிய ஏதேனும் சட்டப் பிரச்சனை உள்ளதா?"
    ),
    "te": (
        "నేను LawPilot AI, రాజ్యాంగ, క్రిమినల్, సివిల్, కుటుంబ, ఆస్తి, వినియోగదారుల రక్షణ, ఉపాధి, సైబర్, బ్యాంకింగ్ మరియు పన్ను వంటి భారతీయ చట్టాల అన్ని విభాగాలలో సహాయపడే సమగ్ర చట్టపరమైన సహాయకుడిని. "
        "చట్టపరమైన పరిధికి వెలుపల ఉన్న సాధారణ అంశాలలో నేను సహాయం చేయలేను. నేను మీకు సహాయం చేయగల చట్టపరమైన సమస్య ఏదైనా ఉందా?"
    ),
    "bn": (
        "আমি LawPilot AI, সাংবিধানিক, ফৌজদারি, দেওয়ানি, পারিবারিক, সম্পত্তি, ভোক্তা সুরক্ষা, কর্মসংস্থান, সাইবার, ব্যাংকিং এবং কর সহ ভারতীয় আইনের সমস্ত প্রধান ক্ষেত্রে সহায়তা প্রদানকারী একটি ব্যাপক আইনি সহায়ক। "
        "ভারতীয় আইনের বাইরের সাধারণ বিষয়ে আমি সাহায্য করতে পারি না। এমন কোনো আইনি বিষয় আছে যাতে আমি সাহায্য করতে পারি?"
    ),
    "hinglish": (
        "Main LawPilot AI hoon, Indian law ke sabhi major areas (Constitutional, Criminal, Civil, Family, Property, Consumer, Employment, Cyber, Banking, Tax, RTI) me aapka comprehensive legal assistant. "
        "Main aapke legal rights samjhne, statutory provisions analyze karne aur legal documents draft karne me madad kar sakta hoon. "
        "Main Indian legal scope ke bahar general topics me help nahi kar sakta. Kya koi legal issue hai jisme main aapki madad karu?"
    )
}

class DomainGuardrail:
    """
    Evaluates whether user input falls within LawPilot AI's comprehensive Indian legal assistance scope.
    """

    # Unambiguous out-of-scope triggers (pure trivia, coding, jokes, science, sports, creative)
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

    # Explicit legal indicators spanning all 18 Indian legal domains
    LEGAL_INDICATORS = [
        r"\b(?:deposit|salary|wages|employer|landlord|tenant|evict|eviction|rent|refund|defective|notice|court|lawyer|advocate|police|fir|cheating|agreement|lease|painting|consumer|flat|workplace|commissioner|cheque|cheque\s*bounce|dues|payslip|relieving|bns|bnss|bsa|ipc|crpc|bail|arrest|writ|article\s*(?:14|19|21|32|226)|injunction|order\s*37|order\s*39|stay\s*order|limitation|divorce|maintenance|custody|domestic\s*violence|pwdva|rera|partition|mutation|encroachment|posh|gratuity|cyber\s*crime|1930|phishing|upi\s*scam|bank\s*freeze|rbi\s*ombudsman|tax\s*notice|income\s*tax|gst|trademark|copyright|patent|mact|accident\s*claim|insurance\s*claim|ngt|pollution|rti|pio|passport\s*impounded|arbitration|mediation|lok\s*adalat)\b",
        r"(?:डिपॉज़िट|वेतन|किराया|मकान\s*मालिक|सैलरी|रिफंड|दोषपूर्ण|नोटीस|एफआईआर|जमानत|तलाक|घरेलू\s*हिंसा|रेरा|चेक\s*बाउंस|સિક્યોરિટી|પગાર|ભાડું|મકાનમાલિક|રિફંડ|ખામીયુક્ત|ડિપોઝિટ|પોલીસ|એફઆઈઆર|જામીન|છૂટાછેડા|રેરા|ચેક\s*બાઉન્સ|શમ્બળ|ശമ്പളം|വാടക|തൊഴിലുടമ|റീഫണ്ട്|പോലീസ്|ஜாமீன்|சம்பளம்|வாடகை|நிறுவனம்|ஜீதம்|అద్దె|డిపాజిట్|బెయిల్|বেতন|ভাড়া|রিফান্ড|ঘরমালक|जामीन)"
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

        # In-scope or ambiguous (err on the side of helping the citizen)
        return False, None, False
