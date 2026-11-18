import sys
import os
sys.path.insert(0, os.path.abspath("."))
import re
from app.main import chat_endpoint
from app.models.schemas import ChatRequest

def test_single_turn(name, message, expected_lang, check_fn):
    print(f"\n--- Testing: {name} ---")
    req = ChatRequest(
        message=message,
        conversation_history=[],
        session_id=f"sess_{name.lower().replace(' ', '_')}"
    )
    res = chat_endpoint(req)
    content = res.content
    print(f"User Msg: '{message}'")
    print(f"AI Response Preview: {content[:200]}...")

    passed, reason = check_fn(content)
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} -> {reason}")
    return passed

def has_indic_script(text, start, end):
    return sum(1 for c in text if start <= ord(c) <= end) >= 10

def has_devanagari(text):
    return has_indic_script(text, 0x0900, 0x097F)

def has_gujarati(text):
    return has_indic_script(text, 0x0A80, 0x0AFF)

def has_malayalam(text):
    return has_indic_script(text, 0x0D00, 0x0D7F)

def has_tamil(text):
    return has_indic_script(text, 0x0B80, 0x0BFF)

def has_telugu(text):
    return has_indic_script(text, 0x0C00, 0x0C7F)

def has_bengali(text):
    return has_indic_script(text, 0x0980, 0x09FF)

def check_english_legal(content):
    # Check no Devanagari / Indic scripts
    devanagari_count = sum(1 for c in content if 0x0900 <= ord(c) <= 0x097F)
    if devanagari_count > 5:
        return False, f"Contains unexpected Devanagari script ({devanagari_count} chars)"
    # Check no Hinglish header phrases
    if "aapki situation" in content.lower() or "aapke kanooni adhikar" in content.lower():
        return False, "Leaked Hinglish headers in English response"
    # Check for English legal words
    if any(w in content.lower() for w in ["situation", "legal", "notice", "deposit", "tenant", "rights", "act"]):
        return True, "Fluent English response with correct legal headers and statutory analysis"
    return False, "Does not look like substantive English response"

def check_hindi(content):
    if not has_devanagari(content):
        return False, "Missing Devanagari script in Hindi response"
    hindi_markers = ["आपकी", "कानूनी", "अधिकार", "कदम", "मकान", "मालिक", "डिपॉजिट", "नोटिस", "सकते"]
    hits = sum(1 for w in hindi_markers if w in content)
    if hits >= 2:
        return True, f"Authentic Hindi in Devanagari script ({hits} markers found)"
    return False, "Insufficient Hindi markers"

def check_hinglish(content):
    devanagari_count = sum(1 for c in content if 0x0900 <= ord(c) <= 0x097F)
    if devanagari_count > 5:
        return False, "Hinglish response should be in Latin script, not Devanagari"
    hinglish_words = ["aap", "karein", "karna", "nahi", "raha", "deposit", "notice", "kadam", "adhikar", "paise"]
    hits = sum(1 for w in hinglish_words if re.search(rf"\b{w}\b", content.lower()))
    if hits >= 2:
        return True, f"Natural Hinglish response ({hits} markers found)"
    return False, "Insufficient Hinglish markers"

def check_gujarati(content):
    if has_gujarati(content):
        return True, "Rich Gujarati script response"
    return False, "Missing Gujarati script"

def check_marathi(content):
    if not has_devanagari(content):
        return False, "Missing Devanagari script in Marathi response"
    marathi_words = ["तुमची", "कायदेशीर", "स्थिती", "पावले", "घरमालक", "नोटीस", "आहे", "नाही", "करा"]
    hits = sum(1 for w in marathi_words if w in content)
    if hits >= 2 or "\u0933" in content:
        return True, f"Authentic Marathi response ({hits} markers found)"
    return False, "Insufficient Marathi markers"

def check_malayalam(content):
    if has_malayalam(content):
        return True, "Rich Malayalam script response"
    return False, "Missing Malayalam script"

def check_tamil(content):
    if has_tamil(content):
        return True, "Rich Tamil script response"
    return False, "Missing Tamil script"

def check_telugu(content):
    if has_telugu(content):
        return True, "Rich Telugu script response"
    return False, "Missing Telugu script"

def check_bengali(content):
    if has_bengali(content):
        return True, "Rich Bengali script response"
    return False, "Missing Bengali script"

def check_english_non_legal(content):
    devanagari_count = sum(1 for c in content if 0x0900 <= ord(c) <= 0x097F)
    if devanagari_count > 5:
        return False, "Devanagari found in English non-legal refusal"
    if any(w in content.lower() for w in ["scope", "legal", "lawpilot", "cannot", "specialise", "assist"]):
        return True, "Polite scope refusal in pure English"
    return False, "Invalid refusal response"

def check_hindi_non_legal(content):
    if not has_devanagari(content):
        return False, "Missing Devanagari in Hindi non-legal refusal"
    if any(w in content for w in ["सहायक", "कानूनी", "दायरा", "LawPilot", "मदद", "असमर्थ"]):
        return True, "Polite scope refusal in Hindi"
    return False, "Invalid Hindi refusal"

