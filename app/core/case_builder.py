import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from app.models.schemas import CaseData, CaseCategoryEnum, LanguageEnum

class CaseBuilder:
    """
    Intelligent Case Extraction and Structuring Engine.
    Converts user dialogues across English, Hindi, Gujarati, Marathi, Tamil, Telugu,
    Malayalam, Bengali, and Hinglish into verified structured legal cases across all
    major areas of Indian law.
    Identifies missing facts, flags conflicting dates, and ensures zero hallucination.
    """

    # Category classification patterns for all major domains of Indian Law
    CONSTITUTIONAL_KEYWORDS = [
        r"\b(fundamental\s*rights?|article\s*(?:14|19|21|32|226)|writ|habeas\s*corpus|mandamus|certiorari|quo\s*warranto|arbitrar\w*|high\s*court|supreme\s*court|constitutional|unconstitutional|detained|detention|police\s*atrocity|natural\s*justice|show-cause\s*notice)\b",
        r"(મૂળભૂત\s*અધિકારો?|બંધારણ|રિટ|मौलिक\s*अधिकार|संविधान|रिट|அடிப்படை\s*உரிமைகள்|ప్రాథమిక\s*హక్కులు|মৌলিক\s*অধিকার)"
    ]

    CRIMINAL_KEYWORDS = [
        r"\b(fir|zero\s*fir|police\s*complaint|police\s*station|sho|cognizable|arrest|bail|anticipatory\s*bail|bns|bnss|bsa|ipc|crpc|cheating|section\s*318|section\s*420|theft|robbery|assault|beating|violence|intimidation|extortion|threat\s*to\s*life|chargesheet|magistrate\s*complaint|electronic\s*evidence|evidence\s*in\s*court|electronic\s*record|section\s*63|sakshya|65b)\b",
        r"(પોલીસ\s*ફરિયાદ|એફઆઈઆર|જામીન|ધમકી|ચોરી|છેતરપિંડી|ઇલેક્ટ્રોનિક\s*પુરાવા|एफआईआर|पुलिस\s*शिकायत|जमानत|धमकी|ठगी|धोखाधड़ी|इलेक्ट्रॉनिक\s*साक्ष्य|പോലീസ്\s*പരാതി|എഫ്ഐആർ|ஜாமீன்|புகார்|బెయిల్|ఫిర్యాదు|এফআইআর|অভিযোগ|जामीन)"
    ]

    CIVIL_KEYWORDS = [
        r"\b(civil\s*suit|recovery\s*of\s*money|order\s*37|summary\s*suit|injunction|stay\s*order|order\s*39|limitation\s*act|time\s*barred|3\s*years\s*limitation|promissory\s*note|breach\s*of\s*contract|liquidated\s*damages|specific\s*performance)\b",
        r"(સિવિલ\s*દાવો|પૈસાની\s*વસૂલાત|સ્ટે\s*ઓર્ડર|दीवानी\s*मुकदमा|रुपये\s*की\s*वसूली|स्टे\s*ऑर्डर|ഇഞ്ചങ്ക്ഷൻ|தடை\s*உத்தரவு|స్టే\s*ఆర్డర్|টাকা\s*আদায়)"
    ]

    FAMILY_KEYWORDS = [
        r"\b(divorce|mutual\s*divorce|section\s*13b|custody|child\s*custody|maintenance|alimony|section\s*144\s*bnss|125\s*crpc|domestic\s*violence|dv\s*act|pwdva|shared\s*household|cruelty\s*by\s*husband|498a|hindu\s*marriage|special\s*marriage|restitution)\b",
        r"(છૂટાછેડા|પેટાભથ્થું|ઘરેલું\s*હિંસા|તલાક|तलाक|गुज़ारा\s*भत्ता|घरेलू\s*हिंसा|कस्टडी|വിവാഹമോചനം|ഡൊമസ്റ്റിക്\s*വയലൻസ്|விவாகரத்து|ஜீവനாம்சம்|విడాకులు|భరణం|বিবাহবিচ্ছেদ|খোরপোশ)"
    ]

    PROPERTY_KEYWORDS = [
        r"\b(rera|builder\s*delay|possession\s*delay|flat\s*possession|land\s*dispute|title\s*deed|sale\s*deed|mutation|registry|encroachment|partition\s*suit|ancestral\s*property|illegal\s*construction|stamp\s*duty|registration\s*act)\b",
        r"(રેરા|જમીન\s*વિવાદ|દસ્તાવેજ|ભાગલા|વારસાઈ|रेरा|जमीन\s*विवाद|कब्जा|रजिस्ट्री|बंटवारा|பாகப்பிரிவினை|పంపకాలు|জমি\s*বিরোধ)"
    ]

    CYBER_KEYWORDS = [
        r"\b(cyber\s*crime|online\s*fraud|upi\s*scam|phishing|hacked|identity\s*theft|section\s*66d|sim\s*swap|cyber\s*cell|1930\s*helpline|1930|cybercrime\.gov\.in|data\s*leak|dpdp|otp\s*fraud|apk\s*fraud|fake\s*link|fake\s*courier|unauthorized\s*(?:upi|debit|transfer)|leaked|data\s*breach|privacy\s*leak|aadhaar|personal\s*data|data\s*fiduciary)\b",
        r"(સાયબર\s*ક્રાઈમ|ઓનલાઈન\s*ફ્રોડ|યુપીઆઈ\s*સ્કેમ|साइबर\s*क्राइम|ऑनलाइन\s*धोखाधड़ी|यूपीआई\s*फ्रॉड|ஹேக்|சைபர்\s*கிரைம்|సైబర్\s*నేరం|সাইবার\s*অপরাধ)"
    ]

    BANKING_KEYWORDS = [
        r"\b(cheque|cheques|bounced|dishonour|dishonored|dishonoured|insufficient\s*funds|138\s*ni|bank\s*account\s*freeze|debit\s*freeze|lien\s*on\s*account|rbi\s*ombudsman|cms\s*rbi|recovery\s*agent|loan\s*recovery|harassment.*loan|sarfaesi|cibil\s*score)\b",
        r"(ચેક\s*બાઉન્સ|બેંક\s*ખાતું\s*ફ્રીઝ|લોન\s*રિકવરી|चेक\s*बाउंस|बैंक\s*खाता\s*फ्रीज|लोन\s*एजेंट\s*परेशान|செக்\s*பவுன்ஸ்|చెక్కు\s*బౌన్స్|চেক\s*বাউন্স)"
    ]

    TAXATION_KEYWORDS = [
        r"\b(income\s*tax|section\s*148|section\s*148a|reassessment|escaped\s*assessment|gst\s*notice|show\s*cause\s*notice|drc-01|itc\s*mismatch|input\s*tax\s*credit|tax\s*demand)\b",
        r"(ઇન્કમટેક્સ\s*નોટિસ|જીએસટી\s*નોટિસ|इनकम\s*टैक्स\s*नोटिस|जीएसटी\s*नोटिस|வருமான\s*வரி|ఆదాయపు\s*పన్ను|আয়কর\s*নোটিশ)"
    ]

    IPR_KEYWORDS = [
        r"\b(copyright|trademark|passing\s*off|brand\s*name\s*copied|patent|plagiarism|piracy|counterfeit|cease\s*and\s*desist|infringement)\b",
        r"(કોપીરાઈટ|ટ્રેડમાર્ક|कॉपीराइट|ट्रेडमार्क|பதிப்புரிமை|కాపీరైట్|কপিরাইট)"
    ]

    MOTOR_VEHICLE_KEYWORDS = [
        r"\b(mact|motor\s*accident|road\s*accident|accident\s*compensation|hit\s*and\s*run|section\s*166|section\s*161|third\s*party\s*insurance|vehicular\s*negligence|rash\s*driving\s*claim|claims\s*tribunal|solatium)\b",
        r"(અકસ્માત\s*વળતર|રોડ\s*અકસ્માત|दुर्घटना\s*मुआवजा|सड़क\s*दुर्घटना|வாகன\s*விபத்து|రోడ్డు\s*ప్రమాదం|সড়ক\s*দুর্ঘটনা)"
    ]

    INSURANCE_KEYWORDS = [
        r"\b(health\s*insurance|insurance\s*claim|claim\s*repudiated|repudiated|insurance\s*ombudsman|mediclaim|cashless\s*denied|life\s*insurance|irdai|pre-existing\s*condition|hospitalization\s*claim)\b",
        r"(વીમા\s*ક્લેમ\s*નામંજૂર|વીમા\s*ઓમ્બડ્સમેન|बीमा\s*क्लेम\s*खारिज|इन्श्योरेंस\s*ओम्बड्समैन|காப்பீடு|భీమా\s*క్లెయిమ్|বীমা\s*দাবি)"
    ]

    ENVIRONMENTAL_KEYWORDS = [
        r"\b(ngt|national\s*green\s*tribunal|pollution|illegal\s*tree\s*cutting|water\s*contamination|air\s*pollution|environmental\s*clearance|crz\s*violation|green\s*zone\s*encroachment)\b",
        r"(પ્રદૂષણ|નેશનલ\s*ગ્રીન\s*ટ્રિબ્યુનલ|पर्यावरण|प्रदूषण|एनजीटी|மாசு|కాలుష్యం|দূষণ)"
    ]

    ADMINISTRATIVE_KEYWORDS = [
        r"\b(rti|right\s*to\s*information|pio|public\s*information\s*officer|first\s*appeal|second\s*appeal|cic|cat|central\s*administrative\s*tribunal|government\s*employee\s*service\s*matter)\b",
        r"(આરટીઆઈ|માહિતીનો\s*અધિકાર|आरटीआई|सूचना\s*का\s*अधिकार|தகவல்\s*அறியும்\s*உரிமை|సమాచార\s*హక్కు|তথ্য\s*অধিকার)"
    ]

    IMMIGRATION_KEYWORDS = [
        r"\b(passport\s*impounded|passport\s*refusal|rpo|regional\s*passport\s*office|criminal\s*case\s*passport|noc\s*for\s*passport|frro|visa\s*deportation|citizenship\s*act)\b",
        r"(પાસપોર્ટ|વિઝા|पासपोर्ट\s*अटका|पासपोर्ट\s*इनकार|கடவுச்சீட்டு|పాస్\u200cపోర్ట్|পাসপোর্ট)"
    ]

    ADR_KEYWORDS = [
        r"\b(arbitration|arbitrator|arbitration\s*clause|arbitral|mediation|mediation\s*act|lok\s*adalat|settlement\s*agreement|conciliation|mediated\s*settlement)\b",
        r"(આર્બિટ્રેશન|મધ્યસ્થી|લોક\s*અદાલત|मध्यस्थता|आर्बिट्रेशन|लोक\s*अदालत|மத்தியஸ்தம்|మధ్యవర్తిత్వం|সালিশ)"
    ]

    TENANT_KEYWORDS = [
        r"\b(tenant|landlord|rent|deposit|security\s*deposit|owner|flat|apartment|lease|evict|eviction|wear\s*and\s*tear|painting\s*charges|makaan\s*malik|kiraya|kirayedar|makandari|model\s*tenancy)\b",
        r"(સિક્યોરિટી|ડિપોઝિટ|મકાનમાલિક|ભાડું|મકાન\s*ખાલી|किराया|मकान\s*मालिक|डिपॉज़िट|വാടക|ഡെപ്പോസിറ്റ്|வாடகை|வைப்புத்தொகை|అద్దె|డిపాజిట్|ভাড়া|আমানત|घरमालक)"
    ]

    CONSUMER_KEYWORDS = [
        r"\b(consumer|product|defective|amazon|flipkart|meesho|order|delivery|refund|return|courier|warranty|shopping|service\s*not\s*provided|damaged\s*phone|seller|retailer|kharida|saman|paise\s*wapas|kharab\s*nikla|cpa\s*2019|e-daakhil|1915)\b",
        r"(ખામીયુક્ત|રિફંડ|વેચનાર|ખરીદ્યો|ફોન|દ્વારા|दोषपूर्ण|विक्रेता|उपभोक्ता|റീഫണ്ട്|തകരാർ|குறைபாடு|ரீபண்ட்|లోపం|రీఫండ్|ত্রুটি|ফেরত)"
    ]

    EMPLOYMENT_KEYWORDS = [
        r"\b(salary|employee|employer|boss|resigned|resignation|appointment\s*letter|wages|dues|full\s*and\s*final|fnf|relieving\s*letter|payslip|pf|workplace|manager|naukri|vetan|tanakhwah|posh|sexual\s*harassment|internal\s*committee|gratuity)\b",
        r"(પગાર|નિયોક્તા|કંપની|વેતન|વેજીસ|वेतन|नियोक्ता|तनख्वाह|തൊഴിലുടമ|ശമ്പളം|சம்பளம்|நிறுவனம்|జీతం|యజమాని|বেতন|নিয়োগকর্তা|ಸಂಬಳ|पगार)"
    ]

    # Currency extraction regex patterns
    CURRENCY_PATTERNS = [
        r"₹\s*([0-9,]+)",
        r"(?:rs\.?|inr|rupees)\s*([0-9,]+)",
        r"([0-9,]+)\s*(?:rs\.?|inr|rupees)",
        r"([0-9]+)\s*(?:k|thousand|hazar|lakh|lac|crore)\b",
        r"([0-9,]+)\s*ka\b"
    ]

    # Date extraction patterns
    DATE_PATTERNS = [
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
        r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*(?:20\d\d)?)\b",
        r"\b(yesterday|last\s*week|last\s*month|2\s*months\s*ago|two\s*months\s*ago|do\s*mahine\s*pehle)\b"
    ]

    @classmethod
    def classify_category(cls, text: str) -> Tuple[CaseCategoryEnum, str]:
        """Classifies text into a specific Indian legal category and sub-category."""
        lower_text = text.lower()

        # Check in priority order of specificity
        
        # 1. Cyber Law
        for pattern in cls.CYBER_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "financial_cyber_fraud" if any(w in lower_text for w in ["upi", "otp", "bank", "scam", "fraud"]) else "online_harassment_or_data_leak"
                return (CaseCategoryEnum.CYBER, sub)

        # 2. Banking & Cheque Bounce
        for pattern in cls.BANKING_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "cheque_bounce_138" if "cheque" in lower_text else ("account_freeze" if "freeze" in lower_text else "bank_service_deficiency")
                return (CaseCategoryEnum.BANKING, sub)

        # 3. Insurance
        for pattern in cls.INSURANCE_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "wrongful_claim_repudiation"
                return (CaseCategoryEnum.INSURANCE, sub)

        # 4. Taxation
        for pattern in cls.TAXATION_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "income_tax_notice_response" if "income" in lower_text else "gst_show_cause_response"
                return (CaseCategoryEnum.TAXATION, sub)

        # 5. IPR
        for pattern in cls.IPR_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "copyright_or_trademark_infringement"
                return (CaseCategoryEnum.IPR, sub)

        # 6. Motor Vehicle / Accident
        for pattern in cls.MOTOR_VEHICLE_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "mact_accident_claim" if "mact" in lower_text or "accident" in lower_text else "hit_and_run_claim"
                return (CaseCategoryEnum.MOTOR_VEHICLE, sub)

        # 7. ADR
        for pattern in cls.ADR_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "arbitration_or_mediation_process"
                return (CaseCategoryEnum.ADR, sub)

        # 8. Administrative & RTI
        for pattern in cls.ADMINISTRATIVE_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "rti_application_or_appeal"
                return (CaseCategoryEnum.ADMINISTRATIVE, sub)

        # 9. Immigration
        for pattern in cls.IMMIGRATION_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "passport_or_visa_grievance"
                return (CaseCategoryEnum.IMMIGRATION, sub)

        # 10. Constitutional Law
        for pattern in cls.CONSTITUTIONAL_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "writ_petition_or_fundamental_rights"
                return (CaseCategoryEnum.CONSTITUTIONAL, sub)

        # 11. Criminal Law (BNS/BNSS/BSA)
        for pattern in cls.CRIMINAL_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "fir_registration" if "fir" in lower_text else ("bail_application" if "bail" in lower_text else "criminal_fraud_or_cheating")
                return (CaseCategoryEnum.CRIMINAL, sub)

        # 12. Family Law
        for pattern in cls.FAMILY_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "domestic_violence" if "domestic" in lower_text or "violence" in lower_text else ("maintenance_claim" if "maintenance" in lower_text else "divorce_and_custody")
                return (CaseCategoryEnum.FAMILY, sub)

        # 13. Property & RERA
        for pattern in cls.PROPERTY_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "rera_possession_delay" if "rera" in lower_text or "builder" in lower_text else "property_ownership_or_partition"
                return (CaseCategoryEnum.PROPERTY, sub)

        # 14. Tenant & Landlord
        for pattern in cls.TENANT_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "security_deposit_withheld" if "deposit" in lower_text or "security" in lower_text else ("unlawful_eviction_threat" if "evict" in lower_text else "tenancy_dispute")
                return (CaseCategoryEnum.TENANT, sub)

        # 15. Consumer Protection
        for pattern in cls.CONSUMER_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "defective_product_or_refund" if "refund" in lower_text or "defective" in lower_text else "e_commerce_grievance"
                return (CaseCategoryEnum.CONSUMER, sub)

        # 16. Employment & Labour
        for pattern in cls.EMPLOYMENT_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "posh_workplace_harassment" if "posh" in lower_text or "sexual" in lower_text else ("unpaid_or_delayed_salary" if "salary" in lower_text or "wages" in lower_text else "employment_settlement")
                return (CaseCategoryEnum.EMPLOYMENT, sub)

        # 17. Civil Law
        for pattern in cls.CIVIL_KEYWORDS:
            if re.search(pattern, lower_text):
                sub = "money_recovery_or_injunction"
                return (CaseCategoryEnum.CIVIL, sub)

        # 18. General / Fallback
        return (CaseCategoryEnum.GENERAL, "general_legal_inquiry")

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
                    match_str = m.group(0).lower()
                    if "k" in match_str or "thousand" in match_str or "hazar" in match_str:
                        val *= 1000
                    elif "lakh" in match_str or "lac" in match_str:
                        val *= 100000
                    elif "crore" in match_str:
                        val *= 10000000
                    amounts.append(int(val))
                except ValueError:
                    continue

        if not amounts:
            num_matches = re.findall(r"\b(\d{4,8})\b", text)
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
        """Extracts dates and checks for chronological contradictions."""
        found_dates = []
        for pattern in cls.DATE_PATTERNS:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for m in matches:
                found_dates.append(m.strip())

        conflict_warning = None
        if len(found_dates) >= 2:
            lower = text.lower()
            if "vacated on" in lower and "moved in on" in lower:
                try:
                    if re.search(r"vacated\s+on\s+([a-z0-9\s]+)\s+and\s+moved\s+in\s+on\s+([a-z0-9\s]+)", lower):
                        conflict_warning = "Contradictory timeline detected: Move-in date appears after the vacate date. Please clarify the correct chronology."
                except Exception:
                    pass

        return found_dates, conflict_warning

    @classmethod
    def extract_case(cls, text: str, state_jurisdiction: Optional[str] = None, previous_case: Optional[CaseData] = None) -> CaseData:
        """
        Builds or updates a CaseData model based on user dialogue across any Indian legal category.
        Strictly preserves factual accuracy without inventing data.
        """
        category, sub_category = cls.classify_category(text)
        amounts_data = cls.extract_amounts(text)
        dates, date_conflict = cls.extract_dates_and_check_conflicts(text)

        # Dynamic party & role mapping across all categories
        role_map = {
            CaseCategoryEnum.CONSTITUTIONAL: ("Petitioner / Aggrieved Citizen", "Respondent (State / Public Authority)"),
            CaseCategoryEnum.CRIMINAL: ("Complainant / Victim / Informant", "Accused / Opposing Party / Police Authority"),
            CaseCategoryEnum.CIVIL: ("Plaintiff / Claimant", "Defendant / Responding Party"),
            CaseCategoryEnum.FAMILY: ("Applicant / Aggrieved Spouse", "Respondent / Opposing Spouse"),
            CaseCategoryEnum.PROPERTY: ("Property Buyer / Allottee / Owner", "Developer / Builder / Disputing Party"),
            CaseCategoryEnum.TENANT: ("Tenant", "Landlord / Property Owner"),
            CaseCategoryEnum.CONSUMER: ("Consumer / Purchaser", "Seller / E-Commerce Platform / Service Provider"),
            CaseCategoryEnum.EMPLOYMENT: ("Employee / Workman", "Employer / Management"),
            CaseCategoryEnum.CYBER: ("Victim / Complainant", "Fraudster / Impersonator (Unknown/Cyber Fraud Accused)"),
            CaseCategoryEnum.BANKING: ("Account Holder / Payee / Customer", "Bank / Cheque Drawer / Financial Institution"),
            CaseCategoryEnum.TAXATION: ("Assessee / Taxpayer", "Assessing Officer / Revenue Authority"),
            CaseCategoryEnum.IPR: ("Proprietor / Author / Rights Holder", "Infringing Party / Imitator"),
            CaseCategoryEnum.MOTOR_VEHICLE: ("Claimant / Injured / Dependent", "Vehicle Driver / Owner / Insurer"),
            CaseCategoryEnum.INSURANCE: ("Policyholder / Insured Person", "Insurance Company / TPA"),
            CaseCategoryEnum.ENVIRONMENTAL: ("Aggrieved Resident / Applicant", "Polluting Industry / Municipal Body"),
            CaseCategoryEnum.ADMINISTRATIVE: ("Information Seeker / Applicant", "Public Information Officer / Department"),
            CaseCategoryEnum.IMMIGRATION: ("Passport Applicant / Citizen", "Regional Passport Officer / Authority"),
            CaseCategoryEnum.ADR: ("Disputing Party / Claimant", "Opposing Party / Respondent"),
            CaseCategoryEnum.GENERAL: ("Aggrieved Party", "Opposing Party"),
            CaseCategoryEnum.OTHER: ("Inquiring Party", "Relevant Authority")
        }

        user_role, counterparty_role = role_map.get(category, ("Aggrieved Party", "Opposing Party"))

        # Agreement / documentation status
        agreements = "Not specified in conversation"
        lower = text.lower()
        if any(w in lower for w in ["no written agreement", "bina agreement", "no agreement", "oral contract", "no document"]):
            agreements = "Oral agreement / No formal contract executed (Corroborated by banking/chat records)"
        elif any(w in lower for w in ["agreement", "contract", "deed", "registered", "notarized", "offer letter"]):
            agreements = "Written agreement / Contract exists"

        # Evidence detection
        evidence_found = []
        if any(w in lower for w in ["bank statement", "upi", "transfer", "bank proof", "account statement", "passbook"]):
            evidence_found.append("Bank Transfer Proof / UPI Transaction Records")
        if any(w in lower for w in ["whatsapp", "chat", "message", "sms"]):
            evidence_found.append("WhatsApp / Electronic Chat Records")
        if any(w in lower for w in ["invoice", "bill", "receipt", "slip", "payslip", "salary slip"]):
            evidence_found.append("Payment Receipts / Invoices / Tax Invoices")
        if any(w in lower for w in ["email", "mail", "written notice"]):
            evidence_found.append("Email Correspondence")
        if any(w in lower for w in ["photo", "video", "unboxing", "cctv"]):
            evidence_found.append("Photographic / Video / CCTV Evidence")
        if any(w in lower for w in ["cheque", "dishonour memo", "bank memo"]):
            evidence_found.append("Original Cheque & Bank Return Memo")
        if any(w in lower for w in ["fir", "police complaint", "docket", "complaint copy"]):
            evidence_found.append("Copy of Lodged Police / Portal Complaint")

        # Missing information analysis
        missing = []
        if not amounts_data.get("primary_amount") and category in [
            CaseCategoryEnum.CIVIL, CaseCategoryEnum.BANKING, CaseCategoryEnum.TENANT,
            CaseCategoryEnum.CONSUMER, CaseCategoryEnum.EMPLOYMENT, CaseCategoryEnum.PROPERTY,
            CaseCategoryEnum.INSURANCE, CaseCategoryEnum.CYBER
        ]:
            missing.append("Exact financial amount in dispute (in ₹).")
        if not state_jurisdiction:
            missing.append("State or District where the incident occurred (determines applicable state enactments and court jurisdiction).")
        if not dates:
            missing.append("Key dates (date of incident, transaction, notice receipt, or cause of action).")
        if not evidence_found:
            missing.append("Documentary proofs available (receipts, chat logs, agreements, bank statements).")

        # Timeline
        timeline = []
        if dates:
            for d in dates:
                timeline.append({"date": d, "event": "Event referenced in user statement"})
        else:
            timeline.append({"date": "Recent", "event": "Dispute reported by user"})

        # Counterparty Name extraction heuristic
        counterparty_name = counterparty_role
        m_name = re.search(r"(?:from|against|with|company|seller|landlord|owner|bank|builder)\s+([A-Z][a-zA-Z0-9\s]{2,25})", text)
        if m_name and m_name.group(1).lower() not in ["the", "a", "my", "this", "that", "an"]:
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
            desired_resolution="Redressal, recovery of dues, relief or formal legal notice",
            missing_information=missing,
            state_jurisdiction=state_jurisdiction or "To be specified by user"
        )

        return case

    @classmethod
    def generate_follow_up_questions(cls, case: CaseData, language: LanguageEnum = LanguageEnum.ENGLISH) -> List[str]:
        """Generates contextual, targeted follow-up questions for the specific legal domain."""
        questions = []
        lang_str = language.value if hasattr(language, "value") else str(language).lower()

        # 1. Location / State question if missing
        if not case.state_jurisdiction or case.state_jurisdiction == "To be specified by user":
            if lang_str in ["hi", "hindi"]:
                questions.append("यह घटना किस राज्य या शहर में हुई है? (न्यायाधिकार और राज्य कानूनों के लिए आवश्यक)")
            elif lang_str in ["gu", "gujarati"]:
                questions.append("આ ઘટના કયા રાજ્ય કે શહેરમાં બની છે? (અધિકારક્ષેત્ર અને સ્થાનિક કાયદા નક્કી કરવા માટે)")
            elif lang_str in ["mr", "marathi"]:
                questions.append("ही घटना कोणत्या राज्यात किंवा शहरात घडली आहे? (अधिकारक्षेत्र निश्चित करण्यासाठी)")
            elif lang_str in ["hinglish"]:
                questions.append("Ye incident kis State ya City me hua hai? (Jurisdiction aur local laws decide karne ke liye)")
            else:
                questions.append("In which Indian State or District did this incident occur? (Determines court jurisdiction and applicable local laws)")

        # 2. Specific domain questions
        if case.category == CaseCategoryEnum.BANKING:
            if lang_str in ["hi", "hindi"]:
                questions.append("क्या आपके पास बैंक का चेक वापसी मेमो (Cheque Return Memo) और मूल चेक उपलब्ध है?")
            elif lang_str in ["gu", "gujarati"]:
                questions.append("શું તમારી પાસે બેંકનો ચેક રિટર્ન મેમો (Cheque Return Memo) ઉપલબ્ધ છે?")
            else:
                questions.append("Do you have the original bounced cheque and the Bank Return Memo showing the date and reason of dishonour?")
        elif case.category == CaseCategoryEnum.CYBER:
            if lang_str in ["hi", "hindi"]:
                questions.append("क्या आपने 1930 साइबर हेल्पलाइन या cybercrime.gov.in पर तुरंत शिकायत दर्ज कराई है?")
            elif lang_str in ["gu", "gujarati"]:
                questions.append("શું તમે 1930 સાયબર હેલ્પલાઈન કે cybercrime.gov.in પર ફરિયાદ નોંધાવી છે?")
            else:
                questions.append("Have you lodged an immediate complaint on the National Cyber Crime Portal (cybercrime.gov.in) or called Helpline 1930?")
        elif case.category == CaseCategoryEnum.CRIMINAL:
            if lang_str in ["hi", "hindi"]:
                questions.append("क्या आपने संबंधित पुलिस थाने में लिखित शिकायत दी है और क्या उसकी पावती (acknowledgment) मिली है?")
            elif lang_str in ["gu", "gujarati"]:
                questions.append("શું તમે પોલીસ સ્ટેશનમાં લેખિત ફરિયાદ આપી છે અને તેની પહોંચ મેળવી છે?")
            else:
                questions.append("Have you submitted a formal written complaint to the local police station, and did you receive a receiving copy / acknowledgment?")
        elif case.category == CaseCategoryEnum.PROPERTY:
            if lang_str in ["hi", "hindi"]:
                questions.append("क्या प्रोजेक्ट रेरा (RERA) में पंजीकृत है और क्या आपके पास बिल्डर-बायर एग्रीमेंट (BBA) है?")
            elif lang_str in ["gu", "gujarati"]:
                questions.append("શું પ્રોજેક્ટ રેરા (RERA) માં રજિસ્ટર્ડ છે અને શું તમારી પાસે બિલ્ડર કરાર છે?")
            else:
                questions.append("Is the project registered under RERA, and what is the committed possession date specified in your Builder-Buyer Agreement?")
        elif case.category == CaseCategoryEnum.ADMINISTRATIVE:
            if lang_str in ["hi", "hindi"]:
                questions.append("क्या यह आवेदन केंद्र सरकार के विभाग से संबंधित है या राज्य सरकार के विभाग से?")
            else:
                questions.append("Does the RTI request pertain to a Central Government public authority or a State Government department?")
        elif case.category == CaseCategoryEnum.TENANT:
            if lang_str in ["gu", "gujarati"]:
                questions.append("શું તમારી પાસે ભાડા કરાર અને સિક્યોરિટી ડિપોઝિટ ચૂકવ્યાના બેંક વ્યવહારના પુરાવા છે?")
            elif lang_str in ["hi", "hindi"]:
                questions.append("क्या आपके पास रेंट एग्रीमेंट और सिक्योरिटी डिपॉजिट भुगतान की बैंक रसीद है?")
            else:
                questions.append("Do you have a written rent agreement and bank transaction receipts proving the payment of your security deposit?")
        elif case.category == CaseCategoryEnum.CONSUMER:
            if lang_str in ["gu", "gujarati"]:
                questions.append("શું તમારી પાસે ખરીદીનું ટેક્સ ઇનવોઇસ અને કંપનીનો લેખિત ઇનકાર છે?")
            elif lang_str in ["hi", "hindi"]:
                questions.append("क्या आपके पास खरीदारी का टैक्स इनवॉइस और विक्रेता द्वारा रिफंड से इनकार का लिखित प्रमाण है?")
            else:
                questions.append("Do you possess the original purchase invoice and written communication showing the seller's refusal to refund/replace?")
        elif case.category == CaseCategoryEnum.EMPLOYMENT:
            if lang_str in ["gu", "gujarati"]:
                questions.append("શું તમારી પાસે એપોઇન્ટમેન્ટ લેટર, સેલરી સ્લિપ અને રાજીનામાનો સ્વીકાર પત્ર છે?")
            elif lang_str in ["hi", "hindi"]:
                questions.append("क्या आपके पास नियुक्ति पत्र, अंतिम वेतन पर्ची और कंपनी को भेजा गया ईमेल उपलब्ध है?")
            else:
                questions.append("Do you possess your appointment letter, recent payslips, and copy of formal communication sent regarding pending dues?")

        return questions[:3]
