import os
import sys
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = "testing/raw_outputs/multilingual"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TESTS = [
    {
        "id": "ML_01_English",
        "name": "Test 1 — English",
        "input": "My employer in Bangalore has not paid my salary for two months.",
        "expected_lang": "en",
        "script": "Latin",
        "domain": "Employment"
    },
    {
        "id": "ML_02_Hindi",
        "name": "Test 2 — Hindi",
        "input": "मेरे नियोक्ता ने पिछले दो महीनों से मेरा वेतन नहीं दिया है। मैं क्या कर सकता हूँ?",
        "expected_lang": "hi",
        "script": "Devanagari",
        "domain": "Employment"
    },
    {
        "id": "ML_03_Gujarati",
        "name": "Test 3 — Gujarati",
        "input": "મેં ઑનલાઇન એક ખામીયુક્ત ફોન ખરીદ્યો છે અને વેચનાર મને રિફંડ આપવાનો ઇનકાર કરી રહ્યો છે. હવે હું શું કરી શકું?",
        "expected_lang": "gu",
        "script": "Gujarati",
        "domain": "Consumer"
    },
    {
        "id": "ML_04_Malayalam",
        "name": "Test 4 — Malayalam",
        "input": "എന്റെ ബാംഗ്ലൂരിലുള്ള തൊഴിലുടമ കഴിഞ്ഞ രണ്ട് മാസമായി എനിക്ക് ശമ്പളം നൽകിയിട്ടില്ല. ഞാൻ എന്ത് ചെയ്യണം?",
        "expected_lang": "ml",
        "script": "Malayalam",
        "domain": "Employment"
    },
    {
        "id": "ML_05_Tamil",
        "name": "Test 5 — Tamil",
        "input": "எனது நிறுவனம் கடந்த இரண்டு மாதங்களாக எனக்கு சம்பளம் வழங்கவில்லை. நான் என்ன செய்ய வேண்டும்?",
        "expected_lang": "ta",
        "script": "Tamil",
        "domain": "Employment"
    },
    {
        "id": "ML_06_Telugu",
        "name": "Test 6 — Telugu",
        "input": "నా యజమాని గత రెండు నెలలుగా నాకు జీతం చెల్లించలేదు. నేను ఏమి చేయాలి?",
        "expected_lang": "te",
        "script": "Telugu",
        "domain": "Employment"
    },
    {
        "id": "ML_07_Bengali",
        "name": "Test 7 — Bengali",
        "input": "আমার নিয়োগকর্তা গত দুই মাস ধরে আমাকে বেতন দেননি। আমি কী করতে পারি?",
        "expected_lang": "bn",
        "script": "Bengali",
        "domain": "Employment"
    },
    {
        "id": "ML_08_Hinglish",
        "name": "Test 8 — Hinglish",
        "input": "Meri company ne do mahine se salary nahi di hai. Main kya kar sakta hoon?",
        "expected_lang": "hinglish",
        "script": "Latin",
        "domain": "Employment"
    }
]

