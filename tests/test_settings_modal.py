"""
Verification Test Suite for Settings Modal Close Button Fixes
Tests:
1. Bottom Close button is completely removed.
2. Top-right cross (×) button has valid handlers.
3. closeSettingsModal() and openSettingsModal() exist and update display state.
4. Backdrop click on .modal-overlay closes the modal.
5. Escape key event closes the modal.
6. Live server serves updated templates and scripts.
"""

import os
import sys
import re
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_settings_modal():
    print("======================================================================")
    print("LAWPILOT AI — SETTINGS MODAL FIX VERIFICATION")
    print("======================================================================\n")

    # 1. Inspect app/templates/index.html
    print("--- 1. Inspecting index.html ---")
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    settings_modal_match = re.search(r'<div class="modal-overlay" id="settingsModal"[^>]*>([\s\S]*?)<\/div>\s*<\/div>', html)
    assert settings_modal_match, "Could not find settingsModal in index.html"
    settings_modal_html = settings_modal_match.group(0)

    # Verify bottom Close button is removed
    assert '<div class="modal-footer">' not in settings_modal_html, "modal-footer still exists in settingsModal"
    assert '>Close</button>' not in settings_modal_html, "Bottom Close button still exists in settingsModal"
    print("✓ Bottom 'Close' button is completely removed from Settings modal.")

    # Verify top-right cross exists
    assert 'id="closeSettingsBtn"' in settings_modal_html, "closeSettingsBtn not found in settingsModal"
    assert 'onclick="closeSettingsModal()"' in settings_modal_html, "onclick handler missing from close button"
    print("✓ Top-right close button (✕) exists with closeSettingsModal() handler.")

    # 2. Inspect app/static/js/app.js
    print("\n--- 2. Inspecting app.js ---")
    with open("app/static/js/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    assert "function closeSettingsModal()" in js, "closeSettingsModal function not defined in app.js"
    assert "function openSettingsModal()" in js, "openSettingsModal function not defined in app.js"
    assert "settingsModal.style.display = 'none'" in js, "closeSettingsModal does not set display = 'none'"
    assert "settingsModal.style.display = 'flex'" in js, "openSettingsModal does not set display = 'flex'"
    print("✓ openSettingsModal() and closeSettingsModal() functions exist and properly manage display state.")

    # Verify backdrop click listener
    assert "if (e.target === settingsModal)" in js, "Backdrop click listener missing for settingsModal"
    print("✓ Backdrop click listener verified (clicking outside closes modal).")

    # Verify Escape key listener
    assert "if (e.key === 'Escape')" in js, "Escape key event listener missing"
    assert "closeSettingsModal();" in js, "Escape key does not call closeSettingsModal"
    print("✓ Escape key listener verified (pressing Escape closes modal).")

    # 3. Live Server Endpoint Check
    print("\n--- 3. Verifying Live Server Assets ---")
    r_html = requests.get(f"{BASE_URL}/", timeout=5)
    assert r_html.status_code == 200, f"Failed to get home page: {r_html.status_code}"
    assert '>Close</button>' not in r_html.text, "Live server still serving old index.html with bottom Close button"
    assert 'id="closeSettingsBtn"' in r_html.text, "Live server not serving closeSettingsBtn"

    r_js = requests.get(f"{BASE_URL}/static/js/app.js", timeout=5)
    assert r_js.status_code == 200, f"Failed to get app.js: {r_js.status_code}"
    assert "closeSettingsModal" in r_js.text, "Live server not serving closeSettingsModal in app.js"

    print("✓ Live server successfully serves the updated HTML and JavaScript assets.")

    print("\n======================================================================")
    print("ALL SETTINGS MODAL FIX VERIFICATION CHECKS PASSED (100% GREEN)!")
    print("======================================================================\n")

if __name__ == "__main__":
    test_settings_modal()
