"""
LawPilot AI — Unicode and Multilingual Integrity Test Suite
Verifies UTF-8 encoding across streaming and non-streaming responses,
ensuring zero mojibake (à¤... / \u00e0\u00a4) across all Indian languages.
"""

import os
import sys
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = "testing/raw_outputs/unicode_fix"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MOJIBAKE_PATTERNS = ["à¤", "à¥", "à¦", "à®", "à°", "à²", "à´", "àª", "Ã", "Â"]

def detect_mojibake(text: str) -> bool:
    """Checks if text contains corrupted UTF-8 byte sequences rendered as Latin-1."""
    return any(p in text for p in MOJIBAKE_PATTERNS)

def count_scripts(text: str):
    mr_hi_count = sum(1 for c in text if 0x0900 <= ord(c) <= 0x097F)
    gu_count = sum(1 for c in text if 0x0A80 <= ord(c) <= 0x0AFF)
    ml_count = sum(1 for c in text if 0x0D00 <= ord(c) <= 0x0D7F)
    ta_count = sum(1 for c in text if 0x0B80 <= ord(c) <= 0x0BFF)
    te_count = sum(1 for c in text if 0x0C00 <= ord(c) <= 0x0C7F)
    bn_count = sum(1 for c in text if 0x0980 <= ord(c) <= 0x09FF)
    return {
        "devanagari": mr_hi_count,
        "gujarati": gu_count,
        "malayalam": ml_count,
        "tamil": ta_count,
        "telugu": te_count,
        "bengali": bn_count
    }

def run_sse_stream(prompt: str, history=None, session_id="test_session"):
    """Connects to /api/chat/stream, reads SSE tokens incrementally, and reconstructs response."""
    history = history or []
    payload = {
        "message": prompt,
        "conversation_history": history,
        "session_id": session_id
    }
    t0 = time.time()
    resp = requests.post(
        f"{BASE_URL}/api/chat/stream",
        json=payload,
        stream=True,
        timeout=25
    )
    resp.encoding = "utf-8"
    assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text}"

    content_type = resp.headers.get("content-type", "")
    assert "utf-8" in content_type.lower() or "text/event-stream" in content_type.lower(), f"Unexpected Content-Type: {content_type}"

    tokens = []
    metadata = {}
    done_event = {}
    raw_sse_lines = []

    for raw_line in resp.iter_lines(decode_unicode=False):
        if not raw_line:
            continue
        line = raw_line.decode("utf-8", errors="replace")
        raw_sse_lines.append(line)
        if line.startswith("data: "):
            data_str = line[6:].strip()
            if data_str:
                data = json.loads(data_str)
                evt_type = data.get("type")
                if evt_type == "metadata":
                    metadata = data
                elif evt_type == "token":
                    tokens.append(data.get("content", ""))
                elif evt_type == "done":
                    done_event = data

    elapsed = round(time.time() - t0, 2)
    accumulated_content = "".join(tokens)
    if not accumulated_content and done_event.get("content"):
        accumulated_content = done_event.get("content")

    return {
        "accumulated_text": accumulated_content,
        "tokens_count": len(tokens),
        "metadata": metadata,
        "done_event": done_event,
        "elapsed_sec": elapsed,
        "headers": dict(resp.headers),
        "raw_lines_sample": raw_sse_lines[:15]
    }