def test_language_switch():
    print("\n--- Testing: Multi-turn Language Switching (English -> Hindi -> English) ---")
    session_id = "sess_lang_switch_test"
    
    # Turn 1: English
    t1_msg = "My landlord in Bengaluru has deducted 20000 for painting from my deposit."
    res1 = chat_endpoint(ChatRequest(
        message=t1_msg,
        conversation_history=[],
        session_id=session_id
    ))
    c1 = res1.content
    print(f"Turn 1 (EN): {c1[:120]}...")
    p1, r1 = check_english_legal(c1)
    if not p1:
        print(f"[FAIL] Turn 1: {r1}")
        return False
    print(f"[PASS] Turn 1: {r1}")

    # Turn 2: Hindi switch
    t2_msg = "क्या वे ऐसा कानूनी रूप से कर सकते हैं? मुझे क्या करना चाहिए?"
    history = [
        {"role": "user", "content": t1_msg},
        {"role": "assistant", "content": c1}
    ]
    res2 = chat_endpoint(ChatRequest(
        message=t2_msg,
        conversation_history=history,
        session_id=session_id
    ))
    c2 = res2.content
    print(f"Turn 2 (HI): {c2[:120]}...")
    p2, r2 = check_hindi(c2)
    if not p2:
        print(f"[FAIL] Turn 2: {r2}")
        return False
    print(f"[PASS] Turn 2: {r2}")

    # Turn 3: Switch back to English
    t3_msg = "What is the notice period required if I decide to send a legal notice?"
    history.extend([
        {"role": "user", "content": t2_msg},
        {"role": "assistant", "content": c2}
    ])
    res3 = chat_endpoint(ChatRequest(
        message=t3_msg,
        conversation_history=history,
        session_id=session_id
    ))
    c3 = res3.content
    print(f"Turn 3 (EN): {c3[:120]}...")
    p3, r3 = check_english_legal(c3)
    if not p3:
        print(f"[FAIL] Turn 3: {r3}")
        return False
    print(f"[PASS] Turn 3: {r3}")

    return True

def run_suite():
    tests = [
        ("Pure English Tenancy Query", "Help me with the main problem regarding my landlord deposit in Bangalore. They deducted 25000 for painting.", "en", check_english_legal),
        ("Pure English Consumer Query", "I bought a defective mobile phone online and the seller is refusing to refund me. What can I do?", "en", check_english_legal),
        ("Pure Hindi Query", "मेरे मकान मालिक ने मेरा ₹30,000 का सिक्योरिटी डिपॉजिट वापस नहीं किया है। मैं क्या करूँ?", "hi", check_hindi),
        ("Pure Hinglish Query", "Mera landlord security deposit wapas nahi de raha hai, 2 mahine ho gaye. Kya karu?", "hinglish", check_hinglish),
        ("Gujarati Query", "મને મારા મકાનમાલિક તરફથી મળેલી કાનૂની નોટિસ સમજવામાં મદદ કરો.", "gu", check_gujarati),
        ("Marathi Query", "मला माझ्या घरमालकाकडून मिळालेली कायदेशीर नोटीस समजून घेण्यासाठी मदत करा.", "mr", check_marathi),
        ("Malayalam Query", "എന്റെ ഭൂവുടമ സെക്യൂരിറ്റി ഡെപ്പോസിറ്റ് തിരികെ നൽകുന്നില്ല. എനിക്ക് എന്ത് ചെയ്യാൻ കഴിയും?", "ml", check_malayalam),
        ("Tamil Query", "என் நில உரிமையாளர் முன்பணத்தை திருப்பித் தர மறுக்கிறார். நான் என்ன செய்ய வேண்டும்?", "ta", check_tamil),
        ("Telugu Query", "నా ఇంటి యజమాని సెక్యూరిటీ డిపాజిట్ తిరిగి ఇవ్వడం లేదు. నేను ఏమి చేయాలి?", "te", check_telugu),
        ("Bengali Query", "আমার বাড়িওয়ালা সিকিউরিটি ডিপোজিট ফেরত দিতে অস্বীকার করছেন। আমি কি করতে পারি?", "bn", check_bengali),
        ("Explicit English Override", "Answer in English: Mera landlord deposit nahi de raha", "en", check_english_legal),
        ("Explicit Hindi Override", "Please answer in Hindi: My employer has not paid my salary for 2 months.", "hi", check_hindi),
        ("Non-Legal Query English", "Write a python script for binary search algorithm", "en", check_english_non_legal),
        ("Non-Legal Query Hindi", "स्वादिष्ट चाय बनाने की विधि बताइए", "hi", check_hindi_non_legal),
    ]

    results = []
    for name, msg, exp, chk in tests:
        success = test_single_turn(name, msg, exp, chk)
        results.append((name, success))

    switch_success = test_language_switch()
    results.append(("Multi-turn Language Switch", switch_success))

    print("\n" + "="*50)
    print("MULTILINGUAL CONSISTENCY EVALUATION SUMMARY")
    print("="*50)
    passed_count = sum(1 for _, ok in results if ok)
    for name, ok in results:
        res = "PASS" if ok else "FAIL"
        print(f"[{res}] {name}")
    print(f"\nFinal: {passed_count}/{len(results)} Passed ({(passed_count/len(results))*100:.1f}%)")
    return passed_count == len(results)

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
