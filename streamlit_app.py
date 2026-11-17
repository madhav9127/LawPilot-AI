"""
LawPilot AI — Simple, Single-Page AI Legal Chatbot for India
Clean, ChatGPT-like interface built with Streamlit.
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
    page_title="LawPilot AI — Legal Assistant for India",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimal CSS styling
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 800px;
    }
    .header-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .brand-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
    }
    .brand-tagline {
        font-size: 0.8rem;
        color: #64748b;
    }
    .grounded-badge {
        background: #f0fdf4;
        color: #166534;
        font-size: 0.75rem;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        border: 1px solid #bbf7d0;
        font-weight: 500;
    }
    .welcome-box {
        text-align: center;
        padding: 3rem 1rem;
    }
    .welcome-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    .welcome-desc {
        font-size: 1rem;
        color: #64748b;
        max-width: 550px;
        margin: 0 auto 2rem auto;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div class="header-bar">
    <div>
        <span class="brand-title">⚖️ LawPilot AI</span><br>
        <span class="brand-tagline">Your AI assistant for everyday legal problems in India</span>
    </div>
    <div>
        <span class="grounded-badge">🛡️ Grounded in Official Statutes</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize Session Messages and Unique Session ID
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = f"st_{uuid.uuid4().hex[:8]}"

# Helper to process user message and generate assistant response
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

# Sidebar for simple options & reset
with st.sidebar:
    st.markdown("### ⚙️ Session Options")
    if st.button("🔄 Start New Conversation", use_container_width=True):
        reset_memory(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = f"st_{uuid.uuid4().hex[:8]}"
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
    st.markdown("**Core Supported Domains:**")
    st.markdown("- 🏠 Tenant & Landlord Disputes\n- 🛒 Consumer Protection\n- 💼 Employment Issues")
    st.markdown("---")
    st.markdown("**Emergency Helplines:**")
    st.markdown("- **Police Emergency:** 112\n- **NALSA Free Legal Aid:** 15100\n- **Consumer Helpline:** 1915\n- **Medical Emergency:** 108")

# Initial Welcome Screen (Disappears once chat has messages)
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-box">
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-desc">
            Describe your legal challenge in plain English, Hindi, or Hinglish.
            LawPilot AI helps you understand your rights, organize your evidence, and generate legal notices.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 My landlord is refusing to return my security deposit.", use_container_width=True):
            process_and_reply("My landlord is refusing to return my security deposit.")
            st.rerun()
        if st.button("💼 My company has not paid my salary for two months.", use_container_width=True):
            process_and_reply("My company has not paid my salary for two months.")
            st.rerun()
    with c2:
        if st.button("🛒 I purchased a defective product and the seller is refusing a refund.", use_container_width=True):
            process_and_reply("I purchased a defective product and the seller is refusing a refund.")
            st.rerun()
        if st.button("📑 Help me understand a legal notice I received.", use_container_width=True):
            process_and_reply("Help me understand a legal notice I received.")
            st.rerun()

# Display Chat Messages
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Display citations if present
        if msg.get("citations"):
            st.markdown("---")
            st.markdown("**Verified Statutory Citations:**")
            for c in msg["citations"]:
                st.markdown(f"- [{c.act_name} — {c.section}]({c.official_url}): *{c.title}*")

        # In-chat actions for assistant messages
        if msg["role"] == "assistant":
            col_act1, col_act2 = st.columns([1, 1])
            with col_act1:
                if st.button("📄 Draft Legal Notice", key=f"btn_draft_{i}"):
                    process_and_reply("Draft a formal legal notice based on our conversation.")
                    st.rerun()
            with col_act2:
                if st.button("📊 Show Case Summary", key=f"btn_sum_{i}"):
                    process_and_reply("Summarize my case and tell me what information is missing.")
                    st.rerun()

# Chat Input
user_input = st.chat_input("Describe your legal issue in English, Hindi, or Hinglish...")
if user_input:
    process_and_reply(user_input)
    st.rerun()
