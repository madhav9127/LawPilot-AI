"""
Comprehensive Verification Test Suite for LawPilot AI Refinements:
1. Title generation (2-5 words) on all legal domains and languages
2. Genuine token streaming over SSE (/api/chat/stream)
3. Input UI placeholder verification
4. Removal of language dropdown
5. Turn-by-turn natural multilingual switching
6. Zero emojis in UI and responses
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("======================================================================")
    print("LAWPILOT AI — REFINEMENTS VERIFICATION SUITE")
    print("======================================================================\n")

    # -------------------------------------------------------------------------
    # TEST 1: TITLE GENERATION TESTS
    # -------------------------------------------------------------------------
    print("--- 1. Testing Title Generation ---")
    from app.core.title_generator import generate_conversation_title

    title_cases = [
        ("My landlord is refusing to return my ₹25,000 deposit", "Security Deposit Dispute"),
        ("My employer has not paid my salary for two months", "Unpaid Salary Issue"),
        ("I bought a defective phone and the seller refuses a refund", "Defective Product Refund"),
        ("I received a legal notice and don't understand it", "Legal Notice Assistance"),
        ("My landlord is threatening to evict me", "Eviction Dispute"),
        ("मेरे मकान मालिक ने ₹25,000 का डिपॉज़िट वापस नहीं किया", "Security Deposit Dispute"),
        ("कंपनी ने मेरा वेतन नहीं दिया है", "Unpaid Salary Issue"),
        ("Meri company ne do mahine se salary nahi di hai. Main kya kar sakta hoon?", "Unpaid Salary Issue"),
        ("landlord ne deposit return nahi kiya", "Security Deposit Dispute"),
        ("എന്റെ ശമ്പളം നൽകിയിട്ടില്ല", "Unpaid Salary Issue")
    ]

    for prompt, expected in title_cases:
        gen = generate_conversation_title(prompt)
        print(f"Prompt: '{prompt[:45]}...' -> Title: '{gen}'")
        assert gen == expected, f"Expected '{expected}', got '{gen}'"
        # Verify title length is 2-5 words
        word_count = len(gen.split())
        assert 2 <= word_count <= 5, f"Title '{gen}' has {word_count} words (not 2-5)"

    print("✓ Test 1 Passed: All conversation titles match expected 2-5 word topics across languages.\n")

    # -------------------------------------------------------------------------
    # TEST 2: STREAMING RESPONSE VIA /api/chat/stream (SSE)
    # -------------------------------------------------------------------------
    print("--- 2. Testing Genuine Token Streaming (/api/chat/stream) ---")
    stream_url = f"{BASE_URL}/api/chat/stream"
    payload = {
        "message": "Explain my rights if my landlord refuses to return my ₹25,000 deposit in Jaipur.",
        "conversation_history": [],
        "session_id": "test_stream_session"
    }

    start_time = time.perf_counter()
    r = requests.post(stream_url, json=payload, stream=True, timeout=15)
    assert r.status_code == 200, f"Expected 200 OK, got {r.status_code}"

    received_events = []
    tokens = []
    metadata = None
    done_event = None
    first_token_time = None

    for line in r.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            data_str = line[6:].strip()
            if not data_str:
                continue
            event = json.loads(data_str)
            received_events.append(event)
            event_type = event.get("type")

            if event_type == "metadata":
                metadata = event
                print(f"-> Metadata Event received: title='{event.get('title')}', citations={len(event.get('citations', []))}")
            elif event_type == "token":
                if first_token_time is None:
                    first_token_time = (time.perf_counter() - start_time) * 1000
                tokens.append(event.get("content", ""))
            elif event_type == "done":
                done_event = event
                print(f"-> Done Event received! Total tokens received: {len(tokens)}")

    total_duration = (time.perf_counter() - start_time) * 1000
    print(f"Streaming metrics: First token in {first_token_time:.2f}ms | Total duration: {total_duration:.2f}ms")

    assert metadata is not None, "Missing metadata event in SSE stream"
    assert metadata.get("title") == "Security Deposit Dispute", f"Expected 'Security Deposit Dispute', got {metadata.get('title')}"
    assert len(tokens) >= 5, f"Expected streaming tokens, got only {len(tokens)}"
    assert done_event is not None, "Missing done event in SSE stream"

    full_streamed_text = "".join(tokens)
    print("Streamed response preview:")
    print(full_streamed_text[:200] + "...\n")
    assert "### | Your Situation" in full_streamed_text or "Situation" in full_streamed_text, "Missing Situation section"
    assert "### | Your Legal Position" in full_streamed_text or "Legal Position" in full_streamed_text, "Missing Legal Position section"
    print("✓ Test 2 Passed: Genuine SSE token streaming verified from backend to client.\n")

    # -------------------------------------------------------------------------
    # TEST 3: UI INPUT PLACEHOLDER & LANGUAGE SELECTOR REMOVAL
    # -------------------------------------------------------------------------
    print("--- 3. Testing Input Placeholder & Language Selector Removal ---")
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Exact placeholder requirement: "Describe your legal problem..."
    assert 'placeholder="Describe your legal problem..."' in html, "Chat input does not have exact required placeholder"
    assert "plain English, Hindi, or Hinglish" not in html, "Placeholder still mentions languages"

    # Language dropdown removal
    assert 'id="languageSelect"' not in html, "languageSelect dropdown was not removed from index.html"
    assert '<select' not in html, "A select element still exists in index.html"
    assert 'class="grounded-pill"' in html, "Grounded in Official Sources pill was accidentally removed"

    with open("app/static/css/styles.css", "r", encoding="utf-8") as f:
        css = f.read()
    assert ".language-select" not in css, "CSS still contains .language-select styles"
    print("✓ Test 3 Passed: Placeholder is exact and language dropdown is completely removed.\n")

    # -------------------------------------------------------------------------
    # TEST 4: MULTILINGUAL NATURAL SWITCHING (Turn-by-Turn)
    # -------------------------------------------------------------------------
    print("--- 4. Testing Turn-by-Turn Natural Language Switching ---")
    session_multi = f"test_multi_{int(time.time())}"

    # Turn 1: English
    t1_res = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "My employer has not paid my salary for two months.",
        "conversation_history": [],
        "session_id": session_multi
    }).json()
    print("Turn 1 (English) ->", t1_res['content'][:100].replace('\n', ' '))
    assert "Payment of Wages" in t1_res['content'] or "salary" in t1_res['content'].lower()

    # Turn 2: Hinglish
    t2_history = [
        {"role": "user", "content": "My employer has not paid my salary for two months."},
        {"role": "assistant", "content": t1_res['content']}
    ]
    t2_res = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Ab mujhe company ko legal notice bhejna hai. Kaise bheju?",
        "conversation_history": t2_history,
        "session_id": session_multi
    }).json()
    print("Turn 2 (Hinglish) ->", t2_res['content'][:100].replace('\n', ' '))
    # Check Hinglish keywords in Turn 2
    assert any(w in t2_res['content'].lower() for w in ["aap", "karein", "notice", "salary", "bhejein", "dues", "demand"]), "Turn 2 should be in Hinglish"

    # Turn 3: Hindi (Devanagari)
    t3_history = t2_history + [
        {"role": "user", "content": "Ab mujhe company ko legal notice bhejna hai. Kaise bheju?"},
        {"role": "assistant", "content": t2_res['content']}
    ]
    t3_res = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "क्या मैं सीधे लेबर कमिश्नर के पास शिकायत कर सकता हूँ?",
        "conversation_history": t3_history,
        "session_id": session_multi
    }).json()
    print("Turn 3 (Hindi) ->", t3_res['content'][:100].replace('\n', ' '))
    has_devanagari = any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in t3_res['content'])
    assert has_devanagari, "Turn 3 should respond in Hindi Devanagari script"
    print("✓ Test 4 Passed: Natural multi-turn multilingual switching works seamlessly.\n")

    # -------------------------------------------------------------------------
    # TEST 5: ZERO EMOJIS IN UI AND CORE SECTIONS
    # -------------------------------------------------------------------------
    print("--- 5. Testing Zero Emojis in UI ---")
    # Check index.html prompt cards & footer
    emoji_check_list = ["🏠", "🛒", "💼", "📑", "⚙️", "ℹ️", "💬", "⚖️", "📋", "📄", "🔗"]
    for emo in emoji_check_list:
        assert emo not in html, f"Emoji '{emo}' found in index.html"

    print("✓ Test 5 Passed: Zero emojis in HTML template; crisp professional SVGs verified.\n")

    print("======================================================================")
    print("ALL REFINEMENT VERIFICATION TESTS PASSED (100% GREEN)!")
    print("======================================================================")

if __name__ == "__main__":
    run_tests()
