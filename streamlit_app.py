"""
LawPilot AI — Streamlit Community Cloud Interface
Dual deployment frontend offering instant 1-click cloud demonstration.
"""

import streamlit as st
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.schemas import LanguageEnum, CaseCategoryEnum, DocumentTypeEnum, DocumentGenerationRequest
from app.core.llm_provider import LLMProviderFactory
from app.core.case_builder import CaseBuilder
from app.core.evidence_checklist import EvidenceChecklistManager
from app.core.document_generator import DocumentGenerator
from app.core.escalation import EscalationDetector

st.set_page_config(
    page_title="LawPilot AI — India Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Deep Navy & Subtle Teal)
st.markdown("""
<style>
    .main-title {
        color: #0F172A;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #0D9488;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .statute-box {
        background-color: #F0FDFA;
        border-left: 4px solid #0D9488;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 8px 0;
    }
    .disclaimer-box {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        color: #991B1B;
        padding: 10px;
        border-radius: 6px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-title">⚖️ LawPilot AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Navigate Legal Challenges. Know Your Rights. Take Action.</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    language = st.selectbox(
        "Preferred Language / भाषा",
        options=["English", "हिंदी (Hindi)", "Hinglish"],
        index=0
    )
    lang_enum = LanguageEnum.ENGLISH
    if language == "हिंदी (Hindi)":
        lang_enum = LanguageEnum.HINDI
    elif language == "Hinglish":
        lang_enum = LanguageEnum.HINGLISH

    state = st.selectbox(
        "Jurisdiction / State",
        options=["All India (Central Statutes)", "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh"]
    )

    st.markdown("---")
    st.markdown("**🛡️ System Mode:** Grounded Statutory Mode")
    st.markdown("**Emergency Helplines (India):**")
    st.markdown("- **NALSA Legal Aid:** 15100\n- **Consumer Grievance:** 1915\n- **National Emergency:** 112")
    
    st.markdown("---")
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        st.rerun()

# Tabs
tab_chat, tab_cases, tab_docs, tab_about = st.tabs(["💬 Legal Assistant", "📋 Case Dashboard", "📄 Document Generator", "ℹ️ About & Ethics"])

# Initialize session messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Namaste! I am **LawPilot AI**. Explain your legal situation regarding Tenant disputes, Consumer grievances, or Employment issues in English, Hindi, or Hinglish."}
    ]

# TAB 1: Chat Assistant
with tab_chat:
    col_chat, col_info = st.columns([2, 1])

    with col_chat:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Explain your legal problem (e.g., Landlord deposit return nahi kar raha ₹25000)...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Generate AI Response
            provider = LLMProviderFactory.get_provider()
            resp = provider.generate_response(
                message=user_input,
                conversation_history=st.session_state.messages,
                language=lang_enum,
                state_jurisdiction=state
            )

            with st.chat_message("assistant"):
                st.markdown(resp.content)
                if resp.citations:
                    st.markdown("**Verified Statutory Citations:**")
                    for c in resp.citations:
                        st.markdown(f"- [{c.act_name} — {c.section}]({c.official_url}): *{c.title}*")

            st.session_state.messages.append({"role": "assistant", "content": resp.content})

    with col_info:
        st.subheader("💡 Example Realistic Cases")
        if st.button("🏠 T1: ₹25,000 Deposit Not Returned"):
            st.session_state.messages.append({"role": "user", "content": "Tenant paid ₹25,000 as security deposit. Landlord refuses to return it after the tenant vacates."})
            st.rerun()
        if st.button("🛒 C1: ₹15,000 Defective Phone"):
            st.session_state.messages.append({"role": "user", "content": "Customer purchased a ₹15,000 smartphone online. It arrived defective and the seller refuses a refund."})
            st.rerun()
        if st.button("💼 E1: Unpaid Two Months Salary"):
            st.session_state.messages.append({"role": "user", "content": "Employee has not received two months of salary from employer."})
            st.rerun()

# TAB 2: Case Dashboard & Evidence
with tab_cases:
    st.subheader("Structured Case Information")
    last_user_msg = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "General tenancy inquiry")
    extracted_case = CaseBuilder.extract_case(last_user_msg, state_jurisdiction=state)

    c1, c2, c3 = st.columns(3)
    c1.metric("Category", extracted_case.category.value.upper())
    c2.metric("Disputed Amount", extracted_case.financial_amounts.get("formatted_primary", "Not specified"))
    c3.metric("Parties", f"{extracted_case.user_role} vs {extracted_case.counterparty_name}")

    st.markdown("#### Dynamic Evidence Checklist")
    evidence_items = EvidenceChecklistManager.get_checklist_for_category(extracted_case.category)
    for item in evidence_items:
        with st.expander(f"📌 {item.name} ({item.category})"):
            st.write(f"**Importance under Indian Evidence Act:** {item.legal_importance}")
            st.write(f"**Description:** {item.description}")

# TAB 3: Document Generator
with tab_docs:
    st.subheader("Legal Document Drafting & Export")
    doc_type = st.selectbox(
        "Select Document Type",
        options=[
            ("security_deposit_demand", "Security Deposit Demand Notice"),
            ("consumer_complaint_draft", "Consumer Complaint (District Commission)"),
            ("unpaid_salary_demand", "Unpaid Salary & Dues Demand Notice"),
            ("formal_legal_notice", "Formal Legal Notice Draft")
        ],
        format_func=lambda x: x[1]
    )

    doc_user = st.text_input("Your Name", "Aman Sharma")
    doc_opp = st.text_input("Opponent Name", "Ramesh Kumar (Landlord)")
    doc_amt = st.text_input("Disputed Amount", "₹25,000")
    doc_facts = st.text_area("Facts of the Dispute", "Vacated premises in clean condition. Landlord refusing to refund deposit.")

    req = DocumentGenerationRequest(
        doc_type=DocumentTypeEnum(doc_type[0]),
        user_name=doc_user,
        counterparty_name=doc_opp,
        facts=doc_facts,
        disputed_amount=doc_amt,
        demands=f"Immediate refund of {doc_amt} within 15 days."
    )

    doc_text = DocumentGenerator.generate_document_text(req)
    st.text_area("Live Generated Draft Preview", doc_text, height=300)

    col_pdf, col_docx = st.columns(2)
    with col_pdf:
        pdf_bytes = DocumentGenerator.generate_pdf(doc_text, title=f"LawPilot AI - {doc_type[1]}")
        st.download_button("📄 Download PDF Document", data=pdf_bytes, file_name=f"LawPilot_{doc_type[0]}.pdf", mime="application/pdf")
    with col_docx:
        docx_bytes = DocumentGenerator.generate_docx(doc_text, title=f"LawPilot AI - {doc_type[1]}")
        st.download_button("📑 Download Word (DOCX) Document", data=docx_bytes, file_name=f"LawPilot_{doc_type[0]}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# TAB 4: About & Ethics
with tab_about:
    st.subheader("About LawPilot AI")
    st.markdown("""
    **LawPilot AI** is an intelligent, grounded legal assistant for Indian citizens facing everyday disputes in Tenancy, Consumer Affairs, and Employment.
    
    ### Core Anti-Hallucination Principles:
    1. **Direct Statutory Retrieval:** All citations originate from verified sources (India Code, Consumer Protection Act 2019, Transfer of Property Act 1882).
    2. **Refusal to Fabricate:** Refuses to invent legal sections or guarantee court outcomes.
    3. **Emergency Escalation:** Immediately directs urgent crises (summons, physical force, threats) to NALSA (15100) and police (112).
    """)
    st.markdown('<div class="disclaimer-box"><b>Disclaimer:</b> LawPilot AI provides general legal information and assistance. It is not a substitute for advice from a qualified advocate.</div>', unsafe_allow_html=True)