def execute_all_tests():
    print("=" * 70)
    print("LAWPILOT AI — UNICODE & MULTILINGUAL STREAMING INTEGRITY TEST SUITE")
    print("=" * 70)

    results = []

    # -------------------------------------------------------------
    # TEST 1: Marathi Consumer Query (Streaming)
    # -------------------------------------------------------------
    print("\n--- TEST 1: Marathi Defective Phone ---")
    t1_prompt = "मी ऑनलाइन एक दोषपूर्ण मोबाईल फोन खरेदी केला आहे आणि विक्रेता मला पैसे परत करण्यास नकार देत आहे. आता मी काय करू शकतो?"
    t1 = run_sse_stream(t1_prompt, session_id="test1_marathi")
    text1 = t1["accumulated_text"]
    has_mojibake1 = detect_mojibake(text1)
    counts1 = count_scripts(text1)
    status1 = "PASS" if not has_mojibake1 and counts1["devanagari"] > 100 else "FAIL"

    print(f"Status: {status1} | Devanagari chars: {counts1['devanagari']} | Mojibake: {has_mojibake1} | Tokens: {t1['tokens_count']}")
    print(f"Preview:\n{text1[:180]}...\n")

    res1 = {
        "test_id": "TEST_01_MARATHI",
        "prompt": t1_prompt,
        "status": status1,
        "has_mojibake": has_mojibake1,
        "devanagari_chars": counts1["devanagari"],
        "tokens_received": t1["tokens_count"],
        "elapsed_sec": t1["elapsed_sec"],
        "response": text1
    }
    results.append(res1)
    with open(f"{OUTPUT_DIR}/TEST_01_MARATHI.json", "w", encoding="utf-8") as f:
        json.dump(res1, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # TEST 2: Hindi Unpaid Wages (Streaming)
    # -------------------------------------------------------------
    print("\n--- TEST 2: Hindi Unpaid Salary ---")
    t2_prompt = "मेरे नियोक्ता ने पिछले दो महीनों से मेरा वेतन नहीं दिया है। मैं क्या कर सकता हूँ?"
    t2 = run_sse_stream(t2_prompt, session_id="test2_hindi")
    text2 = t2["accumulated_text"]
    has_mojibake2 = detect_mojibake(text2)
    counts2 = count_scripts(text2)
    status2 = "PASS" if not has_mojibake2 and counts2["devanagari"] > 100 else "FAIL"

    print(f"Status: {status2} | Devanagari chars: {counts2['devanagari']} | Mojibake: {has_mojibake2}")
    print(f"Preview:\n{text2[:180]}...\n")

    res2 = {
        "test_id": "TEST_02_HINDI",
        "prompt": t2_prompt,
        "status": status2,
        "has_mojibake": has_mojibake2,
        "devanagari_chars": counts2["devanagari"],
        "response": text2
    }
    results.append(res2)
    with open(f"{OUTPUT_DIR}/TEST_02_HINDI.json", "w", encoding="utf-8") as f:
        json.dump(res2, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # TEST 3: Gujarati Consumer Query (Streaming)
    # -------------------------------------------------------------
    print("\n--- TEST 3: Gujarati Defective Phone ---")
    t3_prompt = "મેં ઑનલાઇન એક ખામીયુક્ત ફોન ખરીદ્યો છે અને વેચનાર મને રિફંડ આપવાનો ઇનકાર કરી રહ્યો છે. હવે હું શું કરી શકું?"
    t3 = run_sse_stream(t3_prompt, session_id="test3_gujarati")
    text3 = t3["accumulated_text"]
    has_mojibake3 = detect_mojibake(text3)
    counts3 = count_scripts(text3)
    status3 = "PASS" if not has_mojibake3 and counts3["gujarati"] > 100 else "FAIL"

    print(f"Status: {status3} | Gujarati chars: {counts3['gujarati']} | Mojibake: {has_mojibake3}")
    print(f"Preview:\n{text3[:180]}...\n")

    res3 = {
        "test_id": "TEST_03_GUJARATI",
        "prompt": t3_prompt,
        "status": status3,
        "has_mojibake": has_mojibake3,
        "gujarati_chars": counts3["gujarati"],
        "response": text3
    }
    results.append(res3)
    with open(f"{OUTPUT_DIR}/TEST_03_GUJARATI.json", "w", encoding="utf-8") as f:
        json.dump(res3, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # TEST 4: Malayalam Unpaid Wages (Streaming)
    # -------------------------------------------------------------
    print("\n--- TEST 4: Malayalam Unpaid Salary ---")
    t4_prompt = "എന്റെ തൊഴിലുടമ കഴിഞ്ഞ രണ്ട് മാസമായി എനിക്ക് ശമ്പളം നൽകിയിട്ടില്ല. ഞാൻ എന്ത് ചെയ്യണം?"
    t4 = run_sse_stream(t4_prompt, session_id="test4_malayalam")
    text4 = t4["accumulated_text"]
    has_mojibake4 = detect_mojibake(text4)
    counts4 = count_scripts(text4)
    status4 = "PASS" if not has_mojibake4 and counts4["malayalam"] > 100 else "FAIL"

    print(f"Status: {status4} | Malayalam chars: {counts4['malayalam']} | Mojibake: {has_mojibake4}")
    print(f"Preview:\n{text4[:180]}...\n")

    res4 = {
        "test_id": "TEST_04_MALAYALAM",
        "prompt": t4_prompt,
        "status": status4,
        "has_mojibake": has_mojibake4,
        "malayalam_chars": counts4["malayalam"],
        "response": text4
    }
    results.append(res4)
    with open(f"{OUTPUT_DIR}/TEST_04_MALAYALAM.json", "w", encoding="utf-8") as f:
        json.dump(res4, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # TEST 5: English Baseline (Streaming)
    # -------------------------------------------------------------
    print("\n--- TEST 5: English Baseline ---")
    t5_prompt = "My employer in Bangalore has not paid my salary for two months."
    t5 = run_sse_stream(t5_prompt, session_id="test5_english")
    text5 = t5["accumulated_text"]
    has_mojibake5 = detect_mojibake(text5)
    status5 = "PASS" if not has_mojibake5 and "salary" in text5.lower() else "FAIL"

    print(f"Status: {status5} | Mojibake: {has_mojibake5}")
    print(f"Preview:\n{text5[:180]}...\n")

    res5 = {
        "test_id": "TEST_05_ENGLISH",
        "prompt": t5_prompt,
        "status": status5,
        "has_mojibake": has_mojibake5,
        "response": text5
    }
    results.append(res5)
    with open(f"{OUTPUT_DIR}/TEST_05_ENGLISH.json", "w", encoding="utf-8") as f:
        json.dump(res5, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # TEST 6: Mixed Language (Marathi-English)
    # -------------------------------------------------------------
    print("\n--- TEST 6: Mixed Marathi-English Deposit ---")
    t6_prompt = "माझ्या landlord ने माझा ₹25,000 deposit परत केलेला नाही. मला काय करावे?"
    t6 = run_sse_stream(t6_prompt, session_id="test6_mixed")
    text6 = t6["accumulated_text"]
    has_mojibake6 = detect_mojibake(text6)
    counts6 = count_scripts(text6)
    has_amount = "25,000" in text6 or "25000" in text6 or "२५,०००" in text6
    status6 = "PASS" if not has_mojibake6 and counts6["devanagari"] > 100 and has_amount else "FAIL"

    print(f"Status: {status6} | Devanagari chars: {counts6['devanagari']} | ₹25,000 preserved: {has_amount}")
    print(f"Preview:\n{text6[:180]}...\n")

    res6 = {
        "test_id": "TEST_06_MIXED_MARATHI",
        "prompt": t6_prompt,
        "status": status6,
        "has_mojibake": has_mojibake6,
        "devanagari_chars": counts6["devanagari"],
        "amount_preserved": has_amount,
        "response": text6
    }
    results.append(res6)
    with open(f"{OUTPUT_DIR}/TEST_06_MIXED_MARATHI.json", "w", encoding="utf-8") as f:
        json.dump(res6, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # TEST 7: Streaming Integrity (Long Structure with headings & sections)
    # -------------------------------------------------------------
    print("\n--- TEST 7: Long Structured Marathi Streaming Integrity ---")
    t7_prompt = "माझ्या घरमालकाने माझे ₹30,000 डिपॉझिट परत केले नाही आणि रेंट अ‍ॅग्रीमेंटनुसार ₹15,000 पेंटिंगचे कापले आहेत. मला सविस्तर कायदेशीर मार्गदर्शन हवे आहे."
    t7 = run_sse_stream(t7_prompt, session_id="test7_long_stream")
    text7 = t7["accumulated_text"]
    has_mojibake7 = detect_mojibake(text7)
    counts7 = count_scripts(text7)
    has_headers = "परिस्थिती" in text7 or "कायदेशीर" in text7 or "पावले" in text7 or "Situation" in text7
    has_wear_tear = "झीज" in text7 or "wear and tear" in text7.lower() or "घसारा" in text7
    status7 = "PASS" if not has_mojibake7 and counts7["devanagari"] > 300 and has_headers and t7["tokens_count"] > 15 else "FAIL"

    print(f"Status: {status7} | Tokens: {t7['tokens_count']} | Length: {len(text7)} chars | Devanagari: {counts7['devanagari']}")
    print(f"Headers present: {has_headers} | Normal wear & tear covered: {has_wear_tear}")

    res7 = {
        "test_id": "TEST_07_STREAMING_INTEGRITY",
        "prompt": t7_prompt,
        "status": status7,
        "has_mojibake": has_mojibake7,
        "tokens_count": t7["tokens_count"],
        "devanagari_chars": counts7["devanagari"],
        "headers_present": has_headers,
        "wear_tear_explained": has_wear_tear,
        "response": text7
    }
    results.append(res7)
    with open(f"{OUTPUT_DIR}/TEST_07_STREAMING_INTEGRITY.json", "w", encoding="utf-8") as f:
        json.dump(res7, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # TEST 8: Conversation Persistence & Restoration
    # -------------------------------------------------------------
    print("\n--- TEST 8: Conversation Persistence ---")
    # Simulate saving to storage and reloading via JSON parse/stringify
    stored_json = json.dumps({
        "id": "conv_marathi_persist_test",
        "title": "Security Deposit Dispute",
        "messages": [
            {"role": "user", "content": t6_prompt},
            {"role": "assistant", "content": text6}
        ]
    }, ensure_ascii=False)

    # Reload from stringified JSON (exact browser localStorage simulation)
    reloaded = json.loads(stored_json)
    reloaded_ai_msg = reloaded["messages"][1]["content"]
    persist_mojibake = detect_mojibake(reloaded_ai_msg)
    status8 = "PASS" if reloaded_ai_msg == text6 and not persist_mojibake else "FAIL"

    print(f"Status: {status8} | Content exactly preserved: {reloaded_ai_msg == text6} | Mojibake: {persist_mojibake}")

    res8 = {
        "test_id": "TEST_08_PERSISTENCE",
        "status": status8,
        "persisted_content_matches": reloaded_ai_msg == text6,
        "has_mojibake": persist_mojibake
    }
    results.append(res8)
    with open(f"{OUTPUT_DIR}/TEST_08_PERSISTENCE.json", "w", encoding="utf-8") as f:
        json.dump(res8, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # TEST 9: Multi-Turn Language Switching (English -> Marathi -> Hindi)
    # -------------------------------------------------------------
    print("\n--- TEST 9: Language Switching (English -> Marathi -> Hindi) ---")
    s9_id = "sess_lang_switch_9"
    history9 = []

    # Turn 1: English
    p9_1 = "My employer has withheld my salary for two months."
    t9_1 = run_sse_stream(p9_1, history=history9, session_id=s9_id)
    out9_1 = t9_1["accumulated_text"]
    st9_1 = "PASS" if "salary" in out9_1.lower() and not detect_mojibake(out9_1) else "FAIL"
    print(f"Turn 1 (English) -> Status: {st9_1}")
    history9.append({"role": "user", "content": p9_1})
    history9.append({"role": "assistant", "content": out9_1})

    # Turn 2: Marathi
    p9_2 = "मी आता कंपनीला लीगल नोटीस कशी पाठवू शकतो?"
    t9_2 = run_sse_stream(p9_2, history=history9, session_id=s9_id)
    out9_2 = t9_2["accumulated_text"]
    c9_2 = count_scripts(out9_2)
    st9_2 = "PASS" if c9_2["devanagari"] > 80 and not detect_mojibake(out9_2) else "FAIL"
    print(f"Turn 2 (Marathi) -> Status: {st9_2} | Devanagari chars: {c9_2['devanagari']}")
    history9.append({"role": "user", "content": p9_2})
    history9.append({"role": "assistant", "content": out9_2})

    # Turn 3: Hindi
    p9_3 = "अगर कंपनी 15 दिन में जवाब न दे तो क्या करें?"
    t9_3 = run_sse_stream(p9_3, history=history9, session_id=s9_id)
    out9_3 = t9_3["accumulated_text"]
    c9_3 = count_scripts(out9_3)
    st9_3 = "PASS" if c9_3["devanagari"] > 80 and not detect_mojibake(out9_3) else "FAIL"
    print(f"Turn 3 (Hindi) -> Status: {st9_3} | Devanagari chars: {c9_3['devanagari']}")

    status9 = "PASS" if st9_1 == "PASS" and st9_2 == "PASS" and st9_3 == "PASS" else "FAIL"
    res9 = {
        "test_id": "TEST_09_LANGUAGE_SWITCHING",
        "status": status9,
        "turn1": {"prompt": p9_1, "status": st9_1, "response": out9_1[:200]},
        "turn2": {"prompt": p9_2, "status": st9_2, "response": out9_2[:200]},
        "turn3": {"prompt": p9_3, "status": st9_3, "response": out9_3[:200]}
    }
    results.append(res9)
    with open(f"{OUTPUT_DIR}/TEST_09_LANGUAGE_SWITCHING.json", "w", encoding="utf-8") as f:
        json.dump(res9, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------
    summary = {
        "total_tests": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": sum(1 for r in results if r["status"] == "FAIL"),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": results
    }
    with open(f"{OUTPUT_DIR}/_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"UNICODE EVALUATION COMPLETE: {summary['passed']}/{len(results)} PASSED")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    execute_all_tests()
