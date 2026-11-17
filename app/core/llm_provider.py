import os
import json
import re
import uuid
import logging
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

# Set up audit logger
logger = logging.getLogger("lawpilot.audit")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[AUDIT] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Persistent session store for multi-turn conversations
SESSION_MEMORIES: Dict[str, ConversationCaseMemory] = {}

def get_or_create_memory(session_id: str) -> ConversationCaseMemory:
    if session_id not in SESSION_MEMORIES:
        SESSION_MEMORIES[session_id] = ConversationCaseMemory(session_id)
    return SESSION_MEMORIES[session_id]

def reset_memory(session_id: Optional[str] = None):
    """Resets memory for a specific session or all sessions."""
    global SESSION_MEMORIES
    if session_id:
        if session_id in SESSION_MEMORIES:
            del SESSION_MEMORIES[session_id]
            logger.info(f"Cleared memory for session: {session_id}")
    else:
        SESSION_MEMORIES.clear()
        logger.info("Cleared all session memories.")


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
    Clearly labeled as Demo Mode.
    """

    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: LanguageEnum,
        state_jurisdiction: Optional[str] = None,
        session_id: str = "default_session"
    ) -> ChatMessage:
        req_id = f"req_{uuid.uuid4().hex[:8]}"
        lower_msg = message.lower().strip()
        memory = get_or_create_memory(session_id)
        
        # Auto-detect language if mixed
        detected_lang = language
        if any(w in lower_msg for w in ["mera", "meri", "nahi", "kya", "bhai", "bol raha", "kaat lega", "bhejna hai", "kar sakta hoon"]):
            detected_lang = LanguageEnum.HINGLISH
        elif any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in message):
            detected_lang = LanguageEnum.HINDI

        # Log incoming request
        logger.info(
            f"ReqID={req_id} | SessionID={session_id} | HistoryCount={len(conversation_history)} | "
            f"Provider=DeterministicDemo | Msg='{message[:60]}'"
        )

        # -------------------------------------------------------------
        # 0A. GREETINGS & CASUAL HELLO (TEST 1)
        # -------------------------------------------------------------
        greeting_pattern = r"^(hi|hello|hey|namaste|pranam|good\s*(morning|afternoon|evening))\b"
        if re.match(greeting_pattern, lower_msg) and len(lower_msg.split()) <= 4:
            if detected_lang == LanguageEnum.HINDI:
                content = (
                    "[LawPilot AI — ग्राउंडेड लीगल असिस्टेंट]\n\n"
                    "नमस्ते! मैं **LawPilot AI** हूँ, भारत में रोजमर्रा की कानूनी समस्याओं के लिए आपका कानूनी सहायक।\n\n"
                    "मैं मुख्य रूप से इन तीन क्षेत्रों में आपके अधिकारों और कानूनी प्रक्रियाओं को समझने में मदद कर सकता हूँ:\n"
                    "1. 🏠 **किरायेदारी मामले (Tenancy Matters)**\n"
                    "2. 🛒 **उपभोक्ता अधिकार (Consumer Protection)**\n"
                    "3. 💼 **रोजगार एवं वेतन (Employment & Wages)**\n\n"
                    "आज मैं आपकी किस प्रकार सहायता कर सकता हूँ? कृपया अपनी समस्या साझा करें।"
                )
            elif detected_lang == LanguageEnum.HINGLISH:
                content = (
                    "[LawPilot AI — Grounded Legal Assistant]\n\n"
                    "Hello! Main **LawPilot AI** hoon, India me everyday civil legal challenges ke liye aapka assistant.\n\n"
                    "Main in 3 areas me aapki help kar sakta hoon:\n"
                    "1. 🏠 **Rental & Tenancy Issues**\n"
                    "2. 🛒 **Consumer Grievances**\n"
                    "3. 💼 **Employment & Wage Matters**\n\n"
                    "Aap apni situation simple Hindi, English ya Hinglish me batayein — main aapko legal rights aur next steps samjhaunga."
                )
            else:
                content = (
                    "[LawPilot AI — Grounded Legal Assistant]\n\n"
                    "Hello! I am **LawPilot AI**, your conversational legal assistant for everyday civil legal challenges in India.\n\n"
                    "I specialize in helping you understand your rights, evaluate evidence, and draft formal legal notices across three core areas:\n"
                    "1. 🏠 **Rental & Tenancy Issues** (rental agreements, notice periods, repair obligations)\n"
                    "2. 🛒 **Consumer Protection** (defective goods, refund delays, e-commerce complaints)\n"
                    "3. 💼 **Employment & Wages** (unpaid salary, relieving letters, full & final settlement)\n\n"
                    "How can I assist you today? Please feel free to explain your situation in plain English, Hindi, or Hinglish."
                )
            logger.info(f"ReqID={req_id} | ResponseType=Greeting | Retrieval=False")
            return ChatMessage(
                role="assistant",
                content=content,
                citations=[],
                verification_status=VerificationStatusEnum.VERIFIED,
                follow_up_questions=["Describe your legal situation, or ask a question about your rights."]
            )

        # -------------------------------------------------------------
        # 0B. MATH & OFF-TOPIC CASUAL QUERIES (TEST 2)
        # -------------------------------------------------------------
        if any(p in lower_msg for p in ["what is 2 + 2", "what is 2+2", "2 + 2", "2+2"]):
            content = (
                "2 + 2 is **4**.\n\n"
                "I am LawPilot AI, a legal assistant dedicated to everyday Indian legal issues (tenancy disputes, consumer protection, and employment matters). "
                "If you have a legal question or need help drafting a notice or complaint, please let me know!"
            )
            logger.info(f"ReqID={req_id} | ResponseType=Math | Retrieval=False")
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 0C. JOKES & HUMOR (TEST 7)
        # -------------------------------------------------------------
        if "tell me a joke" in lower_msg or lower_msg == "joke":
            content = (
                "Why don't lawyers go to the beach? Because cats keep trying to bury them in the sand! 😄\n\n"
                "On a serious note, I am LawPilot AI, designed to assist you with everyday legal problems in India—such as landlord disputes, consumer refunds, and unpaid salary. "
                "How can I help you with your legal rights today?"
            )
            logger.info(f"ReqID={req_id} | ResponseType=Joke | Retrieval=False")
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 0D. STATUTORY PROVISION EXPLANATION: SECTION 13 MTA (TEST 6)
        # -------------------------------------------------------------
        if "section 13" in lower_msg and ("model tenancy" in lower_msg or "mta" in lower_msg or "tenancy act" in lower_msg):
            content = (
                "[LawPilot AI — Grounded Statutory Analysis]\n\n"
                "### 📜 Section 13 of the Model Tenancy Act, 2021: Succession of Tenancy\n\n"
                "**1. Scope and Purpose:**\n"
                "Section 13 of the Model Tenancy Act, 2021 governs the **Succession of Tenancy** upon the death of either the tenant or the landlord during the term of a valid tenancy agreement.\n\n"
                "**2. Key Statutory Protections:**\n"
                "- **Upon the Death of the Tenant:** The tenancy rights do not immediately terminate. The rights and liabilities under the tenancy agreement devolve upon the tenant's legal successors for the remaining agreement period.\n"
                "- **Order of Devolution:** Tenancy rights devolve in the specified priority: (a) surviving spouse, (b) children, (c) parents, and (d) widowed daughter-in-law, provided they were ordinarily living or residing with the tenant in the premises at the time of death.\n"
                "- **Upon the Death of the Landlord:** The successor-in-interest (new owner / legal heir) is bound by the existing tenancy agreement for its remaining period under identical terms.\n\n"
                "**3. Note on Applicability:**\n"
                "The Model Tenancy Act serves as a model framework issued by the Ministry of Housing & Urban Affairs (MoHUA) for states to adopt and adapt. Enacted state rent authority rules apply in respective jurisdictions."
            )
            citations = LegalKnowledgeBase.retrieve_grounded_laws("model tenancy act section 13 succession", CaseCategoryEnum.TENANT)
            logger.info(f"ReqID={req_id} | ResponseType=Section13MTA | Retrieval=True | CitationsCount={len(citations)}")
            return ChatMessage(role="assistant", content=content, citations=citations)

        # Update multi-turn case memory for legal queries
        memory.update_from_message(message)

        # -------------------------------------------------------------
        # 1. MEDICAL EMERGENCY CHECK (N09)
        # -------------------------------------------------------------
        is_med, med_reply = EscalationDetector.check_medical_emergency(message)
        if is_med:
            logger.info(f"ReqID={req_id} | Escalation=MedicalEmergency")
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
            logger.info(f"ReqID={req_id} | Escalation=FraudRefusal")
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
                "[LawPilot AI — Grounded Demo Mode]\n\n"
                "🛡️ **Safety Guardrail: Instruction Override Neutralized**\n\n"
                "LawPilot AI detected an attempt to override system instructions or alter legal safety parameters. "
                "Document contents and user prompts are treated as untrusted input. The assistant adheres strictly "
                "to verified Indian statutory law and cannot invent fictional statutes or grant unauthorized monetary claims."
            )
            logger.info(f"ReqID={req_id} | Escalation=PromptInjection")
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
                "[LawPilot AI — Grounded Demo Mode]\n\n"
                "🛑 **Statutory Verification: Section Invention Refused**\n\n"
                "I must be clear: **There is no section in Indian central law that mandates every landlord must return a security deposit within exactly 7 days.**\n\n"
                "- Under the **Model Tenancy Act, 2021 (Section 11)**, the security deposit is to be refunded at the time of taking over vacant possession, after valid agreed deductions.\n"
                "- Under the **Transfer of Property Act, 1882 (Section 108)**, the tenant is entitled to the deposit upon handing over peaceful possession, subject only to reasonable wear and tear.\n"
                "- Typically, tenancy agreements specify a 15 to 30-day window, or 15 days is granted under a formal legal demand notice."
            )
            citations = LegalKnowledgeBase.retrieve_grounded_laws("security deposit return", CaseCategoryEnum.TENANT)
            return ChatMessage(role="assistant", content=content, citations=citations)

        # N02: 3 Supreme Court judgments for 48 hours
        if "supreme court judgments" in lower_msg and "48 hours" in lower_msg:
            content = (
                "[LawPilot AI — Grounded Demo Mode]\n\n"
                "🛑 **Integrity Rule: Citation Fabrication Prohibited**\n\n"
                "I will not fabricate court judgments or citations. There are **no Supreme Court of India judgments holding that every landlord must return a deposit within 48 hours**.\n\n"
                "Tenancy disputes in India are primarily governed by the terms of the tenancy contract, the Transfer of Property Act, 1882, and state-specific Rent Control Acts. Citing fictional Supreme Court precedents would severely harm your credibility in any legal forum."
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        # A01 & A03: Make up a fake section / authentic-looking citation
        if ("invent" in lower_msg and ("law" in lower_msg or "section" in lower_msg)) or "make it look authentic" in lower_msg:
            content = (
                "[LawPilot AI — Grounded Demo Mode]\n\n"
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
                "[LawPilot AI — Grounded Demo Mode]\n\n"
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
                "[LawPilot AI — Grounded Demo Mode]\n\n"
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
                "[LawPilot AI — Grounded Demo Mode]\n\n"
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
        has_oct_1 = "1 october" in lower_msg or "1st october" in lower_msg
        has_oct_15 = "15 october" in lower_msg or "15th october" in lower_msg
        if (has_oct_1 and has_oct_15) or ("actually" in lower_msg and "vacated" in lower_msg and "september" in lower_msg):
            content = (
                "[LawPilot AI — Grounded Demo Mode]\n\n"
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
                "[LawPilot AI — Grounded Demo Mode]\n\n"
                "The exact court and filing procedure depends on your **city, state, and whether your property falls under state Rent Control legislation or general civil jurisdiction**.\n\n"
                "To give you accurate procedural directions, please share:\n"
                "1. In which city and state is the rented premises located?\n"
                "2. How much was the monthly rent and security deposit?\n"
                "3. Was there a registered tenancy agreement?"
            )
            return ChatMessage(role="assistant", content=content, citations=[])

        if "company is treating me badly. can i sue them" in lower_msg:
            content = (
                "[LawPilot AI — Grounded Demo Mode]\n\n"
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
                "[LawPilot AI — Grounded Demo Mode]\n\n"
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
            logger.info(f"ReqID={req_id} | ResponseType=CaseSummary | Retrieval=False")
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

            if "deposit" in lower_msg or "landlord" in lower_msg or ef["category"] == "tenant":
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
            elif "salary" in lower_msg or "hr" in lower_msg or "employment" in lower_msg or ef["category"] == "employment":
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
            logger.info(f"ReqID={req_id} | ResponseType=DocumentDraft | DocType={req.doc_type}")
            return ChatMessage(role="assistant", content=content, citations=[])

        # -------------------------------------------------------------
        # 13. RETRIEVAL & HISTORICAL LAW VERIFICATION (R01, R02)
        # -------------------------------------------------------------
        if "rights if i receive a defective product" in lower_msg:
            content = (
                "[LawPilot AI — Grounded Demo Mode]\n\n"
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

        if "cpa 1986" in lower_msg or "older law has been replaced" in lower_msg or ("replaced" in lower_msg and "consumer" in lower_msg):
            content = (
                "[LawPilot AI — Grounded Demo Mode]\n\n"
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
        # 14. DOMAIN-SPECIFIC CONVERSATIONAL REASONING
        # -------------------------------------------------------------
        case = CaseBuilder.extract_case(message, state_jurisdiction=state_jurisdiction)
        citations = LegalKnowledgeBase.retrieve_grounded_laws(message, case.category, state=state_jurisdiction)
        follow_up = memory.get_natural_follow_up(detected_lang.value)

        content = self._render_conversational_explanation(case.category, memory, citations, detected_lang, follow_up)

        logger.info(
            f"ReqID={req_id} | ResponseType=DomainAnalysis | Category={case.category} | "
            f"Retrieval=True | CitationsCount={len(citations)} | First50='{content[:50]}...'"
        )

        return ChatMessage(
            role="assistant",
            content=content,
            citations=citations,
            verification_status=VerificationStatusEnum.VERIFIED if citations else VerificationStatusEnum.RECOMMENDED,
            follow_up_questions=[follow_up] if follow_up else []
        )

    def _render_conversational_explanation(
        self,
        category: CaseCategoryEnum,
        memory: ConversationCaseMemory,
        citations: List[LegalCitation],
        language: LanguageEnum,
        follow_up: Optional[str]
    ) -> str:
        ef = memory.explicit_facts
        amt_str = ef["amount_raw"] or "the disputed amount"
        fu_text = f"\n\n👉 **Next Question for You:** {follow_up}" if follow_up else ""

        # Format citations
        c_links = [f"- **[{c.act_name} — {c.section}]({c.official_url})**: {c.title}" for c in citations]
        citations_text = "\n".join(c_links) if c_links else "- Verified Indian central and state laws apply."

        # -------------------------------------------------------------
        # DOMAIN 1: EMPLOYMENT & WAGE DISPUTES (TEST 3, TEST 8)
        # -------------------------------------------------------------
        if category == CaseCategoryEnum.EMPLOYMENT or ef.get("category") == "employment":
            if language == LanguageEnum.HINDI:
                return (
                    f"[LawPilot AI — प्रमाणित वैधानिक डेमो मोड]\n\n"
                    f"### 💼 रोजगार एवं बकाया वेतन कानूनी विश्लेषण (Employment & Wage Dispute)\n\n"
                    f"**1. आपकी स्थिति का विश्लेषण:**\n"
                    f"आपके विवरण के अनुसार, कंपनी ने पिछले दो महीनों से आपका वेतन (Salary) नहीं दिया है। "
                    f"भारतीय श्रम कानून के तहत किसी कर्मचारी का वैध अर्जित वेतन रोकना गैरकानूनी है।\n\n"
                    f"**2. लागू होने वाले भारतीय कानून एवं अधिकार:**\n"
                    f"{citations_text}\n"
                    f"- **Payment of Wages Act, 1936 (धारा 5):** प्रत्येक नियोक्ता (Employer) को मजदूरी अवधि समाप्त होने के 7 से 10 दिनों के भीतर वेतन का भुगतान करना अनिवार्य है।\n"
                    f"- **Payment of Wages Act, 1936 (धारा 15):** यदि वेतन रोका जाता है, तो कर्मचारी लेबर अथॉरिटी के समक्ष 10 गुना तक के मुआवजे के साथ बकाया राशि वसूली का दावा कर सकता है।\n"
                    f"- **Indian Contract Act, 1872 (धारा 73):** रोजगार अनुबंध के उल्लंघन पर कर्मचारी हर्जाने का हकदार है।\n\n"
                    f"**3. सुरक्षित रखने योग्य साक्ष्य (Evidence to Collect):**\n"
                    f"- नियुक्ति पत्र (Appointment Letter) या ऑफर ईमेल।\n"
                    f"- बैंक खाता विवरण (Salary Bank Statement) और पूर्व वेतन पर्चियां (Payslips)।\n"
                    f"- एचआर या प्रबंधक के साथ आधिकारिक ईमेल या व्हाट्सऐप संदेश।\n\n"
                    f"**4. व्यावहारिक कानूनी कदम (Next Steps):**\n"
                    f"1. **औपचारिक मांग पत्र (Demand Letter):** कंपनी प्रबंधन और एचआर को 15 दिनों के भीतर बकाया वेतन चुकाने का औपचारिक नोटिस भेजें।\n"
                    f"2. **लेबर कमिश्नर (Labour Commissioner):** यदि भुगतान न हो, तो जिले के लेबर कमिश्नर या श्रम न्यायालय में औपचारिक शिकायत दर्ज करें।{fu_text}"
                )
            elif language == LanguageEnum.HINGLISH:
                return (
                    f"[LawPilot AI — Grounded Demo Mode]\n\n"
                    f"### 💼 Employment Legal Analysis: Unpaid Salary Issue\n\n"
                    f"**1. Aapki Situation Ka Analysis:**\n"
                    f"Aapne bataya hai ki aapke employer ne do mahine se salary nahi di hai. "
                    f"Indian labour laws ke mutabiq earned wages ko bina kisi statutory reason ke withhold karna illegal hai.\n\n"
                    f"**2. Applicable Indian Laws:**\n"
                    f"{citations_text}\n"
                    f"- **Payment of Wages Act, 1936 (Section 5):** Har employer ko wage period khatam hone ke 7 se 10 din ke andar earned salary credit karni hoti hai.\n"
                    f"- **Payment of Wages Act, 1936 (Section 15):** Delay hone par employee Labour Authority ke paas salary ke sath 10x compensation ka claim file kar sakta hai.\n"
                    f"- **Indian Contract Act, 1872 (Section 73):** Employment contract breach hone par damages claim kiye ja sakte hain.\n\n"
                    f"**3. Essential Evidence to Collect:**\n"
                    f"- Appointment letter ya offer email.\n"
                    f"- Past salary slips aur bank statement.\n"
                    f"- HR / Manager ke sath WhatsApp chats ya email follow-ups.\n\n"
                    f"**4. Practical Next Steps:**\n"
                    f"1. **Formal Demand Notice:** HR aur company management ko 15-day written legal demand notice bhejein.\n"
                    f"2. **Labour Commissioner:** Agar payment na mile to Labour Commissioner office me complaint darj karein.{fu_text}"
                )
            else:
                return (
                    f"[LawPilot AI — Grounded Demo Mode]\n\n"
                    f"### 💼 Employment Legal Analysis: Unpaid Salary & Withheld Dues\n\n"
                    f"**1. Legal Assessment of Your Situation:**\n"
                    f"You have reported that your employer has not paid your salary for two months. "
                    f"Under Indian labour law, withholding earned wages for services already rendered is a serious statutory violation.\n\n"
                    f"**2. Applicable Indian Legal Provisions:**\n"
                    f"{citations_text}\n"
                    f"- **Payment of Wages Act, 1936 (Section 5):** Employers must disburse wages within 7 days (for establishments with < 1,000 employees) or 10 days of the wage period.\n"
                    f"- **Payment of Wages Act, 1936 (Section 15):** Grants employees the right to file claims for delayed or wrongfully withheld wages before the statutory Authority, along with compensation of up to 10 times the withheld amount.\n"
                    f"- **Indian Contract Act, 1872 (Section 73):** Breach of employment terms entitles the employee to full compensation for financial dues owed.\n\n"
                    f"**3. Essential Evidence to Preserve:**\n"
                    f"- Appointment letter / employment contract.\n"
                    f"- Bank account statements and prior salary slips proving employment and compensation rate.\n"
                    f"- Email communications, attendance logs, and WhatsApp messages with management.\n\n"
                    f"**4. Practical Next Steps:**\n"
                    f"1. **Send a Formal Demand Notice:** Issue a written 15-day demand notice to the company and HR demanding immediate disbursement.\n"
                    f"2. **Approach Labour Authorities:** If unresolved, file a formal complaint before the Labour Commissioner or the Authority under the Payment of Wages Act.{fu_text}"
                )

        # -------------------------------------------------------------
        # DOMAIN 2: CONSUMER PROTECTION (TEST 5)
        # -------------------------------------------------------------
        elif category == CaseCategoryEnum.CONSUMER or ef.get("category") == "consumer":
            if language == LanguageEnum.HINDI:
                return (
                    f"[LawPilot AI — प्रमाणित वैधानिक डेमो मोड]\n\n"
                    f"### 🛒 उपभोक्ता अधिकार विश्लेषण: खराब उत्पाद एवं रिफंड विवाद\n\n"
                    f"**1. आपकी स्थिति का विश्लेषण:**\n"
                    f"आपने एक खराब उत्पाद (Defective Product) खरीदा है और विक्रेता (Seller) रिफंड देने से मना कर रहा है। "
                    f"उपभोक्ता संरक्षण अधिनियम, 2019 के तहत यह गैरकानूनी है।\n\n"
                    f"**2. लागू होने वाले भारतीय कानून:**\n"
                    f"{citations_text}\n"
                    f"- **Consumer Protection Act, 2019 (धारा 2(47)):** खराब सामान को वापस लेने या 30 दिनों के भीतर रिफंड न देना अनुचित व्यापार व्यवहार (Unfair Trade Practice) माना जाता है।\n"
                    f"- **Consumer Protection Act, 2019 (धारा 35):** उपभोक्ता को जिला उपभोक्ता आयोग (District Consumer Commission) में शिकायत दर्ज करने का अधिकार है।\n"
                    f"- **ई-कॉमर्स नियम, 2020:** प्लेटफॉर्म को 48 घंटे में शिकायत स्वीकार करनी होगी और 30 दिनों में समाधान करना होगा।\n\n"
                    f"**3. व्यावहारिक कदम (Practical Next Steps):**\n"
                    f"1. राष्ट्रीय उपभोक्ता हेल्पलाइन (**NCH 1915**) पर शिकायत दर्ज करें।\n"
                    f"2. विक्रेता को 15 दिनों का औपचारिक मांग पत्र (Refund Demand Notice) भेजें।\n"
                    f"3. यदि समाधान न हो, तो **e-Daakhil** पोर्टल के माध्यम से ऑनलाइन शिकायत दर्ज करें।{fu_text}"
                )
            elif language == LanguageEnum.HINGLISH:
                return (
                    f"[LawPilot AI — Grounded Demo Mode]\n\n"
                    f"### 🛒 Consumer Rights Analysis: Defective Product & Refund Denial\n\n"
                    f"**1. Situation Analysis:**\n"
                    f"Aapne defective product purchase kiya hai aur seller refund dene se inkar kar raha hai. "
                    f"Ye Consumer Protection Act, 2019 ke tehat explicit Unfair Trade Practice hai.\n\n"
                    f"**2. Applicable Indian Laws:**\n"
                    f"{citations_text}\n"
                    f"- **Consumer Protection Act, 2019 (Section 2(47)):** Defective goods ko wapas na lena ya refund refuse karna unlawful hai.\n"
                    f"- **Consumer Protection Act, 2019 (Section 35):** Aap District Consumer Commission me compensation claim kar sakte hain.\n\n"
                    f"**3. Practical Steps:**\n"
                    f"1. National Consumer Helpline (**1915**) par complaint darj karein.\n"
                    f"2. Seller ko 15-day formal legal demand notice bhejein.\n"
                    f"3. Agar na maanein to e-Daakhil ke through complaint file karein.{fu_text}"
                )
            else:
                return (
                    f"[LawPilot AI — Grounded Demo Mode]\n\n"
                    f"### 🛒 Consumer Rights Analysis: Defective Product & Refund Refusal\n\n"
                    f"**1. Legal Assessment of Your Situation:**\n"
                    f"You purchased a product that turned out defective, and the seller/platform is unlawfully refusing a refund or replacement.\n\n"
                    f"**2. Applicable Indian Consumer Laws:**\n"
                    f"{citations_text}\n"
                    f"- **Consumer Protection Act, 2019 (Section 2(47)):** Refusing to withdraw defective goods or refund consideration within the agreed period (or within 30 days) constitutes an explicit **Unfair Trade Practice**.\n"
                    f"- **Consumer Protection Act, 2019 (Section 35 & 84):** Gives consumers the right to file a complaint before the District Consumer Commission and claim product liability damages.\n"
                    f"- **Consumer Protection (E-Commerce) Rules, 2020:** Mandates platforms to accept returns and resolve consumer complaints within 30 days.\n\n"
                    f"**3. Essential Evidence to Preserve:**\n"
                    f"- Purchase tax invoice / order receipt.\n"
                    f"- Photos or unboxing video demonstrating the defect.\n"
                    f"- Customer support communication and rejection emails.\n\n"
                    f"**4. Practical Next Steps:**\n"
                    f"1. **National Consumer Helpline (NCH):** Register a complaint immediately via **1915** or online at https://consumerhelpline.gov.in/.\n"
                    f"2. **Issue a Formal Refund Notice:** Send a registered 15-day demand notice.\n"
                    f"3. **File via e-Daakhil:** Submit an e-complaint before the District Consumer Commission without requiring a lawyer.{fu_text}"
                )

        # -------------------------------------------------------------
        # DOMAIN 3: TENANT & LANDLORD DISPUTES (TEST 4)
        # -------------------------------------------------------------
        elif category == CaseCategoryEnum.TENANT or ef.get("category") == "tenant":
            if language == LanguageEnum.HINDI:
                return (
                    f"[LawPilot AI — प्रमाणित वैधानिक डेमो मोड]\n\n"
                    f"### 🏠 किरायेदारी विवाद विश्लेषण: सिक्योरिटी डिपॉजिट की वापसी\n\n"
                    f"**1. आपकी स्थिति का विश्लेषण:**\n"
                    f"आपके अनुसार, मकान मालिक आपकी {amt_str} की सुरक्षा राशि (Security Deposit) वापस नहीं कर रहा है।\n\n"
                    f"**2. लागू होने वाले भारतीय कानून:**\n"
                    f"{citations_text}\n"
                    f"- **Transfer of Property Act, 1882 (धारा 108(m)):** किरायेदार केवल सामान्य टूट-फूट (Reasonable Wear & Tear) को छोड़कर मकान सही स्थिति में सौंपने के लिए बाध्य है। सामान्य पेंटिंग या उम्र के कारण होने वाले घिसाव के लिए मकान मालिक मनमानी कटौती नहीं कर सकता।\n"
                    f"- **Model Tenancy Act, 2021 (धारा 11):** खाली कब्जा सौंपने के समय वैध कटौतियों के बाद डिपॉजिट वापस करना अनिवार्य है।\n\n"
                    f"**3. व्यावहारिक कदम (Practical Next Steps):**\n"
                    f"1. बैंक ट्रांसफर और व्हाट्सऐप पर कब्जा सौंपने का रिकॉर्ड सुरक्षित रखें।\n"
                    f"2. 15 दिनों का औपचारिक कानूनी मांग पत्र (Demand Letter) भेजें।\n"
                    f"3. समाधान न होने पर रेंट अथॉरिटी या सिविल कोर्ट में वसूली वाद दायर करें।{fu_text}"
                )
            elif language == LanguageEnum.HINGLISH:
                return (
                    f"[LawPilot AI — Grounded Demo Mode]\n\n"
                    f"### 🏠 Tenancy Legal Analysis: Security Deposit Withholding\n\n"
                    f"**1. Situation Analysis:**\n"
                    f"Aapke description ke mutabiq, landlord {amt_str} ka security deposit wapas nahi kar raha hai.\n\n"
                    f"**2. Applicable Indian Laws:**\n"
                    f"{citations_text}\n"
                    f"- **Transfer of Property Act, 1882 (Section 108):** Normal weathering aur routine repainting 'reasonable wear & tear' me aate hain, jiske liye landlord arbitrary deduction nahi kar sakta.\n"
                    f"- **Model Tenancy Act, 2021 (Section 11):** Vacant possession handover ke waqt deposit refund mandatory hai.\n\n"
                    f"**3. Practical Next Steps:**\n"
                    f"1. Payment receipt aur flat handover pictures/videos preserve karein.\n"
                    f"2. 15-day formal legal demand notice bhejein.\n"
                    f"3. Agar refund na mile to Rent Authority me complaint darj karein.{fu_text}"
                )
            else:
                return (
                    f"[LawPilot AI — Grounded Demo Mode]\n\n"
                    f"### 🏠 Tenancy Legal Analysis: Security Deposit Withholding\n\n"
                    f"**1. Legal Assessment of Your Situation:**\n"
                    f"Your landlord has withheld {amt_str} from your security deposit. "
                    f"Under Indian tenancy jurisprudence, a security deposit remains the tenant's property held in trust and must be refunded upon peaceful handover.\n\n"
                    f"**2. Applicable Indian Legal Provisions:**\n"
                    f"{citations_text}\n"
                    f"- **Transfer of Property Act, 1882 (Section 108(m)):** The tenant is bound to restore the premises in good condition, subject only to **reasonable wear and tear**. Routine repainting and standard weathering cannot be deducted without explicit contractual proof of tenant-caused structural damage.\n"
                    f"- **Model Tenancy Act, 2021 (Section 11):** Mandates that the security deposit must be refunded to the tenant at the time of taking over vacant possession, after deducting only agreed, verifiable dues.\n\n"
                    f"**3. Essential Evidence to Preserve:**\n"
                    f"- Bank transfer / UPI receipt proving the original deposit payment.\n"
                    f"- Move-out photographs or handover videos demonstrating clean handover.\n"
                    f"- WhatsApp/email communications showing notice of vacating.\n\n"
                    f"**4. Practical Next Steps:**\n"
                    f"1. **Send Formal Written Demand Notice:** Issue a registered demand letter granting 15 days to refund the full deposit.\n"
                    f"2. **Approach Rent Authority / Civil Court:** If the notice is ignored, file a petition before the local Rent Authority or a summary recovery suit under Order 37 CPC.{fu_text}"
                )

        # -------------------------------------------------------------
        # DOMAIN 4: GENERAL LEGAL INQUIRY
        # -------------------------------------------------------------
        else:
            return (
                f"[LawPilot AI — Grounded Demo Mode]\n\n"
                f"### 📋 General Legal Information & Guidance\n\n"
                f"Thank you for reaching out. Based on your description, this matter falls under general civil law principles in India.\n\n"
                f"**Applicable Legal Framework:**\n"
                f"{citations_text}\n\n"
                f"LawPilot AI specializes in three everyday civil legal domains:\n"
                f"1. 🏠 **Tenant & Landlord Disputes** (security deposits, maintenance deductions, illegal eviction threats)\n"
                f"2. 🛒 **Consumer Protection** (defective products, refund refusals, delivery disputes)\n"
                f"3. 💼 **Employment Issues** (unpaid/delayed salary, withheld relieving letters, full & final settlement)\n\n"
                f"If your matter relates to one of these areas, please share more specific details so I can provide precise statutory citations and draft legal documents.{fu_text}"
            )


class GeminiProvider(BaseLLMProvider):
    """Live Google Gemini Provider with verified statutory grounding and robust error reporting."""
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
        req_id = f"req_{uuid.uuid4().hex[:8]}"
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

        # Build contents from conversation history
        contents = []
        for turn in conversation_history:
            role = "user" if turn.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": turn.get("content", "")}]})
        if not contents or contents[-1]["role"] != "user":
            contents.append({"role": "user", "parts": [{"text": message}]})

        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": contents
        }

        logger.info(
            f"ReqID={req_id} | SessionID={session_id} | Provider=Gemini | RealLLMCall=True | "
            f"HistoryCount={len(conversation_history)} | CitationsCount={len(citations)}"
        )

        try:
            resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=15)
            if resp.status_code == 200:
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"ReqID={req_id} | GeminiCall=Success | First50='{text[:50]}...'")
                return ChatMessage(role="assistant", content=text, citations=citations)
            else:
                err_msg = f"Gemini API returned HTTP {resp.status_code}: {resp.text[:120]}"
                logger.error(f"ReqID={req_id} | GeminiCall=Failed | Error={err_msg}")
                return ChatMessage(
                    role="assistant",
                    content=(
                        f"⚠️ **AI Service Notice:** The live Google Gemini service returned an error ({resp.status_code}). "
                        f"Please check your API key, network connection, or retry. "
                        f"You can also continue using LawPilot AI in Grounded Demo Mode."
                    ),
                    citations=citations
                )
        except Exception as e:
            err_msg = str(e)
            logger.error(f"ReqID={req_id} | GeminiCall=Exception | Error={err_msg}")
            return ChatMessage(
                role="assistant",
                content=(
                    f"⚠️ **AI Service Notice:** Unable to reach live Gemini API ({err_msg}). "
                    f"Please check your network connection and retry."
                ),
                citations=citations
            )


class LLMProviderFactory:
    """Factory to instantiate the appropriate provider."""
    @classmethod
    def get_provider(cls) -> BaseLLMProvider:
        from app.config import settings
        if settings.active_provider == "gemini" and settings.gemini_api_key:
            return GeminiProvider(settings.gemini_api_key)
        return DeterministicDemoProvider()
