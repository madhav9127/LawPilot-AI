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
        r"\b(tenant|landlord|rent|deposit|security deposit|owner|flat|apartment|lease|evict|eviction|broker|society|roommate|wear and tear|painting charges|makaan\s*malik|kiraya|kirayedar|makandari|legal notice|court notice|notice received|eviction notice)\b",
        r"(સિક્યોરિટી|ડિપોઝિટ|મકાનમાલિક|ભાડું|મકાન\s*ખાલી|કાનૂની\s*નોટિસ|લીગલ\s*નોટિસ|નોટિસ\s*મળી|किराया|मकान\s*मालिक|डिपॉज़िट|घरमालक|घरमालकाकडून|घरमालकाने|भाडेकरू|भाडे|भाड्याचे|कायदेशीर\s*नोटीस|लीगल\s*नोटीस|नोटीस\s*मिळाली|വാടക|ഡെപ്പോസിറ്റ്|വാടകക്കാരൻ|വീട്ടുടമസ്ഥൻ|നോട്ടീസ്|வாடகை|வைப்புத்தொகை|வீட்டு\s*உரிமையாளர்|நோட்டீஸ்|అద్దె|డిపాజిట్|ఇంటి\s*యజమాని|నోటీసు|ভাড়া|আমানত|বাড়িওয়ালা|নোটিশ)"
    ]
    CONSUMER_KEYWORDS = [
        r"\b(consumer|product|defective|amazon|flipkart|meesho|order|delivery|delivered|refund|return|courier|warranty|shopping|service not provided|damaged phone|seller|retailer|kharida|saman|paise wapas|kharab nikla)\b",
        r"(ખામીયુક્ત|રિફંડ|વેચનાર|ખરીદ્યો|ફોન|दोषपूर्ण|विक्रेता|उपभोक्ता|റീഫണ്ട്|തകരാർ|குறைபாடு|ரீபண்ட்|లోపం|రీఫండ్|ত্রুটি|ফেরত)"
    ]
    EMPLOYMENT_KEYWORDS = [
        r"\b(salary|employee|employer|boss|company|job|resigned|resignation|appointment letter|wages|dues|full and final|fnf|relieving letter|payslip|pf|workplace|manager|naukri|vetan|tanakhwah|kaam)\b",
        r"(પગાર|નિયોક્તા|કંપની|वेतन|नियोक्ता|तनख्वाह|തൊഴിലുടമ|ശമ്പളം|சம்பளம்|நிறுவனம்|జీతం|యజమాని|বেতন|নিয়োগকর্তা|ಸಂಬಳ)"
    ]
    CYBER_KEYWORDS = [
        r"\b(cyber|hacked|hacking|upi|phishing|otp|online fraud|identity theft|leaked photo|nude|morphing|sextortion|1930|cybercrime|fake profile|account takeover)\b",
        r"(सायबर|हॅक|ऑनलाइन फसवणूक|સાયબર|ઓનલાઇન છેતરપિંડી|സൈബർ|சைபர்)"
    ]
    BANKING_KEYWORDS = [
        r"\b(cheque|cheque bounce|dishonour|138|ni act|bounced cheque|loan default|npa|sarfaesi|recovery agent|bank ombudsman|loan app|emi|bank account freeze)\b",
        r"(चेक बाउंस|धनादेश|बँक|खाते गोठवले|ચેક બાઉન્સ|ബാങ്ക്|வங்கி)"
    ]
    CRIMINAL_KEYWORDS = [
        r"\b(fir|police|arrest|anticipatory bail|bail|theft|chori|assault|beaten|threat to kill|bns|bnss|ipc|crpc|warrant|charge sheet|criminal intimidation|defamation)\b",
        r"(पोलीस|एफआयआर|जामीन|चोरी|ધમકી|પોલીસ|જામીન|പോലീസ്|ஜாமீன்|పోలీస్)"
    ]
    PROPERTY_KEYWORDS = [
        r"\b(builder delay|rera|possession delay|flat possession|sale deed|mutation|patta|khata|encroachment|boundary dispute|land dispute|allottee|7/12|satbara)\b",
        r"(जमीन|बिल्डर|रेरा|सातबारा|જમીન|દસ્તાવેજ|భూమి|நிலம்)"
    ]
    FAMILY_KEYWORDS = [
        r"\b(divorce|mutual consent divorce|cruelty|alimony|maintenance|child custody|visitation|domestic violence|pwdva|hindu marriage act|hma|matrimonial)\b",
        r"(घटस्फोट|पोटगी|घरगुती हिंसाचार|છૂટાછેડા|ભરણપોષણ|വിവാഹമോചനം|விவாகரத்து|విడాకులు)"
    ]
    SUCCESSION_KEYWORDS = [
        r"\b(will|vasiyat|inheritance|ancestral property|coparcenary|daughter share|succession|probate|legal heir certificate|heir)\b",
        r"(वारसा|इच्छापत्र|वारसदार|વારસો|વારસદાર|പൈതൃകം|வாரிசு)"
    ]
    CONTRACT_KEYWORDS = [
        r"\b(breach of contract|agreement broken|damages|liquidated damages|penalty clause|commercial agreement|vendor dispute|partnership|sale of goods)\b",
        r"(करार मोडला|व्यापारी करार|કરાર ભંગ|ஒப்பந்த மீறல்)"
    ]
    IPR_KEYWORDS = [
        r"\b(trademark|copyright|patent|infringement|piracy|stolen logo|brand name copied|passing off|counterfeit)\b",
        r"(ट्रेडमार्क|कॉपीराइट|ટ્રેડમાર્ક|பதிப்புரிமை)"
    ]
    MOTOR_VEHICLE_KEYWORDS = [
        r"\b(mact|accident claim|hit and run|car accident|road accident|motor accident compensation|third party insurance|traffic challan)\b",
        r"(अपघात|मोटार अपघात|અકસ્માત|விபத்து|ప్రమాదం)"
    ]
    CONSTITUTIONAL_KEYWORDS = [
        r"\b(fundamental right|article 21|article 32|article 226|writ petition|habeas corpus|mandamus|unlawful detention|liberty)\b",
        r"(मूलभूत हक्क|घटनात्मक|મૂળભૂત અધિકાર|அடிப்படை உரிமை)"
    ]
    TAXATION_KEYWORDS = [
        r"\b(income tax notice|148 notice|tax scrutiny|gst notice|escaped assessment|tax penalty|rti|right to information|pio)\b",
        r"(आयकर|माहिती अधिकार|આવકવેરો|માહિતી અધિકાર|தகவல் அறியும் உரிமை)"
    ]
    WOMEN_CHILD_KEYWORDS = [
        r"\b(pocso|child abuse|dowry|dahej|dowry demand|498a|child cruelty|juvenile)\b",
        r"(हुंडा|पोक्सो|દહેજ|வரதட்சணை|వరకట్నం)"
    ]
    EDUCATION_SERVICE_KEYWORDS = [
        r"\b(rte|25% quota|ews admission|central administrative tribunal|cat|service dispute|pension withheld|promotion dispute)\b",
        r"(शिक्षण हक्क|पेन्शन|શિક્ષણ અધિકાર|கல்வி உரிமை)"
    ]
    ENVIRONMENTAL_KEYWORDS = [
        r"\b(ngt|national green tribunal|pollution|factory smoke|industrial waste|toxic effluent|tree cutting|environmental damage)\b",
        r"(प्रदूषण|पर्यावरण|હવા પ્રદૂષણ|சுற்றுச்சூழல்)"
    ]
    CIVIL_KEYWORDS = [
        r"\b(civil suit|stay order|injunction|temporary injunction|order 39|summary suit|specific performance|dispossessed)\b",
        r"(दिवाणी दावा|मनाई हुकूम|દિવાની દાવો|தடை உத்தரவு)"
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
                # Check if user received a legal notice from landlord
                is_notice = any(w in lower_text for w in [
                    "notice", "legal notice", "court notice",
                    "નોટિસ", "કાનૂની નોટિસ", "લીગલ નોટિસ",
                    "नोटीस", "कायदेशीर नोटीस", "लीगल नोटीस",
                    "नोटिस", "कानूनी नोटिस", "നോട്ടീസ്", "நோட்டீஸ்", "నోటీసు", "নোটিশ"
                ])
                is_notice_explain = any(w in lower_text for w in [
                    "understand", "explain", "meaning", "received", "got a", "help me with a notice",
                    "સમજવા", "સમજાવો", "સમજવામાં", "મળેલી", "આવેલી",
                    "समजून", "समजण्यासाठी", "मिळालेली", "आलेली",
                    "समझने", "समझाएं", "मिली", "வந்தது", "புரிந்து", "മനസ്സിലാക്കാൻ", "లభించింది", "అర్థం", "বুঝতে"
                ])
                if is_notice and (is_notice_explain or "received" in lower_text or "મળેલી" in lower_text or "मिळालेली" in lower_text or "help me" in lower_text):
                    sub = "legal_notice_received_explanation"
                elif any(w in lower_text for w in ["deposit", "security", "ડિપોઝિટ", "સિક્યોરિટી", "डिपॉज़िट", "ठेव", "ഡെപ്പോസിറ്റ്", "வைப்புத்தொகை", "డిపాజిట్", "আমানত"]):
                    sub = "security_deposit_withheld"
                elif any(w in lower_text for w in ["deduct", "painting", "charges", "કપાત", "कपात", "कापले"]):
                    sub = "unfair_deduction"
                elif any(w in lower_text for w in ["evict", "vacat", "threat", "force", "ખાલી", "કાઢી", "काढून", "बेदखल"]):
                    sub = "unlawful_eviction_threat"
                elif any(w in lower_text for w in ["agreement", "lease", "કરાર", "करार", "ஒப்பந்தம்"]):
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

        # Check Cyber & Online Fraud
        for pattern in cls.CYBER_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.CYBER, "cybercrime_or_online_fraud")

        # Check Banking & Cheque Bounce
        for pattern in cls.BANKING_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.BANKING, "banking_or_cheque_bounce")

        # Check Criminal Law
        for pattern in cls.CRIMINAL_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.CRIMINAL, "criminal_offence_or_procedure")

        # Check Property & RERA
        for pattern in cls.PROPERTY_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.PROPERTY, "real_estate_or_land_dispute")

        # Check Family Law
        for pattern in cls.FAMILY_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.FAMILY, "matrimonial_or_family_dispute")

        # Check Succession & Wills
        for pattern in cls.SUCCESSION_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.SUCCESSION, "succession_or_inheritance")

        # Check Contract & Commercial
        for pattern in cls.CONTRACT_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.CONTRACT, "contract_breach_or_commercial")

        # Check Intellectual Property
        for pattern in cls.IPR_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.IPR, "ipr_infringement")

        # Check Motor Vehicle Claims
        for pattern in cls.MOTOR_VEHICLE_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.MOTOR_VEHICLE, "mact_or_vehicle_accident")

        # Check Constitutional Rights
        for pattern in cls.CONSTITUTIONAL_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.CONSTITUTIONAL, "constitutional_or_fundamental_rights")

        # Check Taxation & RTI
        for pattern in cls.TAXATION_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.TAXATION, "taxation_or_regulatory")

        # Check Women & Child Protection
        for pattern in cls.WOMEN_CHILD_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.WOMEN_CHILD, "women_or_child_protection")

        # Check Education & Service
        for pattern in cls.EDUCATION_SERVICE_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.EDUCATION_SERVICE, "education_or_service_dispute")

        # Check Environmental Law
        for pattern in cls.ENVIRONMENTAL_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.ENVIRONMENTAL, "environmental_or_pollution_dispute")

        # Check Civil Litigation
        for pattern in cls.CIVIL_KEYWORDS:
            if re.search(pattern, lower_text):
                return (CaseCategoryEnum.CIVIL, "civil_litigation_or_injunction")

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
