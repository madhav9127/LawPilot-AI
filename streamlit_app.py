"""
LawPilot AI — Simple, Single-Page AI Legal Chatbot for India
Refined interface matching the official legal tech design.
"""

import streamlit as st
import os
import sys
import uuid

# Ensure root path is imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.schemas import LanguageEnum, CaseCategoryEnum, DocumentTypeEnum, DocumentGenerationRequest
from app.core.llm_provider import LLMProviderFactory, reset_memory
from app.core.document_generator import DocumentGenerator

st.set_page_config(
    page_title="LawPilot AI — India Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling matching reference design
st.markdown("""
<style>
    /* Global styles */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 5rem;
        max-width: 900px;
    }
    
    /* Top Header Bar */
    .top-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 1.25rem;
    }
    .brand-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
    }
    .brand-sub {
        font-size: 0.78rem;
        color: #64748b;
    }
    .grounded-badge {
        background: #f0fdf4;
        color: #166534;
        font-size: 0.75rem;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        border: 1px solid #bbf7d0;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }

    /* Section Headings with Vertical Blue Bar */
    .section-header-bar {
        border-left: 3px solid #2563eb;
        padding-left: 8px;
        font-weight: 700;
        font-size: 1rem;
        color: #0f172a;
        margin: 14px 0 6px 0;
    }

    /* Information Callout Card */
    .info-callout-card {
        background: #f0f7ff;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 12px 14px;
        margin: 14px 0 10px 0;
        color: #0369a1;
        font-size: 0.9rem;
    }

    /* Welcome Box */
    .welcome-box {
        text-align: center;
        padding: 2.5rem 1rem;
    }
    .welcome-title {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    .welcome-desc {
        font-size: 0.95rem;
        color: #64748b;
        max-width: 580px;
        margin: 0 auto 1.5rem auto;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Top Header
st.markdown("""
<div class="top-header">
    <div>
        <span class="brand-title">⚖️ LawPilot AI</span><br>
        <span class="brand-sub">India Legal Assistant</span>
    </div>
    <div>
        <span class="grounded-badge">● Grounded in Official Sources</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = f"st_{uuid.uuid4().hex[:8]}"

# Sidebar Navigation (Matching reference image)
with st.sidebar:
    st.markdown("### ⚖️ LawPilot AI")
    st.caption("India Legal Assistant")
    
    if st.button("➕ New Chat", use_container_width=True):
        reset_memory(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = f"st_{uuid.uuid4().hex[:8]}"
        st.rerun()

    st.markdown("---")
    st.markdown("**TODAY**")
    if st.button("💬 Security deposit dispute", key="hist_1", use_container_width=True):
        st.session_state.temp_prompt = "My landlord in Jaipur is refusing to return my ₹25,000 security deposit. I vacated the flat 20 days ago. What can I do?"
    if st.button("💬 Unpaid salary issue", key="hist_2", use_container_width=True):
        st.session_state.temp_prompt = "My employer in Bangalore has not paid my salary for two months. What legal steps can I take?"
    if st.button("💬 Defective product refund", key="hist_3", use_container_width=True):
        st.session_state.temp_prompt = "I purchased a defective phone online and the seller is refusing to refund or replace it."

    st.markdown("---")
    st.markdown("**Emergency Helplines:**")
    st.markdown("- 🚨 **Police Emergency:** 112\n- ⚖️ **NALSA Legal Aid:** 15100\n- 🛒 **Consumer Helpline:** 1915\n- 🚑 **Medical Emergency:** 108")
    st.markdown("---")
    st.caption("Grounded in Transfer of Property Act, Consumer Protection Act, & Payment of Wages Act.")

def process_and_reply(user_msg: str):
    st.session_state.messages.append({"role": "user", "content": user_msg})
    provider = LLMProviderFactory.get_provider()
    resp = provider.generate_response(
        message=user_msg,
        conversation_history=st.session_state.messages[:-1],
        language=LanguageEnum.ENGLISH,
        session_id=st.session_state.session_id
    )
    st.session_state.messages.append({
        "role": "assistant",
        "content": resp.content,
        "citations": resp.citations
    })

# If a history item or chip was clicked
if "temp_prompt" in st.session_state and st.session_state.temp_prompt:
    prompt_to_send = st.session_state.temp_prompt
    st.session_state.temp_prompt = None
    process_and_reply(prompt_to_send)
    st.rerun()

# Initial Welcome Screen
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-box">
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-desc">
            Describe your legal challenge in plain English, Hindi, or Hinglish.
            LawPilot AI helps you understand your rights, evaluate evidence, and generate legal notices.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 My landlord in Jaipur is refusing to return my ₹25,000 security deposit.", use_container_width=True):
            process_and_reply("My landlord in Jaipur is refusing to return my ₹25,000 security deposit. I vacated the flat 20 days ago. What can I do?")
            st.rerun()
        if st.button("💼 My company has not paid my salary for two months.", use_container_width=True):
            process_and_reply("My company has not paid my salary for two months. What can I do?")
            st.rerun()
    with c2:
        if st.button("🛒 I purchased a defective phone and the seller is refusing a refund.", use_container_width=True):
            process_and_reply("I purchased a defective phone and the seller is refusing a refund.")
            st.rerun()
        if st.button("📑 Help me understand a legal notice I received.", use_container_width=True):
            process_and_reply("Help me understand a legal notice I received from my landlord.")
            st.rerun()

# Display Messages
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Sources accordion (Collapsible like reference image)
        if msg.get("citations") and len(msg["citations"]) > 0:
            with st.expander(f"🔗 Sources ({len(msg['citations'])})", expanded=False):
                for c in msg["citations"]:
                    st.markdown(f"- **[{c.act_name} — {c.section}]({c.official_url})**: *{c.title}*")

        # In-chat actions for assistant messages
        if msg["role"] == "assistant":
            col_act1, col_act2 = st.columns([1, 1])
            with col_act1:
                if st.button("📄 Generate Document", key=f"btn_draft_{i}"):
                    process_and_reply("Draft a formal legal notice based on our conversation.")
                    st.rerun()
            with col_act2:
                if st.button("📊 Show Case Summary", key=f"btn_sum_{i}"):
                    process_and_reply("Summarize my case and tell me what information is missing.")
                    st.rerun()

# Chat Input
user_input = st.chat_input("Describe your legal problem in English, Hindi, or any language...")
if user_input:
    process_and_reply(user_input)
    st.rerun()
