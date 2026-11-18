import re
from typing import Optional, Any

UNAMBIGUOUS_HINGLISH_WORDS = {
    # Pronouns / Demonstratives
    "mera", "meri", "mere", "mujhe", "mujhko", "apna", "apni", "apne",
    "aapka", "aapki", "aapke", "tumhara", "tumhari", "tumhare",
    "unka", "unki", "unke", "inka", "inki", "inke", "unhone", "inhone",
    "kisi", "kisko", "jisko",
    # Question words
    "kya", "kyun", "kyu", "kaise", "kahan", "kitna", "kitni", "kitne", "kab",
    # Verbs & Auxiliaries
    "nahi", "nahin", "nhi", "mat",
    "chahiye", "chahta", "chahti", "chahte",
    "karein", "karna", "karta", "karti", "karte", "karo", "karu", "karoon", "kiya", "kiye",
    "hoga", "hogi", "hoge", "hote", "hoti", "hota", "hona",
    "raha", "rahi", "rahe", "hoon", "gaya", "gayi", "gaye",
    "sakta", "sakti", "sakte", "sakenge",
    "batao", "batayein", "bataiye", "samjhao", "samjhaiye",
    "bheja", "bheji", "bheje", "bhejna", "bhejein",
    "dunga", "dungi", "denge", "dena", "diya", "dega", "degi",
    "liya", "liye", "lena", "lega", "legi",
    "rok", "rakha", "rakhi", "rakhe", "chhod",
    # Domain nouns & legal Hinglish terms
    "paisa", "paise", "rupaye", "kiraya", "kirayedaar", "makan", "makanmalik", "ghar",
    "naukri", "vetan", "shikayat", "faisla", "dhokha", "madad", "bhai",
    # Conjunctions / Adverbs
    "lekin", "magar", "kyunki", "isliye", "warna", "sirf", "zaroor", "kripya"
}

HINGLISH_PHRASES = [
    "kya karu", "kya karna", "kya karein", "kya hoga", "nahi diya", "nahi de raha",
    "nahi de rahe", "nahi mila", "paise wapas", "paisa wapas", "deposit wapas", "salary nahi",
    "makan malik", "notice bhejna", "madad chahiye", "madad karein", "batao kya",
    "batayein kya", "kuch nahi", "ab kya", "kaise karein", "kaise karu", "case karna",
    "complaint karna", "fir darj", "police thana", "vakil karna", "court jana"
]

ENGLISH_WORDS = {
    "the", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "a", "an", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "can", "will", "just", "don", "should", "now", "i", "my",
    "me", "we", "our", "you", "your", "he", "him", "his", "she", "her", "they", "them",
    "their", "what", "which", "who", "whom", "this", "that", "these", "those", "am",
    "would", "could", "please", "help", "problem", "issue", "dispute", "court",
    "landlord", "tenant", "deposit", "rent", "agreement", "police", "notice", "salary",
    "refund", "money", "product", "defective", "company", "employer", "rights", "legal"
}

MARATHI_DISTINCTIVE_WORDS = {
    "आहे", "आहेत", "नाही", "नाहीत", "काय", "मला", "माझे", "माझी", "माझ्या", "माझं",
    "आता", "करू", "शकतो", "शकते", "केला", "केली", "केले", "केलेली", "केलेले", "दिले",
    "दिली", "होते", "होती", "झाले", "झाला", "झाली", "सांगा", "मिळाले", "मिळाली",
    "घरमालक", "घरमालकाने", "घरमालकाकडून", "भाडेकरू", "दोषपूर्ण", "विक्रेता", "पैसे",
    "परत", "देत", "नोटीस", "समजून", "समजण्यासाठी", "मदत", "पगार", "करणे", "तुम्ही",
    "द्या", "करा", "करावे", "पाहिजे", "घेऊन", "जास्त", "फार", "फारच", "खरेदी", "मोबाईल"
}

HINDI_DISTINCTIVE_WORDS = {
    "है", "हैं", "था", "थी", "थे", "नहीं", "क्या", "मुझे", "मेरा", "मेरी", "मेरे",
    "किया", "दिए", "दिया", "दी", "रहा", "रही", "रहे", "सकता", "सकती", "सकते",
    "चाहिए", "बताएं", "बताओ", "करूँ", "करूं", "हुई", "हुआ", "हुए", "मकान",
    "मालिक", "किराया", "वेतन", "पैसे", "वापस", "मदद", "खरीदा", "दुकानदार"
}

