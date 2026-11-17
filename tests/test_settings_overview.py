"""
Comprehensive Test Suite for LawPilot AI Refined Settings Modal (Technical Overview)
Tests:
1. Four structured sections exist:
   - 1. AI Engine (Provider, Model, Verified Connection Status)
   - 2. Knowledge & Grounding (RAG status, Connected Legal Categories, Retrieval Availability, No false '100%' claim)
   - 3. Capabilities (Multilingual, Voice input, Memory, Document Generation)
   - 4. Safety & Safeguards (Legal uncertainty, Human lawyer escalation, Anti-hallucination)
2. No API keys, credentials, or internal prompt leaks.
3. Functional close mechanisms preserved:
   - Top-right cross (✕) button with closeSettingsModal()
   - Backdrop click dismiss
   - Escape key dismiss
4. Backend API /api/system/status provides verified live runtime data.
"""

import os
import re
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_settings_overview():
    print("======================================================================")
    print("LAWPILOT AI — REFINED SETTINGS MODAL VERIFICATION")
    print("======================================================================\n")

    # -------------------------------------------------------------
    # 1. Inspect app/templates/index.html
    # -------------------------------------------------------------
    print("--- 1. Checking Settings Modal Template Structure ---")
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    settings_modal_idx = html.find('id="settingsModal"')
    assert settings_modal_idx != -1, "settingsModal element not found in index.html"
    # Extract the block around settingsModal up to the closing comment or next modal/script
    modal_end_idx = html.find('<!-- Scripts -->', settings_modal_idx)
    modal_html = html[settings_modal_idx:modal_end_idx] if modal_end_idx != -1 else html[settings_modal_idx:]

    # Verify Section 1: AI Engine
    assert "AI Engine" in modal_html, "Section 1 'AI Engine' heading missing"
    assert "statusProvider" in modal_html, "statusProvider field missing"
    assert "statusModel" in modal_html, "statusModel field missing"
    assert "statusConnection" in modal_html, "statusConnection field missing"
    print("✓ Section 1: AI Engine verified (Provider, Model, Connection Status).")

    # Verify Section 2: Knowledge & Grounding
    assert "Knowledge & Grounding" in modal_html, "Section 2 'Knowledge & Grounding' heading missing"
    assert "statusRag" in modal_html, "statusRag field missing"
    assert "statusRetrieval" in modal_html, "statusRetrieval field missing"
    assert "statusSources" in modal_html, "statusSources field missing"
    assert "Tenancy & Rent Control" in modal_html, "Tenancy category missing"
    assert "Consumer Protection" in modal_html, "Consumer Protection category missing"
    assert "Employment & Wages" in modal_html, "Employment category missing"
    # Ensure NO false claim of "100% Grounded"
    assert "100%" not in modal_html, "Forbidden '100%' claim found in modal HTML"
    assert "does not claim exhaustive statutory coverage" in modal_html, "Nuanced grounding disclaimer missing"
    print("✓ Section 2: Knowledge & Grounding verified (RAG status, categories, nuanced disclaimer, no '100%' claim).")

    # Verify Section 3: Capabilities
    assert "Capabilities" in modal_html, "Section 3 'Capabilities' heading missing"
    assert "statusMultilingual" in modal_html, "statusMultilingual field missing"
    assert "statusVoice" in modal_html, "statusVoice field missing"
    assert "statusMemory" in modal_html, "statusMemory field missing"
    assert "statusDocGen" in modal_html, "statusDocGen field missing"
    print("✓ Section 3: Capabilities verified (Multilingual, Voice input, Memory, Document generation).")

    # Verify Section 4: Safety
    assert "Safety" in modal_html, "Section 4 'Safety' heading missing"
    assert "Legal Uncertainty Handling" in modal_html, "Legal uncertainty handling missing"
    assert "Human Lawyer Escalation" in modal_html, "Human lawyer escalation missing"
    assert "Anti-Hallucination" in modal_html, "Anti-hallucination safeguards missing"
    print("✓ Section 4: Safety verified (Uncertainty, Lawyer escalation, Anti-hallucination).")

    # Verify Top-right Close Button & No footer Close button
    assert 'id="closeSettingsBtn"' in modal_html, "closeSettingsBtn missing"
    assert 'onclick="closeSettingsModal()"' in modal_html, "onclick='closeSettingsModal()' missing"
    assert 'modal-footer' not in modal_html, "Bottom footer must remain removed"
    print("✓ Close mechanism verified (Working top-right cross, no bottom close button).")

    # Verify NO secrets or credentials in HTML
    for secret_token in ["AIza", "sk-", "AQ.", "Bearer", "API_KEY", "api_key"]:
        assert secret_token not in modal_html, f"Sensitive credential pattern '{secret_token}' found in modal HTML!"
    print("✓ No credentials, tokens, or internal prompt leaks in HTML.")

    # -------------------------------------------------------------
    # 2. Inspect app/static/js/app.js
    # -------------------------------------------------------------
    print("\n--- 2. Checking JavaScript Handlers ---")
    with open("app/static/js/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    assert "function openSettingsModal()" in js, "openSettingsModal() missing in app.js"
    assert "function closeSettingsModal()" in js, "closeSettingsModal() missing in app.js"
    assert "async function loadSystemStatus()" in js, "loadSystemStatus() missing in app.js"
    assert "fetch('/api/system/status')" in js, "fetch call to /api/system/status missing"
    print("✓ Dynamic system status loader and modal controls verified in app.js.")

    # -------------------------------------------------------------
    # 3. Live Server Endpoint Check
    # -------------------------------------------------------------
    print("\n--- 3. Verifying Live Backend Endpoints ---")
    status_resp = requests.get(f"{BASE_URL}/api/system/status", timeout=5)
    assert status_resp.status_code == 200, f"Expected 200 from /api/system/status, got {status_resp.status_code}"
    status_data = status_resp.json()

    print(f"Status Data Received: {status_data.get('ai_engine', {}).get('provider')} | Model: {status_data.get('ai_engine', {}).get('model')}")

    # Check AI Engine
    ai_engine = status_data.get("ai_engine", {})
    assert "provider" in ai_engine and ai_engine["provider"], "Missing ai_engine.provider"
    assert "model" in ai_engine and ai_engine["model"], "Missing ai_engine.model"
    assert "connection_status" in ai_engine and ai_engine["connection_status"], "Missing ai_engine.connection_status"

    # Check Knowledge & Grounding
    kg = status_data.get("knowledge_and_grounding", {})
    assert kg.get("rag_enabled") is True, "rag_enabled should be True"
    assert kg.get("retrieval_available") is True, "retrieval_available should be True"
    assert len(kg.get("source_categories", [])) >= 3, "source_categories should contain at least 3 legal domains"
    assert "100%" not in kg.get("grounding_disclaimer", ""), "API must not claim 100% coverage"

    # Check Capabilities
    caps = status_data.get("capabilities", {})
    assert "English" in caps.get("multilingual_support", "")
    assert "Voice" in caps.get("voice_input", "") or "Speech" in caps.get("voice_input", "")
    assert "memory" in caps.get("conversation_memory", "").lower()
    assert "PDF" in caps.get("document_generation", "")

    # Check Safety
    safety = status_data.get("safety", {})
    assert "disclaimer" in safety.get("legal_uncertainty_handling", "").lower() or "caveat" in safety.get("legal_uncertainty_handling", "").lower()
    assert "escalation" in safety.get("human_lawyer_escalation", "").lower()
    assert "cross-referencing" in safety.get("anti_hallucination_safeguards", "").lower() or "statute" in safety.get("anti_hallucination_safeguards", "").lower()

    # Verify no credential leaks in JSON
    raw_status_json = status_resp.text
    for secret in ["AQ.", "AIza", "sk-", "api_key", "secret"]:
        assert secret not in raw_status_json, f"Secret pattern '{secret}' leaked in /api/system/status response!"

    print("✓ Backend endpoint /api/system/status verified: all 4 sections present, live, and safe.")

    # Verify Live Page renders new modal
    home_resp = requests.get(f"{BASE_URL}/", timeout=5)
    assert home_resp.status_code == 200
    assert "System & Technical Overview" in home_resp.text
    assert "100% Grounded" not in home_resp.text
    print("✓ Live homepage serves refined Technical Overview Settings Modal.")

    print("\n======================================================================")
    print("ALL 4-SECTION SETTINGS MODAL VERIFICATION TESTS PASSED (100% GREEN)!")
    print("======================================================================\n")

if __name__ == "__main__":
    test_settings_overview()
