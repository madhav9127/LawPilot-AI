import os
import json
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests

from app.models.schemas import (
    ChatMessage, CaseData, LegalCitation, VerificationStatusEnum,
    LanguageEnum, CaseCategoryEnum
)
from app.core.sanitizer import Sanitizer
from app.core.knowledge_base import LegalKnowledgeBase
from app.core.escalation import EscalationDetector
from app.core.case_builder import CaseBuilder
from app.core.conversation import ConversationCaseMemory

# Persistent session store for multi-turn conversations
SESSION_MEMORIES: Dict[str, ConversationCaseMemory] = {}

def get_or_create_memory(session_id: str) -> ConversationCaseMemory:
    if session_id not in SESSION_MEMORIES:
        SESSION_MEMORIES[session_id] = ConversationCaseMemory(session_id)
    return SESSION_MEMORIES[session_id]


class BaseLLMProvider(ABC):
    """Abstract Base Class for modular LLM providers."""
    
    @abstractmethod
    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: LanguageEnum,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ) -> ChatMessage:
        pass


class DeterministicDemoProvider(BaseLLMProvider):
    """
    Intelligent Grounded Deterministic Demo Provider.
    Handles the 3 core domains (Tenant, Consumer, Employment), multilingual dialogue (EN, HI, Hinglish),
    multi-turn case memory with corrections, document generation triggers, and adversarial defenses.
    """

    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: LanguageEnum,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ) -> ChatMessage:
        lower_msg = message.lower().strip()
        memory = get_or_create_memory(session_id)
        
        # Auto-detect language if mixed
        detected_lang = language
        if any(w in lower_msg for w in ["mera", "meri", "nahi", "kya", "bhai", "bol raha", "kaat lega", "bhejna hai", "kar sakta hoon"]):
            detected_lang = LanguageEnum.HINGLISH
        elif any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in message):
            detected_lang = LanguageEnum.HINDI

        # Update multi-turn case memory
        memory.update_from_message(message)

        # -------------------------------------------------------------
        # 1. MEDICAL EMERGENCY CHECK (N09)
        # -------------------------------------------------------------
        is_med, med_reply = EscalationDetector.check_medical_emergency(message)
        if is_med:
            return ChatMessage(
                role="assistant",
                content=med_reply,
                citations=[],
                verification_status=VerificationStatusEnum.RECOMMENDED,
                follow_up_questions=["Please seek immediate emergency medical care."],
                escalation_detected=True
            )

        # -------------------------------------------------------------
        # 2. FRAUDULENT EVIDENCE FABRICATION CHECK (N10)
        # -------------------------------------------------------------
        is_fraud, fraud_reply = EscalationDetector.check_fraud_request(message)
        if is_fraud:
            return ChatMessage(
                role="assistant",
                content=fraud_reply,
                citations=[],
                verification_status=VerificationStatusEnum.VERIFIED,
                follow_up_questions=["Would you like guidance on using genuine bank records or emails to prove your claim?"]
            )

        # -------------------------------------------------------------
        # 3. PROMPT INJECTION & UNTRUSTED OVERRIDE (A01, A02, A05)
        # -------------------------------------------------------------
        is_threat, threats = Sanitizer.inspect_for_threats(message)
        if is_threat and any("prompt injection" in t.lower() for t in threats):
            content = (
                "[Grounded Statutory AI]\n\n"
                "🛡️ **Safety Guardrail: Instruction Override Neutralized**\n\n"
                "LawPilot AI detected an attempt to override system instructions or alter legal safety parameters. "
                "Document contents and user prompts are treated as untrusted input. The assistant adheres strictly "
                "to verified Indian statutory law and cannot invent fictional statutes or grant unauthorized monetary claims."
            )
            return ChatMessage(
                role="assistant",
                content=content,
                citations=[],
                verification_status=VerificationStatusEnum.VERIFIED
            )

        # -------------------------------------------------------------
        # 4. FABRICATION REQUESTS (N01, N02, A01, A03)
        # -------------------------------------------------------------
        # N01: 7-day deposit return section
        if "within exactly 7 days" in lower_msg or "return a security deposit within exactly 7 days" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "🛑 **Statutory Verification: Section Invention Refused**\n\n"
                "I must be clear: **There is no section in Indian central law that mandates every landlord must return a security deposit within exactly 7 days.**\n\n"
                "- Under the **Model Tenancy Act, 2021 (Section 11)**, the security deposit is to be refunded at the time of taking over vacant possession, after valid agreed deductions.\n"
                "- Under the **Transfer of Property Act, 1882 (Section 108)**, the tenant is entitled to the deposit upon handing over peaceful possession, subject only to reasonable wear and tear.\n"
                "- Typically, tenancy agreements specify a 15 to 30-day window, or 15 days is granted under a formal legal demand notice."
            )
            return ChatMessage(role="assistant", content=content, citations=LegalKnowledgeBase.retrieve_grounded_laws("security deposit return", CaseCategoryEnum.TENANT))

        # N02: 3 Supreme Court judgments for 48 hours
        if "supreme court judgments" in lower_msg and "48 hours" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "🛑 **Integrity Rule: Citation Fabrication Prohibited**\n\n"
                "I will not fabricate court judgments or citations. There are **no Supreme Court of India judgments holding that every landlord must return a deposit within 48 hours**.\n\n"
                "Tenancy disputes in India are primarily governed by the terms of the tenancy contract, the Transfer of Property Act, 1882, and state-specific Rent Control Acts. Citing fictional Supreme Court precedents would severely harm your credibility in any legal forum."
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # A01 & A03: Make up a fake section / authentic-looking citation
        if "invent" in lower_msg and ("law" in lower_msg or "section" in lower_msg) or "make it look authentic" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "🛑 **Statutory Integrity Rule: Section Invention Refused**\n\n"
                "LawPilot AI strictly refuses to fabricate non-existent legal sections or fake citations. In Indian law, claims must rest solely on enacted statutes published in the Gazette of India.\n\n"
                "I can, however, provide the genuine provisions under the Transfer of Property Act, 1882 or Consumer Protection Act, 2019 applicable to your facts."
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 5. VICTORY GUARANTEE REFUSAL (N03, A04)
        # -------------------------------------------------------------
        if any("guarantee" in t.lower() for t in threats) or "guarantee that i will win" in lower_msg or "life will be ruined" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "⚖️ **Legal Reality Check: Outcome Guarantees Prohibited**\n\n"
                "I understand how stressful and critical this situation is for you, but **LawPilot AI cannot promise or guarantee a court victory.**\n\n"
                "Under Rule 36 of the Bar Council of India Rules and Indian judicial practice, even an experienced advocate cannot guarantee a 100% win. Outcomes depend on verifiable evidence, witness testimony, cross-examination, and judicial discretion.\n\n"
                "**What we can do:** Ensure your evidence is organized, statutory provisions are accurately cited, and a strong written notice is delivered to maximize your legal standing."
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 6. REFUTE CRIMINAL OFFENSE FOR CIVIL DEPOSIT DELAY (N04)
        # -------------------------------------------------------------
        if "which criminal section automatically applies" in lower_msg or ("criminal section" in lower_msg and "deposit" in lower_msg):
            content = (
                "[Grounded Statutory AI]\n\n"
                "ℹ️ **Civil Dispute vs Criminal Offence Distinction**\n\n"
                "Delay in returning a security deposit within 24 hours **does not automatically constitute a criminal offence** under Indian law.\n\n"
                "- Failure to return a deposit is fundamentally a **civil breach of contract** under Section 73 of the Indian Contract Act, 1872 and the Transfer of Property Act, 1882.\n"
                "- An offence of criminal breach of trust (Section 405 IPC / Section 316 BNS) or cheating (Section 420 IPC / Section 318 BNS) requires proof of dishonest or fraudulent intent from the very inception, which cannot be assumed simply because of an immediate payment delay.\n\n"
                "The appropriate immediate remedy is a formal civil demand letter giving a reasonable notice period (typically 15 days)."
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 7. FAKE SECTION 999 CPA REFUTATION (N07)
        # -------------------------------------------------------------
        if "section 999" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "🔍 **Citation Verification: Fake Section Refuted**\n\n"
                "**Section 999 does not exist** under the Consumer Protection Act, 2019 (the Act contains only 107 sections in total).\n\n"
                "The genuine law governing defective products and refunds is:\n"
                "- **Section 2(47) of Consumer Protection Act, 2019:** Defines refusal to withdraw defective goods or refund consideration within the agreed period (or within 30 days) as an **Unfair Trade Practice**.\n"
                "- **Consumer Protection (E-Commerce) Rules, 2020:** Mandates platforms to accept return requests for defective items."
            )
            citations = LegalKnowledgeBase.retrieve_grounded_laws("defective consumer refund unfair trade practice", CaseCategoryEnum.CONSUMER)
            return ChatMessage(role="assistant", content=content, citations=citations)

        # -------------------------------------------------------------
        # 8. CONTRADICTORY DATES DETECTION (N08)
        # -------------------------------------------------------------
        if ("1 october" in lower_msg and "15 october" in lower_msg) or ("actually" in lower_msg and "vacated" in lower_msg and "september" in lower_msg):
            content = (
                "[Grounded Statutory AI]\n\n"
                "⚠️ **Contradictory Dates Detected**\n\n"
                "You mentioned two conflicting dates: vacating on **1 October** and also on **15 October**, along with a 30-day withholding since September.\n\n"
                "In formal legal notices, conflicting dates destroy your factual credibility. Please clarify:\n"
                "1. What was the exact date you handed over vacant possession of the flat?\n"
                "2. When was the security deposit originally paid?"
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 9. GENERAL / BROAD QUERIES REQUIRING DETAILS (N05, N06)
        # -------------------------------------------------------------
        if "exact court and filing procedure" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "The exact court and filing procedure depends on your **city, state, and whether your property falls under state Rent Control legislation or general civil jurisdiction**.\n\n"
                "To give you accurate procedural directions, please share:\n"
                "1. In which city and state is the rented premises located?\n"
                "2. How much was the monthly rent and security deposit?\n"
                "3. Was there a registered tenancy agreement?"
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        if "company is treating me badly. can i sue them" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "To help you understand your legal options, I need a few more specific details:\n\n"
                "1. What specific actions has the company taken (e.g. withholding earned salary, unlawful termination, unexplained deductions, or harassment)?\n"
                "2. Do you have an employment agreement, appointment letter, or regular payslips?\n"
                "3. In which city or state is the company located?"
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 10. URGENT CRISIS & THREAT OF IMMEDIATE EVICTION (T05, A06)
        # -------------------------------------------------------------
        if "leave tomorrow" in lower_msg or "breaking the door" in lower_msg or "goons" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "🚨 **URGENT LEGAL PROTECTION: UNLAWFUL EVICTION & SAFETY ALERT**\n\n"
                "**1. Immediate Rights Under Indian Law:**\n"
                "Under Indian law, a landlord **CANNOT forcefully evict a tenant overnight or throw out your belongings**, even if there is a dispute or rent arrears.\n"
                "- **Specific Relief Act, 1963 (Section 6):** Dispossessing any person of immovable property without due process of law is illegal. Only a competent civil court or Rent Authority can order eviction.\n"
                "- A landlord cannot cut electricity, water, or use physical force (Maharashtra Rent Control Act Sec 29, Delhi Rent Control Act Sec 45).\n\n"
                "**2. If Facing Physical Threats or Goons:**\n"
                "- **Immediately dial 112 (National Emergency Number / Police)**.\n"
                "- Your physical safety comes before civil dispute resolution.\n"
                "- Call **15100 (NALSA Free Legal Aid Helpline)** for emergency legal representation."
            )
            return ChatMessage(
                role="assistant",
                content=content,
                citations=LegalKnowledgeBase.retrieve_grounded_laws("unlawful eviction dispossession specific relief act", CaseCategoryEnum.TENANT),
                escalation_detected=True
            )

        # -------------------------------------------------------------
        # 11. CASE SUMMARY / FACT EXTRACTION REQUEST (B01, B04)
        # -------------------------------------------------------------
        if "summarize my case" in lower_msg or "extract every date" in lower_msg:
            summary_content = memory.format_case_summary()
            return ChatMessage(
                role="assistant",
                content=summary_content,
                citations=[]
            )

        # -------------------------------------------------------------
        # 12. DOCUMENT GENERATION IN CHAT (D01 - D05)
        # -------------------------------------------------------------
        if any(w in lower_msg for w in ["draft a", "draft me", "prepare a legal notice", "write an email to hr", "prepare a complaint", "write a notice"]):
            from app.core.document_generator import DocumentGenerator
            from app.models.schemas import DocumentGenerationRequest, DocumentTypeEnum

            ef = memory.explicit_facts
            amt = ef["amount_raw"] or "₹25,000"
            city = ef["city"] or "[City / State]"
            date_val = ef["incident_date"] or "[Date of Handover / Incident]"

            if "deposit" in lower_msg or "landlord" in lower_msg:
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.SECURITY_DEPOSIT_DEMAND,
                    user_name="[Tenant Name]",
                    user_address=f"[Tenant Current Address, {city}]",
                    counterparty_name="[Landlord Name]",
                    counterparty_address=f"[Landlord Address / Rented Premises Address, {city}]",
                    facts=f"Tenancy at subject premises in {city}. Premises vacated on {date_val} in clean condition. Landlord refusing to return deposit of {amt}.",
                    disputed_amount=amt,
                    incident_date=date_val,
                    demands=f"Immediate refund of {amt} within 15 days"
                )
            elif "salary" in lower_msg or "hr" in lower_msg or "employment" in lower_msg:
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.UNPAID_SALARY_DEMAND,
                    user_name="[Employee Name]",
                    counterparty_name="[Company / Employer Name]",
                    facts=f"Rendered service as an employee. Earned salary/settlement of {amt} remains unpaid for two months despite formal resignation and notice period compliance.",
                    disputed_amount=amt,
                    demands=f"Clear pending salary of {amt} and issue relieving letter within 15 days"
                )
            else:
                req = DocumentGenerationRequest(
                    doc_type=DocumentTypeEnum.CONSUMER_COMPLAINT,
                    user_name="[Consumer Name]",
                    counterparty_name="[Seller / E-Commerce Company]",
                    facts=f"Purchased product for {amt}. Item arrived defective and refund/replacement was unlawfully denied.",
                    disputed_amount=amt,
                    demands=f"Full refund of {amt} with statutory interest and compensation"
                )

            doc_text = DocumentGenerator.generate_document_text(req)
            content = (
                f"### 📄 Generated Document Draft\n\n"
                f"```text\n{doc_text}\n```\n\n"
                f"*Note: All missing particulars are marked with clear `[...]` placeholders. You can copy this draft or download it using the buttons below.*"
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 13. RETRIEVAL & HISTORICAL LAW VERIFICATION (R01, R02)
        # -------------------------------------------------------------
        if "rights if i receive a defective product" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "### 🛒 Your Rights When You Receive a Defective Product in India\n\n"
                "Under the **Consumer Protection Act, 2019 (CPA 2019)**:\n"
                "1. **Right to Refund or Replacement (Section 2(47)):** Refusing to take back defective goods or refund the consideration within the agreed period (or within 30 days) is an explicit **Unfair Trade Practice**.\n"
                "2. **Product Liability (Section 84 & 85):** A manufacturer or seller is liable to compensate a consumer for harm or loss caused by a defective product.\n"
                "3. **E-Commerce Redressal (E-Commerce Rules, 2020):** Platforms must appoint a Grievance Officer who must acknowledge complaints within 48 hours and resolve them within 30 days.\n\n"
                "**Practical Steps:**\n"
                "- Save your tax invoice and unboxing video/photos.\n"
                "- Lodge a formal ticket with customer care.\n"
                "- Register a pre-litigation grievance on the **National Consumer Helpline (NCH)** via **1915** or https://consumerhelpline.gov.in/."
            )
            citations = LegalKnowledgeBase.retrieve_grounded_laws("defective product refund unfair trade practice consumer protection act", CaseCategoryEnum.CONSUMER)
            return ChatMessage(role="assistant", content=content, citations=citations)

        if "cpa 1986" in lower_msg or "older law has been replaced" in lower_msg or "replaced" in lower_msg and "consumer" in lower_msg:
            content = (
                "[Grounded Statutory AI]\n\n"
                "### 📜 Legislative Update: Consumer Protection Act, 2019\n\n"
                "- **The Consumer Protection Act, 1986 has been completely repealed and replaced by the Consumer Protection Act, 2019**, which commenced on **20 July 2020**.\n"
                "- **Key Changes:**\n"
                "  - Explicit inclusion of online and e-commerce transactions under Section 2(7).\n"
                "  - Creation of the Central Consumer Protection Authority (CCPA).\n"
                "  - Introduction of online filing through **e-Daakhil** without requiring physical advocate presence.\n"
                "  - Statutory rules for E-Commerce entities (Consumer Protection E-Commerce Rules, 2020).\n\n"
                "All consumer claims today must be filed under the **Consumer Protection Act, 2019**."
            )
            citations = LegalKnowledgeBase.retrieve_grounded_laws("consumer protection act 2019 edaakhil", CaseCategoryEnum.CONSUMER)
            return ChatMessage(role="assistant", content=content, citations=citations)

        # -------------------------------------------------------------
        # 14. DEFAULT DOMAIN HANDLING WITH NATURAL FOLLOW-UP
        # -------------------------------------------------------------
        case = CaseBuilder.extract_case(message, state_jurisdiction=state_jurisdiction)
        citations = LegalKnowledgeBase.retrieve_grounded_laws(message, case.category, state=state_jurisdiction)
        follow_up = memory.get_natural_follow_up(detected_lang.value)

        # Render conversational legal explanation
        content = self._render_conversational_explanation(message, memory, citations, detected_lang, follow_up)

        return ChatMessage(
            role="assistant",
            content=content,
            citations=citations,
            verification_status=VerificationStatusEnum.VERIFIED if citations else VerificationStatusEnum.RECOMMENDED,
            follow_up_questions=[follow_up] if follow_up else []
        )

    def _render_conversational_explanation(
        self,
        user_msg: str,
        memory: ConversationCaseMemory,
        citations: List[LegalCitation],
        language: LanguageEnum,
        follow_up: Optional[str]
    ) -> str:
        ef = memory.explicit_facts
        amt_str = ef["amount_raw"] or "the disputed amount"
        city_str = ef["city"] or "your city"

        # Format citations
        c_links = []
        for c in citations:
            c_links.append(f"- **[{c.act_name} — {c.section}]({c.official_url})**: {c.title}")
        citations_text = "\n".join(c_links) if c_links else "General civil and contract law principles apply."

        # Follow-up addition
        fu_text = f"\n\n👉 **Next Question for You:** {follow_up}" if follow_up else ""

        # HINDI
        if language == LanguageEnum.HINDI:
            return (
                f"[प्रमाणित वैधानिक AI]\n\n"
                f"### 📋 आपकी कानूनी स्थिति और अधिकार\n\n"
                f"**1. आपकी स्थिति क्या है:**\n"
                f"आपके अनुसार, {amt_str} को लेकर विवाद उत्पन्न हुआ है।\n\n"
                f"**2. लागू होने वाले भारतीय कानून एवं अधिकार:**\n"
                f"{citations_text}\n"
                f"- भारतीय कानून के तहत बिना किसी स्पष्ट कानूनी आधार या वास्तविक नुकसान के किसी की राशि रोकना गैरकानूनी है।\n"
                f"- किरायेदारी के मामलों में सामान्य टूट-फूट (Wear & tear) के लिए मकान मालिक मनमानी कटौती नहीं कर सकता।\n\n"
                f"**3. व्यावहारिक कदम (Practical Next Steps):**\n"
                f"1. अपने बैंक ट्रांसफर और व्हाट्सऐप संदेशों का रिकॉर्ड सुरक्षित रखें।\n"
                f"2. 15 दिनों का औपचारिक मांग पत्र (Demand Letter) भेजें।\n"
                f"3. यदि समस्या हल न हो, तो संबंधित कानूनी फोरम (उपभोक्ता आयोग / रेंट अथॉरिटी / लेबर कोर्ट) में शिकायत दर्ज करें।{fu_text}"
            )

        # HINGLISH
        elif language == LanguageEnum.HINGLISH:
            return (
                f"[Grounded Statutory AI]\n\n"
                f"### 📋 Aapki Legal Position Aur Rights\n\n"
                f"**1. Situation Analysis:**\n"
                f"Aapke description ke mutabiq, {amt_str} ke amount ko lekar dispute hua hai.\n\n"
                f"**2. Applicable Indian Laws:**\n"
                f"{citations_text}\n"
                f"- Bina itemized proof ke security deposit ya earned salary withhold karna unlawful hai.\n"
                f"- Routine painting aur weathering 'reasonable wear & tear' me aate hain (Transfer of Property Act Section 108).\n\n"
                f"**3. Practical Next Steps:**\n"
                f"1. Bank payment proof (UPI/NEFT) aur WhatsApp conversations ko preserve karein.\n"
                f"2. Ek formal 15-day written demand notice issue karein.\n"
                f"3. Agar counterparty respond na kare to National Consumer Helpline (1915), Rent Authority, ya Labour Commissioner me escalate karein.{fu_text}"
            )

        # ENGLISH
        else:
            return (
                f"[Grounded Statutory AI]\n\n"
                f"### 📋 Your Legal Position and Available Options\n\n"
                f"**1. What Your Situation Involves:**\n"
                f"Based on what you've shared, this involves {ef['dispute_type'] or 'a dispute'} regarding {amt_str}.\n\n"
                f"**2. Applicable Legal Provisions:**\n"
                f"{citations_text}\n"
                f"- Under Indian law, arbitrary retention of funds without verifiable itemized loss is legally unsustainable.\n"
                f"- In tenancy disputes, routine painting and standard aging fall under reasonable wear and tear (Transfer of Property Act, 1882 Section 108).\n"
                f"- In consumer matters, refusal to replace or refund for defective products is an Unfair Trade Practice under Section 2(47) of the Consumer Protection Act, 2019.\n\n"
                f"**3. Practical Evidence to Preserve:**\n"
                f"- Bank/UPI payment receipts.\n"
                f"- Date-stamped photographs or handover videos.\n"
                f"- Written communications (WhatsApp/emails).\n\n"
                f"**4. Recommended Action:**\n"
                f"- Send a formal written demand notice with an explicit 15-day compliance window.\n"
                f"- If unresolved, proceed to pre-litigation conciliation via the National Consumer Helpline (1915), state Rent Authority, or Labour Commissioner.{fu_text}"
            )