def detect_message_language(message: str, explicit_lang: Optional[Any] = None) -> str:
    if not message or not message.strip():
        return "en"

    lower_msg = message.strip().lower()

    # Priority 1: Explicit user instruction for response language
    explicit_requests = [
        # English
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+english\b|english\s+me\b|english\s+mein\b|अंग्रेजी\s+में\b|અંગ્રેજીમાં\b|इंग्रजीत\b", "en"),
        # Hinglish
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+hinglish\b|hinglish\s+me\b|hinglish\s+mein\b", "hinglish"),
        # Hindi
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+hindi\b|hindi\s+me\b|hindi\s+mein\b|हिंदी\s*में\b|हिन्दी\s*में\b", "hi"),
        # Gujarati
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+(?:gujarati|gujrati)\b|gujarati\s+ma\b|ગુજરાતીમાં\b", "gu"),
        # Marathi
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+marathi\b|मराठीत\b|मराठी\s*मध्ये\b|marathi\s+madhye\b", "mr"),
        # Malayalam
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+malayalam\b|മലയാളത്തിൽ\b", "ml"),
        # Tamil
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+tamil\b|தமிழில்\b", "ta"),
        # Telugu
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+telugu\b|తెలుగులో\b", "te"),
        # Bengali
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+(?:bengali|bangla)\b|বাংলায়\b|bangla\s+te\b", "bn"),
        # Kannada
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+kannada\b|ಕನ್ನಡದಲ್ಲಿ\b", "kn"),
        # Punjabi
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+punjabi\b|ਪੰਜਾਬੀ\s*ਵਿੱਚ\b", "pa"),
        # Odia
        (r"\b(?:in|reply\s+in|answer\s+in|respond\s+in|speak\s+in|explain\s+in|write\s+in)\s+odia\b|ଓଡ଼ିଆରେ\b", "or"),
    ]
    for pattern, lang_code in explicit_requests:
        if re.search(pattern, lower_msg, re.IGNORECASE):
            return lang_code

    # Priority 2: Unicode Indic script frequency analysis
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
            # Disambiguate Devanagari: Marathi vs Hindi
            has_marathi_la = "\u0933" in message
            devanagari_tokens = set(re.split(r'[\s,।?.!:\-\"\'()]+', message))
            marathi_hits = sum(1 for w in devanagari_tokens if w in MARATHI_DISTINCTIVE_WORDS)
            hindi_hits = sum(1 for w in devanagari_tokens if w in HINDI_DISTINCTIVE_WORDS)

            if has_marathi_la or marathi_hits > hindi_hits:
                return "mr"
            return "hi"
        return dominant_script

    # Priority 3: Latin script analysis: Hinglish vs English
    tokens = re.findall(r'\b[a-zA-Z]+\b', lower_msg)
    if not tokens:
        return "en"

    h_hits = sum(1 for w in tokens if w in UNAMBIGUOUS_HINGLISH_WORDS)
    e_hits = sum(1 for w in tokens if w in ENGLISH_WORDS)
    has_h_phrase = any(phrase in lower_msg for phrase in HINGLISH_PHRASES)

    if has_h_phrase:
        if e_hits >= h_hits * 3 and h_hits <= 1:
            return "en"
        return "hinglish"

    if h_hits >= 2:
        if e_hits >= h_hits * 2:
            return "en"
        if (h_hits / max(len(tokens), 1)) >= 0.15 or h_hits >= 3:
            return "hinglish"

    # Priority 4: Fallback to explicit_lang if valid
    if explicit_lang:
        val = explicit_lang.value if hasattr(explicit_lang, "value") else str(explicit_lang).lower()
        if val not in ["en", "auto", "none", "", "null"]:
            return val

    return "en"


# Test cases
test_cases = [
    ("Help me with the main problem regarding my landlord deposit in Bangalore", "en"),
    ("I purchased a defective mobile phone online and the seller is refusing to refund me. What can I do now?", "en"),
    ("My landlord deducted money for painting. The main agreement said normal wear and tear is de-facto allowed.", "en"),
    ("Can you please tell me what are my rights under Indian law?", "en"),
    ("Hello, what services do you provide?", "en"),
    ("Mera landlord security deposit wapas nahi de raha hai, 2 mahine ho gaye. Kya karu?", "hinglish"),
    ("Maine ek phone liya tha online lekin defective nikla aur seller refund nahi de raha. Kya karu?", "hinglish"),
    ("Mujhe notice mila hai landlord se, kya karu ab?", "hinglish"),
    ("Salary nahi di company ne 3 months se, kya case kar sakta hoon?", "hinglish"),
    ("Answer in English: Mera landlord deposit nahi de raha", "en"),
    ("Explain in English: what should I do?", "en"),
    ("Please answer in Hindi: I want to know my rights.", "hi"),
    ("Now answer in Gujarati: my landlord took deposit", "gu"),
    ("મને મારા મકાનમાલિક તરફથી મળેલી કાનૂની નોટિસ સમજવામાં મદદ કરો.", "gu"),
    ("मला माझ्या घरमालकाकडून मिळालेली कायदेशीर नोटीस समजून घेण्यासाठी मदत करा.", "mr"),
    ("मी ऑनलाइन एक दोषपूर्ण मोबाईल फोन खरेदी केला आहे आणि विक्रेता मला पैसे परत करण्यास नकार देत आहे. आता मी काय करू शकतो?", "mr"),
    ("मेरे मकान मालिक ने मेरा ₹30,000 का सिक्योरिटी डिपॉजिट वापस नहीं किया है। मैं क्या करूँ?", "hi"),
    ("एम्पलॉयर ने पिछले तीन महीने का वेतन नहीं दिया है। मुझे क्या कानूनी कदम उठाने चाहिए?", "hi"),
    ("എന്റെ ഭൂവുടമ സെക്യൂരിറ്റി ഡെപ്പോസിറ്റ് തിരികെ നൽകുന്നില്ല.", "ml"),
    ("என் நில உரிமையாளர் முன்பணத்தை திருப்பித் தர மறுக்கிறார்.", "ta"),
    ("నా ఇంటి యజమాని సెక్యూరిటీ డిపాజిట్ తిరిగి ఇవ్వడం లేదు.", "te"),
    ("আমার বাড়িওয়ালা সিকিউরিটি ডিপোজিট ফেরত দিতে অস্বীকার করছেন।", "bn"),
]

passed = 0
for text, expected in test_cases:
    detected = detect_message_language(text)
    status = "PASS" if detected == expected else "FAIL"
    if status == "PASS":
        passed += 1
    print(f"[{status}] Expected={expected:8s} | Detected={detected:8s} | Text='{text[:55]}...'")

print(f"\nTotal: {len(test_cases)}, Passed: {passed}, Failed: {len(test_cases) - passed}")