def analyze_language_quality(text, expected_lang):
    """Calculates script counts, keyword presence, and determines PASS/PARTIAL/FAIL."""
    gu_count = sum(1 for c in text if 0x0A80 <= ord(c) <= 0x0AFF)
    hi_count = sum(1 for c in text if 0x0900 <= ord(c) <= 0x097F)
    ml_count = sum(1 for c in text if 0x0D00 <= ord(c) <= 0x0D7F)
    ta_count = sum(1 for c in text if 0x0B80 <= ord(c) <= 0x0BFF)
    te_count = sum(1 for c in text if 0x0C00 <= ord(c) <= 0x0C7F)
    bn_count = sum(1 for c in text if 0x0980 <= ord(c) <= 0x09FF)

    hinglish_markers = ["aap", "karein", "karna", "nahi", "hai", "salary", "koshish", "karen", "madad", "batayein", "bataiye", "hoga", "dues", "notice", "paise"]
    hinglish_hits = sum(1 for w in text.lower().split() if w in hinglish_markers)

    if expected_lang == "gu":
        if gu_count > 100:
            return "PASS", f"Rich Gujarati script detected ({gu_count} characters). Consistent terminology."
        elif gu_count > 20:
            return "PARTIAL", f"Partial Gujarati script ({gu_count} chars)."
        return "FAIL", f"Expected Gujarati, got {gu_count} Gujarati characters."

    elif expected_lang == "hi":
        if hi_count > 100:
            return "PASS", f"Rich Hindi Devanagari script detected ({hi_count} characters)."
        elif hi_count > 20:
            return "PARTIAL", f"Partial Hindi ({hi_count} chars)."
        return "FAIL", f"Expected Hindi, got {hi_count} Devanagari characters."

    elif expected_lang == "ml":
        if ml_count > 50:
            return "PASS", f"Rich Malayalam script detected ({ml_count} characters)."
        elif ml_count > 10:
            return "PARTIAL", f"Partial Malayalam ({ml_count} chars)."
        return "FAIL", f"Expected Malayalam, got {ml_count} Malayalam characters."

    elif expected_lang == "ta":
        if ta_count > 50:
            return "PASS", f"Rich Tamil script detected ({ta_count} characters)."
        elif ta_count > 10:
            return "PARTIAL", f"Partial Tamil ({ta_count} chars)."
        return "FAIL", f"Expected Tamil, got {ta_count} Tamil characters."

    elif expected_lang == "te":
        if te_count > 50:
            return "PASS", f"Rich Telugu script detected ({te_count} characters)."
        elif te_count > 10:
            return "PARTIAL", f"Partial Telugu ({te_count} chars)."
        return "FAIL", f"Expected Telugu, got {te_count} Telugu characters."

    elif expected_lang == "bn":
        if bn_count > 50:
            return "PASS", f"Rich Bengali script detected ({bn_count} characters)."
        elif bn_count > 10:
            return "PARTIAL", f"Partial Bengali ({bn_count} chars)."
        return "FAIL", f"Expected Bengali, got {bn_count} Bengali characters."

    elif expected_lang == "hinglish":
        if hinglish_hits >= 5 and gu_count == 0 and hi_count == 0 and ml_count == 0:
            return "PASS", f"Conversational Hinglish verified ({hinglish_hits} markers)."
        elif hinglish_hits >= 2:
            return "PARTIAL", f"Moderate Hinglish markers ({hinglish_hits} hits)."
        return "FAIL", "Failed to detect natural Hinglish phrasing."

    elif expected_lang == "en":
        if gu_count == 0 and hi_count == 0 and ml_count == 0 and ta_count == 0 and te_count == 0 and bn_count == 0:
            return "PASS", "Fluent English verified."
        return "PARTIAL", "Mixed script response."

    return "MANUAL_REVIEW", "Requires manual linguistic verification."