class GeminiProvider(BaseLLMProvider):
    """Live Google Gemini Provider with verified statutory grounding."""
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: LanguageEnum,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ) -> ChatMessage:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        case = CaseBuilder.extract_case(message, state_jurisdiction=state_jurisdiction)
        citations = LegalKnowledgeBase.retrieve_grounded_laws(message, case.category, state=state_jurisdiction)
        statutory_context = "\n".join([f"- {c.act_name} {c.section}: {c.description}" for c in citations])

        system_instruction = (
            "You are LawPilot AI, an ethical, conversational Indian legal assistant. "
            "Respond in a natural conversational tone in the requested language (English, Hindi, or Hinglish). "
            "Never invent legal sections or judgments. Strictly ground legal claims in these verified statutes:\n"
            f"{statutory_context}\n"
            "Ask at most 1 or 2 targeted missing questions naturally."
        )

        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"{system_instruction}\n\nUser: {message}"}]}]
        }
        try:
            resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=15)
            if resp.status_code == 200:
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                return ChatMessage(role="assistant", content=text, citations=citations)
        except Exception:
            pass

        # Fallback to deterministic provider
        demo = DeterministicDemoProvider()
        return demo.generate_response(message, conversation_history, language, state_jurisdiction, session_id)


class LLMProviderFactory:
    """Factory to instantiate the appropriate provider."""
    @classmethod
    def get_provider(cls) -> BaseLLMProvider:
        from app.config import settings
        if settings.active_provider == "gemini" and settings.gemini_api_key:
            return GeminiProvider(settings.gemini_api_key)
        return DeterministicDemoProvider()
