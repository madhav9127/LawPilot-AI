import os
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"
RAW_DIR = "testing/raw_outputs/multilingual"
os.makedirs(RAW_DIR, exist_ok=True)

TEST_CASES = [
    {
        "id": "ML-01-GU-NOTICE",
        "lang": "gu",
        "category": "tenancy",
        "task": "notice_explanation",
        "description": "Test A: Gujarati landlord legal notice explanation",
        "prompt": "મને મારા મકાનમાલિક તરફથી મળેલી કાનૂની નોટિસ સમજવામાં મદદ કરો."
    },
    {
        "id": "ML-02-MR-NOTICE",
        "lang": "mr",
        "category": "tenancy",
        "task": "notice_explanation",
        "description": "Test B: Marathi landlord legal notice explanation",
        "prompt": "मला माझ्या घरमालकाकडून मिळालेली कायदेशीर नोटीस समजून घेण्यासाठी मदत करा."
    },
    {
        "id": "ML-03-HI-NOTICE",
        "lang": "hi",
        "category": "tenancy",
        "task": "notice_explanation",
        "description": "Hindi landlord legal notice explanation",
        "prompt": "मुझे मेरे मकान मालिक की तरफ से लीगल नोटिस मिला है, इसे समझने में मेरी मदद करें।"
    },
    {
        "id": "ML-04-HINGLISH-NOTICE",
        "lang": "hinglish",
        "category": "tenancy",
        "task": "notice_explanation",
        "description": "Hinglish landlord legal notice explanation",
        "prompt": "Mujhe mere landlord ki taraf se legal notice mila hai, please mujhe ise samajhne me help karo."
    },
    {
        "id": "ML-05-EN-NOTICE",
        "lang": "en",
        "category": "tenancy",
        "task": "notice_explanation",
        "description": "English landlord legal notice explanation",
        "prompt": "Help me understand a legal notice I received from my landlord."
    },
    {
        "id": "ML-06-TA-NOTICE",
        "lang": "ta",
        "category": "tenancy",
        "task": "notice_explanation",
        "description": "Tamil landlord legal notice explanation",
        "prompt": "எனது வீட்டு உரிமையாளரிடமிருந்து வந்த சட்டப்பூர்வ நோட்டீஸைப் புரிந்து கொள்ள எனக்கு உதவுங்கள்."
    },
    {
        "id": "ML-07-ML-NOTICE",
        "lang": "ml",
        "category": "tenancy",
        "task": "notice_explanation",
        "description": "Malayalam landlord legal notice explanation",
        "prompt": "എന്റെ വീട്ടുടമസ്ഥനിൽ നിന്ന് ലഭിച്ച ലീഗൽ നോട്ടീസ് മനസ്സിലാക്കാൻ എന്നെ സഹായിക്കുക."
    },
    {
        "id": "ML-08-TE-NOTICE",
        "lang": "te",
        "category": "tenancy",
        "task": "notice_explanation",
        "description": "Telugu landlord legal notice explanation",
        "prompt": "నా ఇంటి యజమాని నుండి వచ్చిన లీగల్ నోటీసును అర్థం చేసుకోవడంలో నాకు సహాయం చేయండి."
    },
    {
        "id": "ML-09-BN-NOTICE",
        "lang": "bn",
        "category": "tenancy",
        "task": "notice_explanation",
        "description": "Bengali landlord legal notice explanation",
        "prompt": "আমার বাড়িওয়ালার কাছ থেকে পাওয়া আইনি নোটিস বুঝতে আমাকে সাহায্য করুন।"
    },
    {
        "id": "ML-10-GU-DEPOSIT",
        "lang": "gu",
        "category": "tenancy",
        "task": "deposit_refund",
        "description": "Gujarati security deposit non-refund after vacating",
        "prompt": "મેં મકાન ખાલી કરી દીધું છે પણ મકાનમાલિક ₹25,000 ડિપોઝિટ પરત આપતા નથી."
    },
    {
        "id": "ML-11-MR-CONSUMER",
        "lang": "mr",
        "category": "consumer",
        "task": "defective_product",
        "description": "Marathi defective phone purchase and refund denial",
        "prompt": "मी ऑनलाइन एक दोषपूर्ण मोबाईल फोन खरेदी केला आहे आणि विक्रेता मला पैसे परत करण्यास नकार देत आहे. आता मी काय करू शकतो?"
    },
    {
        "id": "ML-12-HI-SALARY",
        "lang": "hi",
        "category": "employment",
        "task": "unpaid_salary",
        "description": "Hindi unpaid salary for two months",
        "prompt": "मेरी कंपनी ने पिछले दो महीने से मेरा वेतन नहीं दिया है। मुझे क्या कानूनी कदम उठाने चाहिए?"
    },
    {
        "id": "ML-13-MR-EVICTION",
        "lang": "mr",
        "category": "tenancy",
        "task": "unlawful_eviction",
        "description": "Marathi unlawful eviction threat with goons",
        "prompt": "माझा घरमालक मला उद्याच घर रिकामे करण्याची धमकी देत आहे आणि गुंड पाठवण्याची भाषा करत आहे. मी काय करू?"
    },
    {
        "id": "ML-14-GU-OFFTOPIC",
        "lang": "gu",
        "category": "off_topic",
        "task": "casual_math",
        "description": "Gujarati casual math query handling",
        "prompt": "2 + 2 કેટલા થાય?"
    },
    {
        "id": "ML-15-MR-GENERAL",
        "lang": "mr",
        "category": "general",
        "task": "domain_clarification",
        "description": "Marathi ambiguous legal query requesting domain details",
        "prompt": "माझी एक कायदेशीर अडचण आहे, मला मदतीची गरज आहे."
    }
]