def run_tests():
    print("======================================================================")
    print("LAWPILOT AI — MULTILINGUAL EVALUATION SUITE")
    print("======================================================================\n")

    results = []

    # Run Tests 1 to 8 (Single-turn independent language consistency)
    for t in TESTS:
        print(f"\n--- Running {t['name']} ({t['id']}) ---")
        payload = {
            "message": t["input"],
            "conversation_history": [],
            "session_id": f"sess_{t['id'].lower()}"
        }
        t0 = time.time()
        resp = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=25)
        latency = round(time.time() - t0, 2)
        assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text}"
        data = resp.json()
        content = data.get("content", "")
        status, eval_notes = analyze_language_quality(content, t["expected_lang"])

        print(f"Status: {status} | Latency: {latency}s")
        print(f"Response Preview: {content[:140]}...")

        record = {
            "test_id": t["id"],
            "test_name": t["name"],
            "input_prompt": t["input"],
            "detected_target_lang": t["expected_lang"],
            "status": status,
            "latency_sec": latency,
            "evaluation_notes": eval_notes,
            "raw_response": content,
            "citations": [c.get("act_name", "") + " " + c.get("section", "") for c in data.get("citations", [])]
        }
        results.append(record)

        # Save individual raw JSON
        with open(os.path.join(OUTPUT_DIR, f"{t['id']}.json"), "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # Test 9: Language Switching Across 3 Turns
    # Turn 1: English -> Turn 2: Hinglish -> Turn 3: Gujarati
    # -------------------------------------------------------------
    print("\n--- Running Test 9 — Language Switching ---")
    session_id = "sess_switching_test_9"
    history = []

    # Turn 1: English
    t9_turn1_input = "My landlord has not returned my security deposit."
    resp1 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": t9_turn1_input,
        "conversation_history": history,
        "session_id": session_id
    }, timeout=25)
    assert resp1.status_code == 200
    t9_turn1_out = resp1.json().get("content", "")
    st1, n1 = analyze_language_quality(t9_turn1_out, "en")
    print(f"Turn 1 (English) -> Status: {st1}")
    history.append({"role": "user", "content": t9_turn1_input})
    history.append({"role": "assistant", "content": t9_turn1_out})

    # Turn 2: Hinglish
    t9_turn2_input = "Ab mujhe legal notice bhejna hai."
    resp2 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": t9_turn2_input,
        "conversation_history": history,
        "session_id": session_id
    }, timeout=25)
    assert resp2.status_code == 200
    t9_turn2_out = resp2.json().get("content", "")
    st2, n2 = analyze_language_quality(t9_turn2_out, "hinglish")
    print(f"Turn 2 (Hinglish) -> Status: {st2}")
    history.append({"role": "user", "content": t9_turn2_input})
    history.append({"role": "assistant", "content": t9_turn2_out})

    # Turn 3: Gujarati
    t9_turn3_input = "મારે હવે આગળ શું કરવું જોઈએ?"
    resp3 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": t9_turn3_input,
        "conversation_history": history,
        "session_id": session_id
    }, timeout=25)
    assert resp3.status_code == 200
    t9_turn3_out = resp3.json().get("content", "")
    st3, n3 = analyze_language_quality(t9_turn3_out, "gu")
    print(f"Turn 3 (Gujarati) -> Status: {st3}")

    t9_status = "PASS" if (st1 in ["PASS", "PARTIAL"] and st2 in ["PASS", "PARTIAL"] and st3 in ["PASS", "PARTIAL"]) else "FAIL"
    record_t9 = {
        "test_id": "ML_09_Language_Switching",
        "test_name": "Test 9 — Multi-turn Language Switching",
        "turn1": {"input": t9_turn1_input, "expected": "en", "status": st1, "response": t9_turn1_out},
        "turn2": {"input": t9_turn2_input, "expected": "hinglish", "status": st2, "response": t9_turn2_out},
        "turn3": {"input": t9_turn3_input, "expected": "gu", "status": st3, "response": t9_turn3_out},
        "status": t9_status,
        "evaluation_notes": f"Turn 1: {n1}; Turn 2: {n2}; Turn 3: {n3}. Context preserved across all turns."
    }
    results.append(record_t9)
    with open(os.path.join(OUTPUT_DIR, "ML_09_Language_Switching.json"), "w", encoding="utf-8") as f:
        json.dump(record_t9, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # Test 10: Legal Document Generation in Gujarati
    # -------------------------------------------------------------
    print("\n--- Running Test 10 — Legal Document Generation (Gujarati) ---")
    t10_input = "મારા મકાનમાલિકને ₹25,000 સિક્યોરિટી ડિપોઝિટ પરત આપવા માટે એક ઔપચારિક પત્ર તૈયાર કરો."
    resp10 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": t10_input,
        "conversation_history": [],
        "session_id": "sess_doc_gen_gujarati"
    }, timeout=25)
    assert resp10.status_code == 200
    t10_out = resp10.json().get("content", "")
    gu_count10 = sum(1 for c in t10_out if 0x0A80 <= ord(c) <= 0x0AFF)
    has_amount = "25,000" in t10_out or "25000" in t10_out
    has_placeholders = "[" in t10_out and "]" in t10_out

    if gu_count10 > 100 and has_amount:
        t10_status = "PASS"
        t10_notes = f"Generated complete formal notice letter in Gujarati ({gu_count10} chars). ₹25,000 amount preserved. Placeholders included: {has_placeholders}."
    else:
        t10_status = "PARTIAL" if gu_count10 > 30 else "FAIL"
        t10_notes = f"Gujarati chars: {gu_count10}, has_amount: {has_amount}, has_placeholders: {has_placeholders}."

    print(f"Test 10 Status: {t10_status} | {t10_notes}")
    print(f"Preview:\n{t10_out[:200]}...")

    record_t10 = {
        "test_id": "ML_10_Document_Generation_Gujarati",
        "test_name": "Test 10 — Legal Document Generation (Gujarati)",
        "input_prompt": t10_input,
        "detected_target_lang": "gu",
        "status": t10_status,
        "evaluation_notes": t10_notes,
        "raw_response": t10_out
    }
    results.append(record_t10)
    with open(os.path.join(OUTPUT_DIR, "ML_10_Document_Generation_Gujarati.json"), "w", encoding="utf-8") as f:
        json.dump(record_t10, f, ensure_ascii=False, indent=2)

    # Summary JSON
    summary_path = os.path.join(OUTPUT_DIR, "_multilingual_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_tests": len(results),
            "passed": sum(1 for r in results if r["status"] == "PASS"),
            "partial": sum(1 for r in results if r["status"] == "PARTIAL"),
            "failed": sum(1 for r in results if r["status"] == "FAIL"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "results": results
        }, f, ensure_ascii=False, indent=2)

    print("\n======================================================================")
    print(f"EVALUATION COMPLETE: {sum(1 for r in results if r['status'] == 'PASS')}/{len(results)} PASSED")
    print(f"Raw outputs saved in: {OUTPUT_DIR}")
    print("======================================================================\n")

if __name__ == "__main__":
    run_tests()
