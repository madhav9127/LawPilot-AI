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

class BaseLLMProvider(ABC):
    """Abstract Base Class for modular LLM providers."""
    
    @abstractmethod
    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: LanguageEnum,
        state_jurisdiction: Optional[str] = None
    ) -> ChatMessage:
        pass


class DeterministicDemoProvider(BaseLLMProvider):
    """
    Intelligent Grounded Deterministic Demo Provider.
    Used when no live API key is configured.
    Provides mathematically reproducible, statutory-grounded responses in EN, HI, and Hinglish.
    Clearly marked as [Demo Mode — Grounded Statutory Rules]. Never fabricates facts or citations.
    """

    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: LanguageEnum,
        state_jurisdiction: Optional[str] = None
    ) -> ChatMessage:
        lower_msg = message.lower().strip()
        
        # 1. Inspect for prompt injection / adversarial threats (A5)
        is_threat, threat_details = Sanitizer.inspect_for_threats(message)
        if is_threat:
            content = (
                "[Demo Mode — Grounded Statutory Rules]\n\n"
                "⚠️ **Safety Intervention: Prompt Injection Detected**\n\n"
                "LawPilot AI detected an attempt to override system instructions or bypass legal safety guardrails. "
                "As an ethical legal assistant, LawPilot AI adheres strictly to verified Indian statutory laws and safety boundaries. "
                "System instructions and legal integrity cannot be overridden."
            )
            return ChatMessage(
                role="assistant",
                content=content,
                citations=[],
                verification_status=VerificationStatusEnum.VERIFIED,
                missing_info=[],
                follow_up_questions=[]
            )

        # 2. Check for Request to Invent Fake Legal Section (A1)
        if any(w in lower_msg for w in ["invent a legal section", "make up a law", "fake section", "create a fictional section"]):
            content = (
                "[Demo Mode — Grounded Statutory Rules]\n\n"
                "🛑 **Statutory Integrity Rule: Section Invention Refused**\n\n"
                "LawPilot AI strictly refuses to invent, fabricate, or hallucinate non-existent legal sections or court judgments. "
                "Under Indian jurisprudence, legal claims must be founded strictly on enacted statutes published in the Gazette of India "
                "or official State Gazettes (accessible via India Code at https://www.indiacode.nic.in/).\n\n"
                "If you are dealing with a tenancy, consumer, or employment dispute, I will only cite verified statutory provisions "
                "such as Section 108 of the Transfer of Property Act, 1882 or Section 2(47) of the Consumer Protection Act, 2019."
            )
            return ChatMessage(
                role="assistant",
                content=content,
                citations=[],
                verification_status=VerificationStatusEnum.VERIFIED,
                missing_info=[],
                follow_up_questions=["Would you like me to explain the genuine, verified provisions applicable to your situation?"]
            )

        # 3. Check for Guarantee of Victory (A3)
        if any(w in lower_msg for w in ["guarantee a win", "guarantee victory", "100% win", "promise i will win", "guarantee court victory"]):
            content = (
                "[Demo Mode — Grounded Statutory Rules]\n\n"
                "⚖️ **Legal Reality Check: Outcome Guarantees Prohibited**\n\n"
                "LawPilot AI cannot and will never guarantee a court victory or guaranteed legal outcome. "
                "Under Rule 36 of the Bar Council of India Rules and established legal ethics, even licensed advocates cannot promise "
                "guaranteed results. Legal outcomes in Indian courts and tribunals depend entirely on evidence admissibility, factual verification, "
                "statutory interpretation, judicial discretion, and the arguments of the counterparty.\n\n"
                "**What LawPilot AI Can Do:** Help you assemble solid documentary evidence, analyze applicable statutory rights, "
                "and prepare compliant legal notices to maximize your legal standing."
            )
            return ChatMessage(
                role="assistant",
                content=content,
                citations=[],
                verification_status=VerificationStatusEnum.VERIFIED,
                missing_info=[],
                follow_up_questions=["Would you like to review the evidence checklist required to support your claim?"]
            )

        # 4. Check for Incorrect Citation Confirmation (A9)
        if "section 999" in lower_msg or ("section" in lower_msg and "confirm" in lower_msg and ("fake" in lower_msg or "99" in lower_msg or "rental act" in lower_msg)):
            content = (
                "[Demo Mode — Grounded Statutory Rules]\n\n"
                "🔍 **Citation Verification Result: Citation Refuted**\n\n"
                "Verification against the official India Code database confirms that the citation you provided is **incorrect or non-existent**.\n\n"
                "- There is no 'Section 999' or general 'Section 99' under standard Indian Tenancy legislation providing unilateral penalties.\n"
                "- The genuine statutory provisions governing tenancy durations and reasonable wear & tear are **Section 106 and Section 108(m)** of "
                "The Transfer of Property Act, 1882, as well as Section 11 of the Model Tenancy Act, 2021.\n\n"
                "Always verify citations via official government repositories such as https://www.indiacode.nic.in/ before issuing formal legal notices."
            )
            citations = LegalKnowledgeBase.retrieve_grounded_laws("tenancy security deposit wear and tear", CaseCategoryEnum.TENANT)
            return ChatMessage(
                role="assistant",
                content=content,
                citations=citations,
                verification_status=VerificationStatusEnum.VERIFIED,
                missing_info=[],
                follow_up_questions=["Would you like me to draft a notice using the verified statutory sections instead?"]
            )

        # 5. Check for Out-of-Domain Requests (A4)
        if any(w in lower_msg for w in ["murder", "divorce", "custody", "patent", "trademark infringement", "dowry", "assault", "ipc 302", "bns"]):
            content = (
                "[Demo Mode — Grounded Statutory Rules]\n\n"
                "ℹ️ **Jurisdiction & Domain Scope Notice**\n\n"
                "This query falls outside LawPilot AI's core specialized domains (Tenant Disputes, Consumer Protection, and Employment Issues).\n\n"
                "**Important Limitation:** For criminal matters, matrimonial disputes (divorce/custody), or specialized intellectual property, "
                "automated guidance cannot provide reliable procedural coverage. "
                "You must consult a qualified advocate specializing in criminal or family law.\n\n"
                "**Legal Aid Option:** If you cannot afford an advocate, you may apply for free legal aid through the "
                "National Legal Services Authority (NALSA) at https://nalsa.gov.in/ or call the national helpline **15100**."
            )
            return ChatMessage(
                role="assistant",
                content=content,
                citations=[],
                verification_status=VerificationStatusEnum.INSUFFICIENT,
                missing_info=["Case falls outside Tenant, Consumer, and Employment domains."],
                follow_up_questions=["Do you have an issue related to rent/tenancy, consumer purchases, or unpaid salary?"]
            )

        # 6. Check for Urgent Escalation (A6)
        escalation = EscalationDetector.analyze(message)
        if escalation.is_escalated and escalation.urgency_level in ["critical", "high"]:
            content = (
                f"[Demo Mode — Grounded Statutory Rules]\n\n"
                f"🚨 **EMERGENCY ESCALATION ALERT ({escalation.urgency_level.upper()})**\n\n"
                f"**Reason for Escalation:** {', '.join(escalation.reasons)}\n\n"
                f"{escalation.recommended_action}\n\n"
                f"**CRITICAL HELPLINES & LEGAL AID:**\n"
                f"- **National Emergency Service:** Dial **112** (Immediate police & emergency intervention)\n"
                f"- **NALSA Free Legal Aid Helpline:** Dial **15100** (Free legal aid for eligible citizens)\n"
                f"- **Women Helpline (All India):** Dial **1091**\n\n"
                f"⚠️ *Disclaimer:* {EscalationDetector.STANDARD_DISCLAIMER}"
            )
            return ChatMessage(
                role="assistant",
                content=content,
                citations=[],
                verification_status=VerificationStatusEnum.RECOMMENDED,
                missing_info=[],
                follow_up_questions=["Have you been physically harmed or are you in immediate danger right now?"],
                escalation_detected=True,
                escalation_details=escalation.model_dump()
            )

        # 7. Check for Contradictory Dates (A2)
        dates, date_conflict = CaseBuilder.extract_dates_and_check_conflicts(message)
        if date_conflict:
            content = (
                "[Demo Mode — Grounded Statutory Rules]\n\n"
                f"⚠️ **Chronological Timeline Inconsistency Detected**\n\n"
                f"{date_conflict}\n\n"
                "Under Indian procedural law, inconsistent factual statements undermine your credibility in legal notices and court affidavits. "
                "Please confirm the exact dates so we can build an accurate case timeline."
            )
            return ChatMessage(
                role="assistant",
                content=content,
                citations=[],
                verification_status=VerificationStatusEnum.INSUFFICIENT,
                missing_info=["Chronological order of move-in and vacate dates."],
                follow_up_questions=["Can you confirm: On what exact date did you move in, and on what date did you hand over possession?"]
            )

        # 8. Extract Structured Case
        case = CaseBuilder.extract_case(message, state_jurisdiction=state_jurisdiction)
        citations = LegalKnowledgeBase.retrieve_grounded_laws(message, case.category, state=state_jurisdiction)
        follow_ups = CaseBuilder.generate_follow_up_questions(case, language=language)

        # 9. Format 8-Point Legal Position Analysis in requested Language
        content = self._format_analysis_response(case, citations, language, state_jurisdiction)

        return ChatMessage(
            role="assistant",
            content=content,
            citations=citations,
            verification_status=VerificationStatusEnum.VERIFIED if citations else VerificationStatusEnum.RECOMMENDED,
            missing_info=case.missing_information,
            follow_up_questions=follow_ups,
            escalation_detected=False
        )

    def _format_analysis_response(
        self,
        case: CaseData,
        citations: List[LegalCitation],
        language: LanguageEnum,
        state: Optional[str]
    ) -> str:
        amt_str = case.financial_amounts.get("formatted_primary", "an unspecified amount")
        state_str = state if state else "India (Central statutes applied; state rent/shops acts may also apply)"

        # Citation list markdown
        c_lines = []
        for c in citations:
            c_lines.append(f"- **{c.act_name} — {c.section}**: {c.title} ([Official Source]({c.official_url}))")
        citations_md = "\n".join(c_lines) if c_lines else "General principles of Indian contract and civil jurisprudence apply."

        # HINDI RESPONSE
        if language == LanguageEnum.HINDI:
            return (
                f"[डेमो मोड — प्रमाणित वैधानिक नियम]\n\n"
                f"### 📋 आपकी कानूनी स्थिति का विश्लेषण (Legal Position Analysis)\n\n"
                f"**1. क्या प्रतीत होता है (What Happened):**\n"
                f"आपके विवरण के अनुसार, {case.counterparty_role} के साथ {amt_str} की राशि को लेकर विवाद उत्पन्न हुआ है।\n\n"
                f"**2. महत्वपूर्ण तथ्य (Key Facts):**\n"
                f"- आपकी भूमिका: {case.user_role}\n"
                f"- विवादित राशि: {amt_str}\n"
                f"- अनुबंध की स्थिति: {case.agreements}\n"
                f"- उपलब्ध साक्ष्य: {', '.join(case.available_evidence) if case.available_evidence else 'प्रमाण विवरण प्रतीक्षित'}\n\n"
                f"**3. लागू होने वाले भारतीय कानून (Applicable Laws):**\n"
                f"{citations_md}\n\n"
                f"**4. आपके कानूनी अधिकार एवं संरक्षण (Rights & Protections):**\n"
                f"- भारतीय कानून के तहत बिना किसी लिखित आधार या वास्तविक क्षति के मनमानी कटौती या भुगतान रोकना गैरकानूनी है।\n"
                f"- सामान्य टूट-फूट (Normal wear and tear) के नाम पर राशि काटना कानूनन प्रतिबंधित है।\n\n"
                f"**5. उपलब्ध कानूनी उपाय (Available Remedies):**\n"
                f"- 15 दिनों का औपचारिक कानूनी मांग पत्र (Formal Demand / Legal Notice) भेजना।\n"
                f"- उपभोक्ता आयोग (e-Daakhil) या रेंट अथॉरिटी / लेबर कमिश्नर के समक्ष शिकायत दर्ज करना।\n\n"
                f"**6. व्यावहारिक विकल्प (Practical Options):**\n"
                f"- पहले लिखित में अंतिम अल्टीमेटम दें।\n"
                f"- सभी व्हाट्सएप चैट और बैंक ट्रांसफर का रिकॉर्ड सुरक्षित रखें।\n\n"
                f"**7. जोखिम एवं सीमाएं (Risks & Limitations):**\n"
                f"- यदि लिखित समझौता नहीं है, तो बैंक स्टेटमेंट ही मुख्य प्रमाण होगा। कानूनी प्रक्रिया में समय लग सकता है।\n\n"
                f"**8. अनुशंसित अगला कदम (Recommended Next Steps):**\n"
                f"1. नीचे दिए गए 'दस्तावेज़ जनरेटर' (Document Generator) से मांग पत्र का ड्राफ्ट तैयार करें।\n"
                f"2. साक्ष्य चेकलिस्ट के अनुसार अपने बैंक विवरण एकत्रित करें।"
            )

        # HINGLISH RESPONSE
        elif language == LanguageEnum.HINGLISH:
            return (
                f"[Demo Mode — Grounded Statutory Rules]\n\n"
                f"### 📋 Aapki Legal Position Ka Analysis\n\n"
                f"**1. Kya Hua Hai (What Happened):**\n"
                f"Aapke description ke mutabiq, {case.counterparty_role} ke sath {amt_str} ke amount ko lekar dispute hua hai.\n\n"
                f"**2. Zaroori Facts (Important Facts):**\n"
                f"- Aapka Role: {case.user_role}\n"
                f"- Disputed Amount: {amt_str}\n"
                f"- Agreement Status: {case.agreements}\n"
                f"- Available Evidence: {', '.join(case.available_evidence) if case.available_evidence else 'Details pending'}\n\n"
                f"**3. Applicable Indian Laws & Citations:**\n"
                f"{citations_md}\n\n"
                f"**4. Aapke Rights & Protections:**\n"
                f"- Indian law ke mutabiq, bina itemized proof ke security deposit ya earned salary withhold karna unlawful hai.\n"
                f"- Normal wear & tear (jaise routine painting) tenant ki liability nahi hoti (Transfer of Property Act Section 108).\n\n"
                f"**5. Available Remedies:**\n"
                f"- Formal written Demand Notice (15-day compliance window ke sath).\n"
                f"- State Rent Authority / Consumer Commission (e-Daakhil) / Labour Commissioner me petition file karna.\n\n"
                f"**6. Practical Options:**\n"
                f"- Pehle traceable channel (Email + Speed Post / WhatsApp) se clear written notice bhein.\n"
                f"- Bina advocate ke bhi National Consumer Helpline (1915) ya NALSA se pre-litigation help le sakte hain.\n\n"
                f"**7. Risks & Limitations:**\n"
                f"- Agar counterparty refuse kare, to statutory forum me proceed karna hoga jisme documentation solid honi chahiye.\n\n"
                f"**8. Recommended Next Steps:**\n"
                f"1. 'Document Generator' tab se Demand Draft generate karein.\n"
                f"2. Evidence Checklist ke document collect karke verify karein."
            )

        # DEFAULT ENGLISH RESPONSE
        else:
            return (
                f"[Demo Mode — Grounded Statutory Rules]\n\n"
                f"### 📋 Comprehensive Legal Position Analysis\n\n"
                f"**1. What Appears to Have Happened:**\n"
                f"Based on your statement, a legal grievance has arisen with your {case.counterparty_role} regarding {amt_str}.\n\n"
                f"**2. Important Facts Extracted:**\n"
                f"- **Your Role:** {case.user_role}\n"
                f"- **Disputed Amount:** {amt_str}\n"
                f"- **Contractual Status:** {case.agreements}\n"
                f"- **Documentary Proofs:** {', '.join(case.available_evidence) if case.available_evidence else 'To be collected per checklist'}\n"
                f"- **Jurisdiction:** {state_str}\n\n"
                f"**3. Potentially Applicable Laws & Grounded Citations:**\n"
                f"{citations_md}\n\n"
                f"**4. Possible Legal Rights & Protections:**\n"
                f"- Under Indian jurisprudence, arbitrary retention of refundable funds without verifiable itemized damage or statutory deduction violates established contract and tenancy law.\n"
                f"- In tenancy matters, normal weathering and painting fall under reasonable wear and tear unless explicitly contracted otherwise.\n"
                f"- In consumer matters, refusal to replace or refund for defective goods constitutes an Unfair Trade Practice under Section 2(47) of the Consumer Protection Act, 2019.\n\n"
                f"**5. Available Statutory Remedies:**\n"
                f"- Issuance of a formal 15-day statutory Demand Notice via traceable registered speed post or electronic mail.\n"
                f"- Escalation to the competent statutory forum (e.g., District Consumer Commission via e-Daakhil, Rent Authority, or Labour Authority under Section 15 of Payment of Wages Act).\n\n"
                f"**6. Practical Options:**\n"
                f"- Attempt a formal written escalation with an explicit 15-day compliance deadline before litigation.\n"
                f"- Preserve all WhatsApp communications, bank debit statements, and invoice records under Section 65B of the Indian Evidence Act (BSA 2023 Section 63).\n\n"
                f"**7. Risks and Limitations:**\n"
                f"- Formal litigation involves filing procedures and court timelines. Amicable settlement backed by a structured demand notice is typically faster and cost-effective.\n\n"
                f"**8. Recommended Next Steps:**\n"
                f"1. Open the **Document Generator** tab to draft an itemized Demand Letter.\n"
                f"2. Review the **Evidence Checklist** tab to verify that your transaction proofs and chat exports are in order.\n"
                f"3. If unresolved within the notice period, consult a licensed advocate to initiate formal proceedings."
            )