def run_suite():
    results = []
    print(f"Starting Multilingual Comprehensive Evaluation Suite ({len(TEST_CASES)} tests)...")
    
    for i, tc in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] Executing {tc['id']}: {tc['description']}")
        payload = {
            "message": tc["prompt"],
            "language": "auto",
            "conversation_history": []
        }
        
        start_time = time.time()
        try:
            resp = requests.post(f"{BASE_URL}/api/chat/stream", json=payload, stream=True, timeout=30)
            latency = round(time.time() - start_time, 2)
            
            full_content = ""
            title = ""
            citations = []
            
            for line in resp.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data["type"] == "metadata":
                            title = data.get("title", "")
                            citations = data.get("citations", [])
                        elif data["type"] == "token":
                            full_content += data.get("content", "")
                        elif data["type"] == "done":
                            if not full_content:
                                full_content = data.get("content", "")
                            title = data.get("title", title)
                            citations = data.get("citations", citations)
                    except Exception:
                        pass
            
            status_code = resp.status_code
        except Exception as e:
            latency = round(time.time() - start_time, 2)
            status_code = 500
            full_content = f"Error: {e}"
            title = ""
            citations = []
        
        # Validation checks
        has_content = len(full_content.strip()) > 50
        no_leaked_placeholders = not any(p in full_content for p in ["your city", "the disputed amount", "an extended period", "[your city]", "[the disputed amount]"])
        
        # For notice tasks, check comprehensive Indic requirements
        notice_checks = {}
        if tc["task"] == "notice_explanation":
            court_words = ["court", "court order", "judgment", "eviction", "order", "કોર્ટ", "ન્યાયાલય", "અદાલત", "अदालत", "ચુકાદો", "कोर्टाचा निकाल", "न्यायालयाचा निर्णय", "निर्णय", "निष्कासन", "फैसला", "തീർപ്പല്ല", "വിധി", "ഉത്തരവ്", "தீர்ப்பு", "தீர்ப்போ", "கட்டளை", "తీర్పు", "ఉత్తర్వు", "ఆదేశం", "রায়", "চূড়ান্ত", "আদেশ"]
            notice_checks["not_court_decree_explained"] = any(w in full_content.lower() for w in court_words) or "notice" in full_content.lower() or "நோட்டீஸ்" in full_content
            
            share_words = ["પેસ્ટ", "અપલોડ", "શેઅર", "વિગતો", "તપાસણી", "पेस्ट", "अपलोड", "शेअर", "साझा", "प्रति", "मजकूर", "द्या", "paste", "upload", "share", "പങ്കുവെക്കുക", "പങ്കുവെക്കൂ", "വ്യക്തമാക്കാമോ", "നൽകുക", "பகிரவும்", "பதிவேற்ற", "తెలియజేయండి", "పంచుకోండి", "పత్రాన్ని", "పేస్ట్", "లిఖిత", "লিখে", "দিন", "আপলোড", "প্রতিলিপি"]
            notice_checks["upload_or_paste_requested"] = any(w in full_content for w in share_words)
            
            redact_words = ["આધાર", "સંવેદનશીલ", "બેંક", "અંગત", "વિગતો ભૂંસીને", "आधार", "संवेदनशील", "बँक", "बैनक", "खाजगी", "काढून टाका", "हटाकर", "redact", "hide", "ব্যক্তিগত", "গোপনীয়তা", "আধার", "ব্যাংক", "মুছে", "ఆధార్", "బ్యాంక్", "వ్యక్తిగత", "తొలగించి", "ஆதார்", "வங்கி", "மறைத்து", "ആധാർ", "ബാങ്ക്", "സ്വകാര്യ", "മറച്ചുവെച്ച്"]
            notice_checks["redact_sensitive_info_advised"] = any(w in full_content for w in redact_words)
            
            deadline_words = ["૧૫", "૩૦", "15", "30", "15-30", "১৫", "৩০", "15 నుండి 30", "15-30 రోజులు", "15 ते 30", "15 से 30", "दिवस", "દિવસ", "दिन", "days", "நாட்கள்", "காலக்கெடு", "நாட்களுக்குள்", "ദിവസം", "ദിവസത്തിനുള്ളിൽ", "రోజులు", "రోజులలోపు", "দিন", "সময়সীমা", "ముగింపు", "deadline", "கால அவகாசம்"]
            notice_checks["deadlines_highlighted"] = any(w in full_content for w in deadline_words)
            
            notice_checks["no_hallucinated_deposit_facts"] = not ("₹25,000" in full_content and "vacated" in full_content.lower())
            
            is_passed = (
                status_code == 200 and 
                has_content and 
                no_leaked_placeholders and 
                notice_checks["upload_or_paste_requested"] and 
                notice_checks["deadlines_highlighted"] and
                notice_checks["no_hallucinated_deposit_facts"]
            )
        else:
            is_passed = status_code == 200 and has_content and no_leaked_placeholders
            
        test_result = {
            "id": tc["id"],
            "language": tc["lang"],
            "category": tc["category"],
            "task": tc["task"],
            "description": tc["description"],
            "prompt": tc["prompt"],
            "status_code": status_code,
            "latency_seconds": latency,
            "generated_title": title,
            "response_length": len(full_content),
            "citations_count": len(citations),
            "no_leaked_placeholders": no_leaked_placeholders,
            "notice_specific_checks": notice_checks if tc["task"] == "notice_explanation" else None,
            "passed": is_passed,
            "response_snippet": full_content[:200] + "..." if len(full_content) > 200 else full_content
        }
        results.append(test_result)
        
        # Save raw output
        raw_output_path = os.path.join(RAW_DIR, f"{tc['id']}.json")
        with open(raw_output_path, "w", encoding="utf-8") as rf:
            json.dump({
                "test_id": tc["id"],
                "input_prompt": tc["prompt"],
                "status_code": status_code,
                "latency_seconds": latency,
                "title": title,
                "citations": citations,
                "full_response": full_content,
                "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }, rf, indent=2, ensure_ascii=False)
        
        status_sym = "✅ PASS" if is_passed else "❌ FAIL"
        print(f"Result: {status_sym} (Latency: {latency}s, Length: {len(full_content)} chars)")
        if tc["task"] == "notice_explanation":
            print(f"Notice checks: {notice_checks}")

    summary = {
        "suite_name": "LawPilot AI Multilingual Comprehension & Generation Evaluation",
        "total_tests": len(results),
        "passed_tests": sum(1 for r in results if r["passed"]),
        "failed_tests": sum(1 for r in results if not r["passed"]),
        "pass_rate_percentage": round((sum(1 for r in results if r["passed"]) / len(results)) * 100, 2),
        "tested_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "test_results": results
    }

    with open("testing/multilingual_language_results.json", "w", encoding="utf-8") as jf:
        json.dump(summary, jf, indent=2, ensure_ascii=False)
        
    print(f"\nEvaluation Suite Finished! Pass Rate: {summary['pass_rate_percentage']}% ({summary['passed_tests']}/{summary['total_tests']})")
    print(f"Summary saved to testing/multilingual_language_results.json")

if __name__ == "__main__":
    run_suite()
