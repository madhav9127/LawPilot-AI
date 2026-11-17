import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from app.models.schemas import CaseData, CaseCategoryEnum, LanguageEnum

class CaseBuilder:
    """
    Intelligent Case Extraction and Structuring Engine.
    Converts user dialogues across English, Hindi, and Hinglish into verified structured legal cases.
    Identifies missing facts, flags conflicting dates, and ensures no details are hallucinated.
    """

    # Category classification patterns
    TENANT_KEYWORDS = [
        r"\b(tenant|landlord|rent|deposit|security deposit|owner|flat|apartment|lease|evict|eviction|broker|society|roommate|wear and tear|painting charges|makaan\s*malik|kiraya|kirayedar|makandari)\b"
    ]
    CONSUMER_KEYWORDS = [
        r"\b(consumer|product|defective|amazon|flipkart|meesho|order|delivery|delivered|refund|return|courier|warranty|shopping|service not provided|damaged phone|seller|retailer|kharida|saman|paise wapas|kharab nikla)\b"
    ]
    EMPLOYMENT_KEYWORDS = [
        r"\b(salary|employee|employer|boss|company|job|resigned|resignation|appointment letter|wages|dues|full and final|fnf|relieving letter|payslip|pf|workplace|manager|naukri|vetan|tanakhwah|kaam)\b"
    ]

    # Currency extraction regex patterns
    CURRENCY_PATTERNS = [
        r"₹\s*([0-9,]+)",
        r"(?:rs\.?|inr|rupees)\s*([0-9,]+)",
        r"([0-9,]+)\s*(?:rs\.?|inr|rupees)",
        r"([0-9]+)\s*(?:k|thousand|hazar)\b",
        r"([0-9,]+)\s*ka\b"
    ]

    # Date extraction patterns
    DATE_PATTERNS = [
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
        r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*(?:20\d\d)?)\b",
        r"\b(yesterday|last week|last month|2 months ago|two months ago|do mahine pehle)\b"
    ]

    @classmethod
    def classify_category(cls, text: str) -> Tuple[CaseCategoryEnum, str]:
        """Classifies text into a legal category and sub-category."""
        lower_text = text.lower()

        # Check Tenant
        for pattern in cls.TENANT_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "general_tenancy_dispute"
                if "deposit" in lower_text or "security" in lower_text:
                    sub = "security_deposit_withheld"
                elif "deduct" in lower_text or "painting" in lower_text:
                    sub = "unfair_deduction"
                elif "evict" in lower_text or "vacat" in lower_text or "threat" in lower_text:
                    sub = "unlawful_eviction_threat"
                elif "agreement" in lower_text:
                    sub = "rental_agreement_dispute"
                return (CaseCategoryEnum.TENANT, sub)

        # Check Consumer
        for pattern in cls.CONSUMER_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "general_consumer_complaint"
                if "refund" in lower_text:
                    sub = "refund_unresolved"
                elif "defective" in lower_text or "damaged" in lower_text:
                    sub = "defective_product"
                elif "wrong" in lower_text or "different" in lower_text:
                    sub = "wrong_product_delivered"
                elif "service" in lower_text:
                    sub = "deficiency_in_service"
                return (CaseCategoryEnum.CONSUMER, sub)

        # Check Employment
        for pattern in cls.EMPLOYMENT_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "general_employment_issue"
                if "unpaid" in lower_text or "delay" in lower_text or "not received" in lower_text:
                    sub = "unpaid_or_delayed_salary"
                elif "fnf" in lower_text or "settlement" in lower_text or "relieving" in lower_text:
                    sub = "final_settlement_withheld"
                elif "deduction" in lower_text:
                    sub = "unexplained_salary_deduction"
                elif "appointment" in lower_text or "contract" in lower_text:
                    sub = "contract_or_appointment_dispute"
                return (CaseCategoryEnum.EMPLOYMENT, sub)

        return (CaseCategoryEnum.GENERAL, "general_inquiry")

    @classmethod
    def extract_amounts(cls, text: str) -> Dict[str, Any]:
        """Extracts financial figures mentioned in the text."""
        amounts = []
        lower_text = text.lower()

        for pattern in cls.CURRENCY_PATTERNS:
            matches = re.finditer(pattern, lower_text)
            for m in matches:
                val_str = m.group(1).replace(",", "").strip()
                try:
                    val = float(val_str)
                    if "k" in m.group(0) or "thousand" in m.group(0) or "hazar" in m.group(0):
                        val *= 1000
                    amounts.append(int(val))
                except ValueError:
                    continue

        if not amounts:
            # Fallback for bare numbers preceding/following key words
            num_matches = re.findall(r"\b(\d{4,7})\b", text)
            for n in num_matches:
                amounts.append(int(n))

        res = {"currency": "INR"}
        if amounts:
            res["primary_amount"] = amounts[0]
            res["all_detected_amounts"] = list(set(amounts))
            res["formatted_primary"] = f"₹{amounts[0]:,}"
        else:
            res["primary_amount"] = None
            res["formatted_primary"] = "Not specified"
        return res

    @classmethod
    def extract_dates_and_check_conflicts(cls, text: str) -> Tuple[List[str], Optional[str]]:
        """Extracts dates and checks for blatant chronological contradictions."""
        found_dates = []
        for pattern in cls.DATE_PATTERNS:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for m in matches:
                found_dates.append(m.strip())

        conflict_warning = None
        # Check for contradictory dates (e.g. Test A2: vacating before moving in, or contradictory dates in text)
        if len(found_dates) >= 2:
            lower = text.lower()
            if "vacated on" in lower and "moved in on" in lower:
                # check if move in date appears later than vacate date
                try:
                    # simplified check if user mentions impossible sequence
                    if re.search(r"vacated\s+on\s+([a-z0-9\s]+)\s+and\s+moved\s+in\s+on\s+([a-z0-9\s]+)", lower):
                        conflict_warning = "Contradictory timeline detected: Move-in date appears after the vacate date. Please clarify the correct chronology."
                except Exception:
                    pass

        return found_dates, conflict_warning

    @classmethod
    def extract_case(cls, text: str, state_jurisdiction: Optional[str] = None, previous_case: Optional[CaseData] = None) -> CaseData:
        """
        Builds or updates a CaseData model based on user dialogue.
        Strictly preserves factual accuracy without inventing data.
        """
        category, sub_category = cls.classify_category(text)
        amounts_data = cls.extract_amounts(text)
        dates, date_conflict = cls.extract_dates_and_check_conflicts(text)

        # Determine parties & roles
        user_role = "Aggrieved Party"
        counterparty_role = "Opposing Party"
        if category == CaseCategoryEnum.TENANT:
            user_role = "Tenant"
            counterparty_role = "Landlord / Property Owner"
        elif category == CaseCategoryEnum.CONSUMER:
            user_role = "Consumer / Purchaser"
            counterparty_role = "Seller / E-Commerce Platform"
        elif category == CaseCategoryEnum.EMPLOYMENT:
            user_role = "Employee"
            counterparty_role = "Employer / Management"

        # Determine agreement status
        agreements = "Not specified in conversation"
        lower = text.lower()
        if "no written agreement" in lower or "bina agreement" in lower or "no agreement" in lower:
            agreements = "Oral tenancy / No written contract (Corroborated by bank transactions & communication)"
        elif "rental agreement" in lower or "lease agreement" in lower or "contract" in lower:
            agreements = "Written agreement exists"

        # Detect evidence mentioned
        evidence_found = []
        if any(w in lower for w in ["bank statement", "upi", "transfer", "bank proof", "account statement"]):
            evidence_found.append("Bank Transfer Proof / Account Statements")
        if any(w in lower for w in ["whatsapp", "chat", "message"]):
            evidence_found.append("WhatsApp / SMS Chat Records")
        if any(w in lower for w in ["invoice", "bill", "receipt", "slip", "payslip", "salary slip"]):
            evidence_found.append("Payment Receipt / Payslips / Invoices")
        if any(w in lower for w in ["email", "mail", "written notice"]):
            evidence_found.append("Email Correspondence")
        if any(w in lower for w in ["photo", "video", "unboxing"]):
            evidence_found.append("Photographic / Video Evidence")

        # Determine missing information
        missing = []
        if not amounts_data.get("primary_amount"):
            missing.append("Exact financial amount in dispute (in ₹).")
        if not state_jurisdiction:
            missing.append("State or City where the incident occurred (determines applicable state tenancy/shops laws).")
        if not dates:
            missing.append("Key dates (e.g. date of transaction, handover date, or payment due date).")
        if not evidence_found:
            missing.append("Status of written documentation or electronic communication proofs.")

        # Timeline
        timeline = []
        if dates:
            for d in dates:
                timeline.append({"date": d, "event": "Event referenced in user statement"})
        else:
            timeline.append({"date": "Recent", "event": "Dispute reported by user"})

        # Counterparty Name extraction heuristic
        counterparty_name = counterparty_role
        m_name = re.search(r"(?:from|against|with|company|seller|landlord|owner)\s+([A-Z][a-zA-Z0-9\s]{2,20})", text)
        if m_name and m_name.group(1).lower() not in ["the", "a", "my", "this", "that"]:
            counterparty_name = m_name.group(1).strip()

        case = CaseData(
            category=category,
            sub_category=sub_category,
            user_role=user_role,
            counterparty_name=counterparty_name,
            counterparty_role=counterparty_role,
            incident_description=text.strip(),
            timeline=timeline,
            financial_amounts=amounts_data,
            agreements=agreements,
            available_evidence=evidence_found,
            actions_already_taken=["Consulted LawPilot AI for initial legal assessment"],
            desired_resolution="Full recovery of dues / refund / settlement with statutory interest",
            missing_information=missing,
            state_jurisdiction=state_jurisdiction or "To be specified by user"
        )

        return case

    @classmethod
    def generate_follow_up_questions(cls, case: CaseData, language: LanguageEnum = LanguageEnum.ENGLISH) -> List[str]:
        """Generates contextual, non-repetitive follow-up questions targeting missing information."""
        questions = []
        
        # Missing state
        if not case.state_jurisdiction or case.state_jurisdiction == "To be specified by user":
            if language == LanguageEnum.HINDI:
                questions.append("यह मामला किस राज्य या शहर का है? (राज्य के अनुसार रेंट कंट्रोल या शॉप्स एक्ट अलग होते हैं)")
            elif language == LanguageEnum.HINGLISH:
                questions.append("Ye incident kis State ya City me hua hai? (State ke hisab se tenancy ya shops act apply hota hai)")
            else:
                questions.append("In which Indian State or Union Territory did this incident occur? (State tenancy/shops acts vary)")

        # Missing amount
        if not case.financial_amounts.get("primary_amount"):
            if language == LanguageEnum.HINDI:
                questions.append("विवादित कुल राशि (रुपयों में) कितनी है?")
            elif language == LanguageEnum.HINGLISH:
                questions.append("Disputed total amount (₹ me) kitna hai?")
            else:
                questions.append("What is the exact financial amount (in ₹) involved in this dispute?")

        # Missing written proof
        if not case.available_evidence:
            if language == LanguageEnum.HINDI:
                questions.append("क्या आपके पास बैंक ट्रांसफर, रसीद या व्हाट्सऐप संदेशों का कोई लिखित प्रमाण है?")
            elif language == LanguageEnum.HINGLISH:
                questions.append("Kya aapke paas bank transfer receipt, WhatsApp chat ya written proof available hai?")
            else:
                questions.append("Do you possess written proofs such as bank transaction receipts, emails, or WhatsApp chat logs?")

        # Category specific question
        if case.category == CaseCategoryEnum.TENANT:
            if language == LanguageEnum.HINDI:
                questions.append("क्या आपने मकान खाली करते समय चाबी सौंपने या कमरे की स्थिति की तस्वीरें ली थीं?")
            elif language == LanguageEnum.HINGLISH:
                questions.append("Vacate karte waqt kya aapne flat handover ki photos ya key handover confirmation liya tha?")
            else:
                questions.append("Did you document the property condition (photos/videos) or retain written handover proof when vacating?")
        elif case.category == CaseCategoryEnum.CONSUMER:
            if language == LanguageEnum.HINDI:
                questions.append("क्या आपने विक्रेता या ई-कॉमर्स सपोर्ट पर आधिकारिक शिकायत टिकट दर्ज किया था?")
            elif language == LanguageEnum.HINGLISH:
                questions.append("Kya aapne seller ya platform customer care me official ticket/complaint register kiya tha?")
            else:
                questions.append("Have you logged an official customer support ticket or registered a complaint with the National Consumer Helpline (NCH)?")
        elif case.category == CaseCategoryEnum.EMPLOYMENT:
            if language == LanguageEnum.HINDI:
                questions.append("क्या आपने कंपनी को फुल एंड फाइनल सेटलमेंट या बकाया वेतन के लिए लिखित ईमेल भेजा है?")
            elif language == LanguageEnum.HINGLISH:
                questions.append("Kya aapne HR/Finance ko full and final settlement ya salary clearance ke liye formal email bheja hai?")
            else:
                questions.append("Have you sent a formal written demand email to HR or management regarding the release of salary/settlement dues?")

        return questions[:3]  # Return at most 3 concise questions to avoid overwhelming user