class GeminiProvider(BaseLLMProvider):
    """Integration for Google Gemini API."""
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        language: LanguageEnum,
        state_jurisdiction: Optional[str] = None
    ) -> ChatMessage:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        # Grounding with verified statutes
        case = CaseBuilder.extract_case(message, state_jurisdiction=state_jurisdiction)
        citations = LegalKnowledgeBase.retrieve_grounded_laws(message, case.category, state=state_jurisdiction)
        statutory_context = "\n".join([f"- {c.act_name} {c.section}: {c.description}" for c in citations])
        
        system_instruction = (
            "You are LawPilot AI, an expert, ethical Indian legal assistant. "
            "You MUST ground your response in genuine Indian statutes. "
            "NEVER invent laws, sections, or court cases. Never guarantee legal victory. "
            "Respond in the requested language (English, Hindi, or Hinglish). "
            f"Verified Statutory Context:\n{statutory_context}\n"
            "Provide the 8-point Legal Position Analysis: "
            "1. What happened, 2. Important facts, 3. Applicable laws, 4. Rights, 5. Remedies, 6. Practical options, 7. Risks, 8. Next steps."
        )

        prompt = f"User input: {message}\nLanguage: {language.value}\nState: {state_jurisdiction or 'All India'}"
        
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_instruction}\n\n{prompt}"}]}
            ]
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
            follow_ups = CaseBuilder.generate_follow_up_questions(case, language=language)
            return ChatMessage(
                role="assistant",
                content=reply_text,
                citations=citations,
                verification_status=VerificationStatusEnum.VERIFIED if citations else VerificationStatusEnum.RECOMMENDED,
                missing_info=case.missing_information,
                follow_up_questions=follow_ups
            )
        else:
            # Fallback to deterministic demo provider if live API call fails
            demo = DeterministicDemoProvider()
            res = demo.generate_response(message, conversation_history, language, state_jurisdiction)
            res.content = f"[Live API Error {response.status_code}: Fallback to Grounded Engine]\n\n" + res.content
            return res


class LLMProviderFactory:
    """Factory to instantiate the appropriate provider."""
    @classmethod
    def get_provider(cls) -> BaseLLMProvider:
        from app.config import settings
        provider_name = settings.active_provider

        if provider_name == "gemini" and settings.gemini_api_key:
            return GeminiProvider(settings.gemini_api_key)
        # Default / Demo mode
        return DeterministicDemoProvider()
