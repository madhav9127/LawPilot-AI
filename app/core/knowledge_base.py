import re
from typing import List, Dict, Optional, Tuple
from app.models.schemas import LegalCitation, VerificationStatusEnum, CaseCategoryEnum

class LegalKnowledgeBase:
    """
    Verified Indian Statutory Knowledge Base and Anti-Hallucination Retrieval Engine.
    Grounds all legal analysis directly in verified Indian statutes, official portals,
    and established procedural legal frameworks across all major areas of Indian law.
    Prioritizes current criminal statutes (BNS 2023, BNSS 2023, BSA 2023 in force from July 1, 2024).
    """
    
    # Official Government & Judicial Portals
    OFFICIAL_PORTALS = {
        "india_code": "https://www.indiacode.nic.in/",
        "egazette": "https://egazette.gov.in/",
        "sci": "https://www.sci.gov.in/",
        "ecourts": "https://ecourts.gov.in/",
        "doj": "https://doj.gov.in/",
        "lawmin": "https://lawmin.gov.in/",
        "nalsa": "https://nalsa.gov.in/",
        "consumeraffairs": "https://consumeraffairs.nic.in/",
        "consumerhelpline": "https://consumerhelpline.gov.in/",
        "labour": "https://labour.gov.in/",
        "mha": "https://www.mha.gov.in/",
        "rbi": "https://www.rbi.org.in/",
        "irdai": "https://irdai.gov.in/",
        "incometax": "https://incometaxindia.gov.in/",
        "gst": "https://www.gst.gov.in/",
        "meity": "https://www.meity.gov.in/",
        "ipindia": "https://ipindia.gov.in/",
        "moef": "https://moef.gov.in/",
        "greentribunal": "https://greentribunal.gov.in/",
        "mea": "https://www.mea.gov.in/",
        "cybercrime": "https://cybercrime.gov.in/",
        "shram_suvidha": "https://shramsuvidha.gov.in/"
    }

    # Verified Statutory Provisions Database Across All Major Indian Legal Domains
    VERIFIED_STATUTES: List[Dict] = [
        # =========================================================================
        # 1. CONSTITUTIONAL LAW
        # =========================================================================
        {
            "id": "CONST_ART14",
            "act_name": "Constitution of India, 1950",
            "section": "Article 14",
            "title": "Equality before law and equal protection of the laws",
            "category": CaseCategoryEnum.CONSTITUTIONAL,
            "keywords": ["equality", "arbitrary", "discrimination", "article 14", "fundamental rights", "state action", "arbitrariness"],
            "description": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India. Strikes down arbitrary state action.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15240",
            "commencement_date": "1950-01-26",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "relevance_notes": "Cornerstone against arbitrary executive action, unfair government tenders, discriminatory regulations, or state denial of rights."
        },
        {
            "id": "CONST_ART21",
            "act_name": "Constitution of India, 1950",
            "section": "Article 21",
            "title": "Protection of life and personal liberty",
            "category": CaseCategoryEnum.CONSTITUTIONAL,
            "keywords": ["liberty", "personal liberty", "article 21", "life", "privacy", "livelihood", "speedy trial", "police harassment", "unlawful arrest"],
            "description": "No person shall be deprived of his life or personal liberty except according to procedure established by law. Encompasses right to privacy, dignified life, legal aid, and protection against custodial violence.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15240",
            "commencement_date": "1950-01-26",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "relevance_notes": "Primary constitutional defense against unlawful detention, harassment, environmental degradation, and breach of bodily integrity."
        },
        {
            "id": "CONST_ART32_226",
            "act_name": "Constitution of India, 1950",
            "section": "Article 32 & Article 226",
            "title": "Remedies for enforcement of rights - Power to issue Writs (Habeas Corpus, Mandamus, Prohibition, Quo Warranto, Certiorari)",
            "category": CaseCategoryEnum.CONSTITUTIONAL,
            "keywords": ["writ", "article 226", "article 32", "high court writ", "supreme court writ", "habeas corpus", "mandamus", "certiorari", "fundamental rights violation"],
            "description": "Empowers citizens to petition the Supreme Court (Art 32) or High Courts (Art 226) for writs of Habeas Corpus, Mandamus, Prohibition, Quo Warranto, and Certiorari to enforce fundamental and legal rights against authorities.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15240",
            "commencement_date": "1950-01-26",
            "jurisdiction": "Central / High Courts & Supreme Court",
            "is_current": True,
            "relevance_notes": "Article 226 has wider scope than Art 32 as it extends to any legal right against government authorities and statutory bodies."
        },

        # =========================================================================
        # 2. CRIMINAL LAW (CURRENT: BNS 2023, BNSS 2023, BSA 2023)
        # =========================================================================
        {
            "id": "BNSS_2023_SEC173",
            "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
            "section": "Section 173",
            "title": "Information in cognizable cases (First Information Report - FIR & Zero FIR)",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["fir", "zero fir", "police complaint", "section 173", "cognizable", "refuse fir", "sho", "police station", "154 crpc"],
            "description": "Every information relating to the commission of a cognizable offence shall be recorded by the officer in charge of a police station. Mandates Zero FIR (recording irrespective of territorial jurisdiction) and electronic FIR. (Historical Equivalent: Section 154 CrPC, 1973).",
            "official_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNSS_2023.pdf",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "historical_equivalent": "Section 154, Code of Criminal Procedure, 1973 (CrPC)",
            "relevance_notes": "If police refuse to register FIR under Sec 173(1), informant can send substance in writing to Superintendent of Police under Sec 173(4) or approach Magistrate under Sec 175(3)."
        },
        {
            "id": "BNSS_2023_SEC479_482",
            "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
            "section": "Section 479 & Section 482",
            "title": "Bail provisions, Maximum period of detention for undertrials, and Anticipatory Bail",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["bail", "anticipatory bail", "arrest", "regular bail", "section 482 bnss", "undertrial", "438 crpc", "437 crpc"],
            "description": "Governs grant of bail in bailable and non-bailable offences. Section 482 provides for direction for grant of bail to persons apprehending arrest (Anticipatory Bail) before High Court or Court of Session. Section 479 liberalises undertrial detention. (Historical Equivalent: Sections 436, 437, 438 CrPC, 1973).",
            "official_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNSS_2023.pdf",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "historical_equivalent": "Sections 436, 437, 438, Code of Criminal Procedure, 1973 (CrPC)",
            "relevance_notes": "Operative criminal procedure code in force from 1 July 2024. Former CrPC provisions apply only to investigations/trials instituted prior to that date."
        },
        {
            "id": "BNS_2023_SEC318",
            "act_name": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
            "section": "Section 318",
            "title": "Cheating and dishonestly inducing delivery of property",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["cheating", "fraud", "scam", "deception", "420 ipc", "section 318 bns", "dishonest inducement", "money cheated"],
            "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property, or to make, alter or destroy the whole or any part of a valuable security, shall be punished with imprisonment up to 7 years and fine. (Historical Equivalent: Section 420, Indian Penal Code, 1860).",
            "official_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNS_2023.pdf",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "historical_equivalent": "Section 415 & 420, Indian Penal Code, 1860 (IPC)",
            "relevance_notes": "Primary substantive offence for financial fraud, business deception, and fraudulent misrepresentation occurring on or after 1 July 2024."
        },
        {
            "id": "BNS_2023_SEC316_303",
            "act_name": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
            "section": "Section 316 & Section 303",
            "title": "Criminal breach of trust and Theft",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["criminal breach of trust", "entrustment", "misappropriation", "theft", "406 ipc", "379 ipc", "section 316 bns"],
            "description": "Section 316 penalizes criminal breach of trust (dishonest misappropriation of entrusted property) with imprisonment up to 5 years or fine. Section 303 penalizes theft. (Historical Equivalent: Sections 405/406 and 378/379 IPC, 1860).",
            "official_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNS_2023.pdf",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "historical_equivalent": "Sections 405/406 & 378/379, Indian Penal Code, 1860 (IPC)",
            "relevance_notes": "Applicable when money, company assets, security deposits, or jewelry entrusted to an agent/partner/bailee is dishonestly converted."
        },
        {
            "id": "BNS_2023_SEC351",
            "act_name": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
            "section": "Section 351",
            "title": "Criminal intimidation",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["threat", "intimidation", "blackmail", "extortion threat", "whatsapp threat", "506 ipc", "section 351 bns"],
            "description": "Whoever threatens another with any injury to his person, reputation or property, with intent to cause alarm to that person, commits criminal intimidation. (Historical Equivalent: Section 503 & 506, Indian Penal Code, 1860).",
            "official_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNS_2023.pdf",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "historical_equivalent": "Sections 503 & 506, Indian Penal Code, 1860 (IPC)",
            "relevance_notes": "Direct legal provision when landlords, loan recovery agents, or abusive counterparties issue threats of violence or social defaming."
        },
        {
            "id": "BSA_2023_SEC61_63",
            "act_name": "Bharatiya Sakshya Adhiniyam, 2023 (BSA)",
            "section": "Section 61 & Section 63",
            "title": "Admissibility of electronic or digital records and Certificate requirement",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["electronic evidence", "whatsapp proof", "email proof", "certificate", "65b evidence act", "section 63 bsa", "call recording", "screenshot"],
            "description": "Recognizes electronic or digital records as valid admissible evidence. Outlines conditions for admissibility of digital records (printouts, CDs, phone memory, emails, chat logs) and certificate under the Schedule to BSA. (Historical Equivalent: Section 65B, Indian Evidence Act, 1872).",
            "official_url": "https://www.mha.gov.in/sites/default/files/2023-12/BSA_2023.pdf",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "historical_equivalent": "Section 65B, Indian Evidence Act, 1872 (IEA)",
            "relevance_notes": "Essential for relying on WhatsApp chats, audio recordings, CCTV footage, and digital receipts in court."
        },

        # =========================================================================
        # 3. CIVIL LAW & PROCEDURE
        # =========================================================================
        {
            "id": "CPC_ORDER37",
            "act_name": "The Code of Civil Procedure, 1908 (CPC)",
            "section": "Order XXXVII (Order 37)",
            "title": "Summary Procedure on negotiable instruments, debts, and liquidated demands",
            "category": CaseCategoryEnum.CIVIL,
            "keywords": ["summary suit", "order 37 cpc", "money recovery", "liquidated demand", "promissory note", "debt recovery", "civil suit"],
            "description": "Provides a fast-track summary suit procedure where the defendant is not entitled to defend as a matter of right unless they obtain leave from the court upon demonstrating a substantial defence. Applies to bills of exchange, cheques, contracts with liquidated amounts.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2191",
            "commencement_date": "1909-01-01",
            "jurisdiction": "Central / Civil Courts",
            "is_current": True,
            "relevance_notes": "Most effective civil remedy for recovering documented financial debts, unpaid loan amounts, or fixed contractual sums without protracted trial."
        },
        {
            "id": "CPC_ORDER39",
            "act_name": "The Code of Civil Procedure, 1908 (CPC)",
            "section": "Order XXXIX, Rules 1 & 2 (Order 39)",
            "title": "Temporary injunctions and interlocutory orders (Stay Order)",
            "category": CaseCategoryEnum.CIVIL,
            "keywords": ["stay order", "injunction", "temporary injunction", "order 39", "restraining order", "status quo", "dispossession stay"],
            "description": "Courts may grant temporary injunction to restrain property being wasted, damaged, alienated, or to restrain unlawful dispossession, upon establishing prima facie case, balance of convenience, and irreparable injury.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2191",
            "commencement_date": "1909-01-01",
            "jurisdiction": "Central / Civil Courts",
            "is_current": True,
            "relevance_notes": "Vital emergency civil relief to preserve status quo, prevent unlawful demolition, stop unauthorized sale, or stay illegal termination."
        },
        {
            "id": "LIMITATION_1963",
            "act_name": "The Limitation Act, 1963",
            "section": "Section 3 & Schedule (Articles 19, 22, 55, 65, 113)",
            "title": "Bar of Limitation and prescribed periods for civil suits",
            "category": CaseCategoryEnum.CIVIL,
            "keywords": ["limitation", "time limit", "3 years", "time barred", "limitation act", "debt limitation", "delay"],
            "description": "Mandates that subject to provisions of sections 4 to 24, every suit instituted after the prescribed period shall be dismissed. General limitation for recovery of money, unpaid salary, or breach of contract is 3 years from the date cause of action arises.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1566",
            "commencement_date": "1964-01-01",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "relevance_notes": "Critical threshold check: failure to initiate proceedings within 3 years bars civil judicial remedy."
        },
        {
            "id": "SRA_1963_SEC6_38",
            "act_name": "The Specific Relief Act, 1963",
            "section": "Section 6 & Section 38",
            "title": "Suit by person dispossessed of immovable property & Perpetual Injunction",
            "category": CaseCategoryEnum.CIVIL,
            "keywords": ["dispossession", "forceful eviction", "section 6 specific relief", "injunction", "perpetual injunction", "peaceful possession"],
            "description": "Section 6 provides summary recovery of possession within 6 months if dispossessed without consent otherwise than in due course of law. Section 38 provides for perpetual injunction to prevent breach of an obligation.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1583",
            "commencement_date": "1964-03-01",
            "jurisdiction": "Central / Civil Courts",
            "is_current": True,
            "relevance_notes": "Protects settled occupants against physical throwing out or illegal padlocking without lawful decree."
        },

        # =========================================================================
        # 4. FAMILY LAW
        # =========================================================================
        {
            "id": "PWDVA_2005_SEC12",
            "act_name": "Protection of Women from Domestic Violence Act, 2005 (PWDVA)",
            "section": "Section 12, Section 18, Section 19 & Section 20",
            "title": "Application to Magistrate for Protection orders, Residence orders, and Monetary relief",
            "category": CaseCategoryEnum.FAMILY,
            "keywords": ["domestic violence", "dv act", "pwdva", "protection order", "residence order", "maintenance", "cruelty", "shared household", "498a"],
            "description": "An aggrieved woman or Protection Officer may apply to a Judicial Magistrate for reliefs including Protection Orders (Sec 18), Residence in shared household (Sec 19), Monetary relief for expenses and loss of earnings (Sec 20), and temporary custody (Sec 21).",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
            "commencement_date": "2006-10-26",
            "jurisdiction": "Central / Magistrate Courts",
            "is_current": True,
            "relevance_notes": "Speedy civil-criminal hybrid protection for women facing physical, verbal, emotional, sexual, or economic domestic abuse."
        },
        {
            "id": "HMA_1955_SEC13",
            "act_name": "The Hindu Marriage Act, 1955",
            "section": "Section 13, Section 13B & Section 24",
            "title": "Divorce, Divorce by Mutual Consent, and Maintenance Pendente Lite",
            "category": CaseCategoryEnum.FAMILY,
            "keywords": ["divorce", "mutual consent divorce", "13b hma", "cruelty", "desertion", "alimony", "interim maintenance", "section 24"],
            "description": "Section 13 specifies fault grounds (cruelty, desertion, adultery). Section 13B provides divorce by mutual consent upon 1 year separation. Section 24 provides interim maintenance and expenses of proceedings to a spouse with insufficient independent income.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1560",
            "commencement_date": "1955-05-18",
            "jurisdiction": "Central / Family Courts",
            "is_current": True,
            "relevance_notes": "Governs marriage, separation, and maintenance disputes among Hindus, Buddhists, Jains, and Sikhs."
        },
        {
            "id": "BNSS_2023_SEC144",
            "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
            "section": "Section 144",
            "title": "Order for maintenance of wives, children and parents",
            "category": CaseCategoryEnum.FAMILY,
            "keywords": ["maintenance", "125 crpc", "section 144 bnss", "child support", "wife maintenance", "parents maintenance", "interim maintenance"],
            "description": "Empowers a Magistrate of the first class to order monthly maintenance for wife, legitimate or illegitimate minor children, and elderly parents unable to maintain themselves, from any person having sufficient means who neglects or refuses to maintain them. (Historical Equivalent: Section 125, Code of Criminal Procedure, 1973).",
            "official_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNSS_2023.pdf",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central / Family & Magistrate Courts",
            "is_current": True,
            "historical_equivalent": "Section 125, Code of Criminal Procedure, 1973 (CrPC)",
            "relevance_notes": "Universal statutory maintenance remedy regardless of personal religion, applicable swiftly through summary inquiry."
        },
        {
            "id": "SMA_1954_SEC27_28",
            "act_name": "The Special Marriage Act, 1954",
            "section": "Section 27 & Section 28",
            "title": "Divorce and Divorce by mutual consent in civil marriages",
            "category": CaseCategoryEnum.FAMILY,
            "keywords": ["special marriage act", "court marriage", "interfaith marriage", "mutual divorce", "civil marriage divorce"],
            "description": "Governs solemnization and dissolution of civil marriages between any two persons irrespective of faith. Section 28 provides mutual consent divorce after 1 year living separately.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1387",
            "commencement_date": "1955-01-01",
            "jurisdiction": "Central / Family Courts",
            "is_current": True,
            "relevance_notes": "Applicable to court marriages, inter-religious, inter-caste, or secular marriages registered under SMA."
        },

        # =========================================================================
        # 5. PROPERTY & REAL ESTATE (RERA, OWNERSHIP, LAND, TENANCY)
        # =========================================================================
        {
            "id": "RERA_2016_SEC18",
            "act_name": "Real Estate (Regulation and Development) Act, 2016 (RERA)",
            "section": "Section 18 & Section 31",
            "title": "Return of amount and compensation for builder delay in handing over possession",
            "category": CaseCategoryEnum.PROPERTY,
            "keywords": ["rera", "builder delay", "possession delay", "flat possession", "rera complaint", "interest on refund", "builder buyer agreement"],
            "description": "If the promoter fails to complete or give possession of an apartment, plot or building in accordance with terms of agreement for sale, he shall be liable on demand to return the amount received with interest (SBI highest MCLR + 2%) or pay monthly delay interest.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2158",
            "commencement_date": "2016-05-01",
            "jurisdiction": "Central / State RERA Authorities",
            "is_current": True,
            "relevance_notes": "Most potent remedy for homebuyers against errant real estate developers for delayed project completion."
        },
        {
            "id": "TPA_1882_SEC106_108",
            "act_name": "The Transfer of Property Act, 1882",
            "section": "Section 106 & Section 108",
            "title": "Duration of leases, notice period, and reasonable wear and tear obligations",
            "category": CaseCategoryEnum.PROPERTY,
            "keywords": ["tenancy", "rent", "security deposit", "notice period", "wear and tear", "painting deduction", "landlord", "eviction"],
            "description": "Section 106 provides 15 days notice for month-to-month leases. Section 108(m) establishes tenant duty to restore premises subject only to reasonable wear and tear, barring arbitrary painting or weathering deductions.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
            "commencement_date": "1882-07-01",
            "jurisdiction": "Central",
            "is_current": True,
            "relevance_notes": "Baseline law governing landlord-tenant rights where state rent control enactments do not prescribe otherwise."
        },
        {
            "id": "REGISTRATION_1908_SEC17_49",
            "act_name": "The Registration Act, 1908",
            "section": "Section 17 & Section 49",
            "title": "Documents of which registration is compulsory and effect of non-registration",
            "category": CaseCategoryEnum.PROPERTY,
            "keywords": ["registration", "registered sale deed", "unregistered agreement", "11 month agreement", "notary agreement", "stamp duty"],
            "description": "Leases of immovable property from year to year or exceeding one year, and transfers of title/interest exceeding ₹100, must be registered. Unregistered documents cannot affect immovable property or be received as evidence of transaction, though admissible as evidence of collateral transaction.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1388",
            "commencement_date": "1909-01-01",
            "jurisdiction": "Central",
            "is_current": True,
            "relevance_notes": "Explains why 11-month lease agreements are executed (to avoid compulsory registration under Sec 17(1)(d))."
        },
        {
            "id": "MTA_2021_SEC11",
            "act_name": "Model Tenancy Act, 2021 (Guidelines & State Enactments)",
            "section": "Section 11 & Section 13",
            "title": "Cap on Security Deposit and Condition for Deductions",
            "category": CaseCategoryEnum.PROPERTY,
            "keywords": ["security deposit", "deposit refund", "maximum deposit", "deduction", "handover", "mta 2021"],
            "description": "Limits security deposit for residential premises to a maximum of two months' rent. Requires refund of security deposit to the tenant at the time of taking over vacant possession of the premises, after making valid deductions agreed under the tenancy agreement.",
            "official_url": "https://mohua.gov.in/upload/uploadfiles/files/Model_Tenancy_Act_English.pdf",
            "commencement_date": "2021-06-02",
            "jurisdiction": "Model Central Act (Adopted by States such as AP, TN, UP)",
            "is_current": True,
            "relevance_notes": "Statutory benchmark used by Rent Authorities and civil courts regarding fair return of security deposit."
        },

        # =========================================================================
        # 6. CONSUMER PROTECTION
        # =========================================================================
        {
            "id": "CPA_2019_SEC2_7",
            "act_name": "The Consumer Protection Act, 2019",
            "section": "Section 2(7)",
            "title": "Definition of Consumer (Including E-commerce and Offline Purchases)",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["consumer", "buyer", "online purchase", "flipkart", "amazon", "e-commerce", "offline store", "cpa 2019"],
            "description": "Defines a consumer as any person who buys goods or hires/avails any services for a consideration paid or promised, including offline or online transactions through electronic means or by teleshopping or direct selling.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
            "commencement_date": "2020-07-20",
            "jurisdiction": "Central",
            "is_current": True,
            "relevance_notes": "Confirms legal standing to seek redressal for online shopping, apps, and digital services."
        },
        {
            "id": "CPA_2019_SEC2_47",
            "act_name": "The Consumer Protection Act, 2019",
            "section": "Section 2(47)",
            "title": "Unfair Trade Practice and Refusal to Take Back Defective Goods or Refund",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["refund", "defective", "unfair trade practice", "refusal", "wrong item", "different product", "replacement"],
            "description": "Refusing to take back or withdraw defective goods or to withdraw or discontinue deficient services and to refund the consideration contemplated within the period stipulated, or within 30 days if no period is stipulated, constitutes an unfair trade practice.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
            "commencement_date": "2020-07-20",
            "jurisdiction": "Central",
            "is_current": True,
            "relevance_notes": "Direct legal basis for mandating refund/replacement for defective smartphones, electronics, or wrong deliveries."
        },
        {
            "id": "CPA_2019_SEC35_38",
            "act_name": "The Consumer Protection Act, 2019",
            "section": "Section 35 & Section 38",
            "title": "Procedure before District Commission & Online e-Daakhil Filing",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["consumer court", "district commission", "file complaint", "edaakhil", "e-daakhil", "pecuniary jurisdiction"],
            "description": "Authorizes consumers to file complaints before the District Consumer Commission directly or through the e-Daakhil portal (edaakhil.nic.in) without requiring advocate representation up to ₹50 Lakhs (as revised by rules).",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
            "commencement_date": "2020-07-20",
            "jurisdiction": "Central / District Commissions",
            "is_current": True,
            "relevance_notes": "Enables citizen self-representation and online tracking of consumer grievances."
        },
        {
            "id": "CPA_ECOM_2020",
            "act_name": "Consumer Protection (E-Commerce) Rules, 2020",
            "section": "Rule 4 & Rule 6",
            "title": "Duties of E-Commerce Entities & Grievance Redressal Mechanism",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["ecommerce rules", "grievance officer", "48 hours", "1 month", "marketplace liability", "refund timeline"],
            "description": "Every e-commerce entity shall establish an adequate grievance redressal mechanism and appoint a Grievance Officer whose details are displayed on its platform. The officer must acknowledge receipt within 48 hours and redress the complaint within one month.",
            "official_url": "https://consumeraffairs.nic.in/sites/default/files/E-commerce%20Rules.pdf",
            "commencement_date": "2020-07-23",
            "jurisdiction": "Central",
            "is_current": True,
            "relevance_notes": "Mandates platforms to resolve delivery failures and refund delays systematically."
        },

        # =========================================================================
        # 7. EMPLOYMENT & LABOUR LAW
        # =========================================================================
        {
            "id": "PWA_1936_SEC5_15",
            "act_name": "The Payment of Wages Act, 1936",
            "section": "Section 5 & Section 15",
            "title": "Time of payment of wages and Claims arising out of deductions from wages or delay in payment",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["unpaid salary", "delayed salary", "wages", "7th day", "10th day", "salary dues", "claim"],
            "description": "Wages must be paid before the expiry of the 7th day after the wage period (or 10th day if more than 1,000 persons employed). Section 15 provides for application to the designated Authority for delayed wages with compensation up to ten times the amount deducted/delayed.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2405",
            "commencement_date": "1937-03-28",
            "jurisdiction": "Central",
            "is_current": True,
            "relevance_notes": "Applies to employees/workers within statutory wage limits; establishes strict statutory timetable for salary."
        },
        {
            "id": "PWA_1936_SEC7",
            "act_name": "The Payment of Wages Act, 1936",
            "section": "Section 7",
            "title": "Deductions which may be made from wages",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["unexplained deduction", "deductions", "penalty", "fines", "final settlement", "withheld"],
            "description": "Strictly enumerates permissible deductions (such as authorized provident fund, income tax, or willful damage shown after formal inquiry). Any arbitrary or unauthorized deduction is unlawful.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2405",
            "commencement_date": "1937-03-28",
            "jurisdiction": "Central",
            "is_current": True,
            "relevance_notes": "Protects against mysterious deductions from final settlement / full and final (FnF) statement."
        },
        {
            "id": "POSH_2013_SEC4_9",
            "act_name": "Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013 (POSH)",
            "section": "Section 4 & Section 9",
            "title": "Constitution of Internal Committee (IC) and Complaint of sexual harassment",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["posh", "sexual harassment", "workplace harassment", "internal committee", "ic complaint", "hostile work environment", "posh act"],
            "description": "Mandates every workplace employing 10 or more employees to constitute an Internal Committee (IC) headed by a senior woman employee. An aggrieved woman may make a written complaint within 3 months (extendable by 3 months). Inquiries must be completed within 90 days.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2104",
            "commencement_date": "2013-12-09",
            "jurisdiction": "Central / All Workplaces",
            "is_current": True,
            "relevance_notes": "Statutory safeguard for women employees in formal and informal, private and public sectors."
        },
        {
            "id": "GRATUITY_1972_SEC4_7",
            "act_name": "The Payment of Gratuity Act, 1972",
            "section": "Section 4 & Section 7",
            "title": "Payment of Gratuity on termination of employment and 30-day payout timeline",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["gratuity", "5 years service", "gratuity calculation", "delayed gratuity", "controlling authority", "gratuity interest"],
            "description": "Gratuity is payable to an employee on separation after rendering continuous service for not less than 5 years. Employer must determine and pay gratuity within 30 days, failing which compound interest is payable under Section 7(3A).",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1483",
            "commencement_date": "1972-09-16",
            "jurisdiction": "Central",
            "is_current": True,
            "relevance_notes": "Protects retired, resigned, or retrenched employees against arbitrary withholding of retirement gratuity."
        },
        {
            "id": "IDA_1947_SEC33C",
            "act_name": "The Industrial Disputes Act, 1947",
            "section": "Section 33C(2)",
            "title": "Recovery of money due from an employer",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["recovery of dues", "labour court", "dues", "33C", "workman", "back wages"],
            "description": "Where any workman is entitled to receive from the employer any money or any benefit which is capable of being computed in terms of money, the workman may apply to the Labour Court for recovery.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/11043",
            "commencement_date": "1947-04-01",
            "jurisdiction": "Central / Labour Courts",
            "is_current": True,
            "relevance_notes": "Statutory recovery forum for employees classified as workmen."
        },

        # =========================================================================
        # 8. CYBER LAW & DIGITAL PERSONAL DATA
        # =========================================================================
        {
            "id": "IT_ACT_2000_SEC66C_66D",
            "act_name": "The Information Technology Act, 2000",
            "section": "Section 66C & Section 66D",
            "title": "Identity theft and Cheating by personation using computer resource (Online Fraud)",
            "category": CaseCategoryEnum.CYBER,
            "keywords": ["cyber crime", "online fraud", "upi scam", "identity theft", "phishing", "66d it act", "impersonation", "hacked", "cyber fraud"],
            "description": "Section 66C penalizes fraudulent use of electronic signature, password or unique identification feature. Section 66D penalizes cheating by personation by using computer resource/communication device with imprisonment up to 3 years and fine up to ₹1 Lakh.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
            "commencement_date": "2000-10-17",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "relevance_notes": "Primary cyber law provision for reporting financial cyber fraud to National Cyber Crime Portal (1930 Helpline)."
        },
        {
            "id": "IT_ACT_2000_SEC43A",
            "act_name": "The Information Technology Act, 2000",
            "section": "Section 43A",
            "title": "Compensation for failure to protect sensitive personal data or information",
            "category": CaseCategoryEnum.CYBER,
            "keywords": ["data breach", "privacy leak", "sensitive data", "negligence", "data security", "compensation for data leak"],
            "description": "Where a body corporate possessing, dealing or handling any sensitive personal data or information is negligent in implementing reasonable security practices, causing wrongful loss or wrongful gain, it is liable to pay damages by way of compensation to the person affected.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
            "commencement_date": "2000-10-17",
            "jurisdiction": "Central / IT Adjudicating Officers",
            "is_current": True,
            "relevance_notes": "Enables victims of corporate data breaches and unauthorized leaks to claim compensation before State IT Secretary/Adjudicating Officer."
        },
        {
            "id": "DPDP_ACT_2023_SEC6_8",
            "act_name": "Digital Personal Data Protection Act, 2023 (DPDP)",
            "section": "Section 6, Section 8 & Section 11",
            "title": "Consent requirements, General obligations of Data Fiduciaries, and Right to Grievance Redressal",
            "category": CaseCategoryEnum.CYBER,
            "keywords": ["dpdp", "data protection", "digital personal data", "data fiduciary", "privacy rights", "consent withdrawal"],
            "description": "Lays down modern statutory framework for processing digital personal data. Mandates free, specific, informed, unconditional and unambiguous consent. Establishes Data Principal rights to access, correction, erasure, and grievance redressal before Data Protection Board of India.",
            "official_url": "https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf",
            "commencement_date": "2023-08-11",
            "jurisdiction": "Central",
            "is_current": True,
            "relevance_notes": "Enacted framework governing personal data rights in the digital ecosystem; progressive implementation."
        },

        # =========================================================================
        # 9. BANKING & FINANCIAL LAW
        # =========================================================================
        {
            "id": "NI_ACT_1881_SEC138",
            "act_name": "The Negotiable Instruments Act, 1881",
            "section": "Section 138, Section 141 & Section 142",
            "title": "Dishonour of cheque for insufficiency of funds in the account (Cheque Bounce)",
            "category": CaseCategoryEnum.BANKING,
            "keywords": ["cheque", "cheques", "bounced", "dishonour", "dishonoured", "funds insufficient", "cheque bounce", "138 ni act", "bounced cheque", "insufficient funds", "statutory demand notice", "15 days notice", "cheque dishonour"],
            "description": "Dishonour of a cheque for insufficiency of funds or exceeding arrangement is a criminal offence punishable with imprisonment up to 2 years or fine up to twice the cheque amount. Prerequisites: Cheque presented within 3 months, statutory demand notice sent within 30 days of memo, drawer fails to pay within 15 days.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2189",
            "commencement_date": "1882-03-01",
            "jurisdiction": "Central / Magistrate Courts",
            "is_current": True,
            "relevance_notes": "Strict statutory timelines: Complaint must be filed before Judicial Magistrate within 1 month after expiry of the 15-day notice window."
        },
        {
            "id": "BNSS_2023_SEC107_FREEZE",
            "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
            "section": "Section 107",
            "title": "Power of police officer to seize or freeze bank accounts linked to suspected offences",
            "category": CaseCategoryEnum.BANKING,
            "keywords": ["bank account freeze", "debit freeze", "lien", "account frozen", "police freeze", "cyber freeze", "102 crpc", "section 107 bnss"],
            "description": "Governs seizure and attachment of property including freezing bank accounts suspected of connection with an offence. Requires immediate reporting of seizure to Magistrate. Victims of arbitrary freezes may petition Magistrate or High Court under Section 528 BNSS / Art 226 for de-freezing. (Historical Equivalent: Section 102 CrPC, 1973).",
            "official_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNSS_2023.pdf",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "historical_equivalent": "Section 102, Code of Criminal Procedure, 1973 (CrPC)",
            "relevance_notes": "Essential for innocent citizens whose UPI/bank accounts get frozen due to third-party cyber fraud chain transactions."
        },
        {
            "id": "RBI_OMBUDSMAN_2021",
            "act_name": "Reserve Bank - Integrated Ombudsman Scheme, 2021",
            "section": "Clause 8 & Clause 10",
            "title": "Grounds of complaint against Regulated Entities (Banks, NBFCs, Payment System Participants)",
            "category": CaseCategoryEnum.BANKING,
            "keywords": ["rbi ombudsman", "bank complaint", "loan harassment", "recovery agent", "unauthorized transaction", "cms rbi", "atm fraud"],
            "description": "Provides free cost-effective single-window grievance redressal against deficiency in service by banks and NBFCs, including unauthorized electronic banking transactions, abusive loan recovery agent behavior, wrongful credit score reporting, and delay in returning security documents.",
            "official_url": "https://cms.rbi.org.in/",
            "commencement_date": "2021-11-12",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "relevance_notes": "Citizens can file online via RBI CMS portal (cms.rbi.org.in) after 30 days of unaddressed complaint to bank."
        },

        # =========================================================================
        # 10. TAXATION LAW (INCOME TAX & GST)
        # =========================================================================
        {
            "id": "ITA_1961_SEC148_148A",
            "act_name": "The Income-tax Act, 1961",
            "section": "Section 148 & Section 148A",
            "title": "Notice where income has escaped assessment and Conducting inquiry before notice",
            "category": CaseCategoryEnum.TAXATION,
            "keywords": ["income tax notice", "section 148", "section 148a", "escaped assessment", "reassessment", "tax demand", "show cause notice it"],
            "description": "Before issuing a reassessment notice under Section 148, the Assessing Officer must conduct inquiry and provide an opportunity of being heard to the assessee under Section 148A by serving a show cause notice with information suggesting income escaped assessment.",
            "official_url": "https://www.incometaxindia.gov.in/pages/acts/income-tax-act.aspx",
            "commencement_date": "1962-04-01",
            "jurisdiction": "Central / Income Tax Department",
            "is_current": True,
            "relevance_notes": "Protects taxpayers against arbitrary reopening of past assessment years without substantive tangible material."
        },
        {
            "id": "CGST_2017_SEC73_74",
            "act_name": "The Central Goods and Services Tax Act, 2017 (CGST)",
            "section": "Section 73 & Section 74",
            "title": "Determination of tax not paid, short paid, erroneously refunded, or ITC wrongly availed",
            "category": CaseCategoryEnum.TAXATION,
            "keywords": ["gst notice", "gst show cause", "itc mismatch", "section 73 cgst", "section 74 cgst", "drc-01", "gst demand"],
            "description": "Section 73 governs determination of tax in non-fraud cases; Section 74 applies where reason involves fraud, willful misstatement or suppression of facts. Department must issue DRC-01 show cause notice detailing grounds and grant hearing opportunity.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2202",
            "commencement_date": "2017-07-01",
            "jurisdiction": "Central / GST Authorities",
            "is_current": True,
            "relevance_notes": "Key procedural safeguard for business owners responding to GST demand notices or Input Tax Credit (ITC) audits."
        },

        # =========================================================================
        # 11. INTELLECTUAL PROPERTY LAW (IPR)
        # =========================================================================
        {
            "id": "COPYRIGHT_1957_SEC51_55",
            "act_name": "The Copyright Act, 1957",
            "section": "Section 51 & Section 55",
            "title": "Infringement of copyright and Civil remedies (Injunction, Damages, Accounts of Profits)",
            "category": CaseCategoryEnum.IPR,
            "keywords": ["copyright", "copyright infringement", "plagiarism", "stolen content", "infringing work", "cease and desist", "copyright notice"],
            "description": "Specifies when copyright is infringed. Section 55 entitles owner of copyright to all remedies by way of injunction, damages, and accounts of profits as conferred by law for infringement of a right.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1367",
            "commencement_date": "1958-01-21",
            "jurisdiction": "Central / Commercial Courts",
            "is_current": True,
            "relevance_notes": "Governs literary, musical, dramatic, artistic, cinematograph film and software code protection."
        },
        {
            "id": "TRADEMARK_1999_SEC29_134",
            "act_name": "The Trade Marks Act, 1999",
            "section": "Section 29 & Section 134",
            "title": "Infringement of registered trade marks and Jurisdiction for filing suit",
            "category": CaseCategoryEnum.IPR,
            "keywords": ["trademark", "trademark infringement", "passing off", "brand name copied", "counterfeit", "commercial suit trademark"],
            "description": "A registered trade mark is infringed by unauthorized use of an identical or deceptively similar mark in relation to identical/similar goods or services. Section 134 allows plaintiff to institute suit where plaintiff actually and voluntarily resides or carries on business.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1993",
            "commencement_date": "2003-09-15",
            "jurisdiction": "Central / District & Commercial Courts",
            "is_current": True,
            "relevance_notes": "Protects brand logos, trade names, business marks against imitation and consumer deception."
        },

        # =========================================================================
        # 12. MOTOR VEHICLE & ACCIDENT CLAIMS
        # =========================================================================
        {
            "id": "MV_ACT_1988_SEC166",
            "act_name": "The Motor Vehicles Act, 1988 (as amended in 2019)",
            "section": "Section 166 & Section 168",
            "title": "Application for compensation before Motor Accidents Claims Tribunal (MACT)",
            "category": CaseCategoryEnum.MOTOR_VEHICLE,
            "keywords": ["road accident", "mact", "accident claim", "motor vehicle accident", "compensation", "death accident", "injury compensation"],
            "description": "An application for compensation arising out of an accident of the nature specified in Section 165 may be made by the person sustaining injury, owner of property, or legal representatives of deceased before MACT having jurisdiction over accident spot or claimants residence.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
            "commencement_date": "1989-07-01",
            "jurisdiction": "Central / MACT Tribunals",
            "is_current": True,
            "relevance_notes": "2019 amendment introduces 6-month limitation under Sec 166(3) for filing accident claim from date of accident."
        },
        {
            "id": "MV_ACT_1988_SEC161",
            "act_name": "The Motor Vehicles Act, 1988 (as amended in 2019)",
            "section": "Section 161",
            "title": "Special provisions as to compensation in case of hit and run motor accident",
            "category": CaseCategoryEnum.MOTOR_VEHICLE,
            "keywords": ["hit and run", "unknown vehicle", "solatium fund", "hit and run compensation", "scheme for compensation"],
            "description": "Provides statutory compensation in respect of death or grievous hurt to any person resulting from a hit and run motor accident (where identity of vehicle cannot be ascertained), enhanced to ₹2 Lakhs for death and ₹50,000 for grievous hurt.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
            "commencement_date": "1989-07-01",
            "jurisdiction": "Central / District Magistrate / Claims Enquiry Officer",
            "is_current": True,
            "relevance_notes": "Ensures accident victims get assured state compensation even when perpetrator vehicle flees."
        },

        # =========================================================================
        # 13. INSURANCE LAW
        # =========================================================================
        {
            "id": "INSURANCE_OMBUDSMAN_2017",
            "act_name": "Insurance Ombudsman Rules, 2017",
            "section": "Rule 13 & Rule 14",
            "title": "Manner in which complaint shall be made to Insurance Ombudsman and Scope of Authority",
            "category": CaseCategoryEnum.INSURANCE,
            "keywords": ["insurance claim rejected", "claim repudiated", "insurance ombudsman", "health insurance claim", "life insurance", "tpa rejection"],
            "description": "Provides efficient, cost-effective grievance redressal for personal insurance policyholders against insurer rejection/repudiation of claims, delay in claim settlement, dispute over premium paid, or misrepresentation of terms. Free filing up to claim limit of ₹30 Lakhs.",
            "official_url": "https://irdai.gov.in/",
            "commencement_date": "2017-04-27",
            "jurisdiction": "Central / Insurance Ombudsman Centres across India",
            "is_current": True,
            "relevance_notes": "Available after insurance company rejects grievance or fails to reply within 30 days."
        },

        # =========================================================================
        # 14. ENVIRONMENTAL LAW
        # =========================================================================
        {
            "id": "NGT_ACT_2010_SEC14_15",
            "act_name": "The National Green Tribunal Act, 2010",
            "section": "Section 14 & Section 15",
            "title": "Tribunal to settle civil environmental disputes, grant relief and restitution",
            "category": CaseCategoryEnum.ENVIRONMENTAL,
            "keywords": ["ngt", "national green tribunal", "pollution", "tree felling", "illegal construction green zone", "air pollution", "water contamination"],
            "description": "The National Green Tribunal has jurisdiction over all civil cases where a substantial question relating to environment arises out of implementation of enactments specified in Schedule I. Can award relief and restitution of property and environment.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2056",
            "commencement_date": "2010-10-18",
            "jurisdiction": "Central / NGT Benches (Principal: Delhi, Pune, Chennai, Kolkata, Bhopal)",
            "is_current": True,
            "relevance_notes": "Application must be filed within 6 months from date cause of action first arose."
        },

        # =========================================================================
        # 15. ADMINISTRATIVE & REGULATORY LAW (RTI & TRIBUNALS)
        # =========================================================================
        {
            "id": "RTI_ACT_2005_SEC6_7_19",
            "act_name": "The Right to Information Act, 2005",
            "section": "Section 6, Section 7 & Section 19",
            "title": "Request for obtaining information, 30-day disposal timeline, and First & Second Appeals",
            "category": CaseCategoryEnum.ADMINISTRATIVE,
            "keywords": ["rti", "right to information", "pio", "public information officer", "30 days rti", "first appeal", "second appeal", "central information commission"],
            "description": "Any citizen can file an application to the Public Information Officer (PIO) with ₹10 fee. Information concerning life or liberty must be provided within 48 hours; general information within 30 days. First Appeal lies to senior designated officer under Sec 19(1); Second Appeal to Information Commission under Sec 19(3).",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2065",
            "commencement_date": "2005-10-12",
            "jurisdiction": "Central & State Public Authorities",
            "is_current": True,
            "relevance_notes": "Primary citizen empowerment tool to uncover official government records, status of police complaints, and administrative files."
        },

        # =========================================================================
        # 16. IMMIGRATION & CITIZENSHIP LAW
        # =========================================================================
        {
            "id": "PASSPORTS_ACT_1967_SEC5_6_10",
            "act_name": "The Passports Act, 1967",
            "section": "Section 5, Section 6 & Section 10",
            "title": "Applications for passports, Refusal grounds, and Variation/Impounding of passports",
            "category": CaseCategoryEnum.IMMIGRATION,
            "keywords": ["passport", "passport impounded", "passport refusal", "rpo", "criminal case passport", "nOC passport", "frro"],
            "description": "Governs issue and refusal of passports. Under Section 6(2)(f), passport cannot be refused merely because of a pending criminal trial without prior judicial permission (NOC) from the concerned trial court. Section 10 governs impounding.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1457",
            "commencement_date": "1967-06-24",
            "jurisdiction": "Central / Regional Passport Offices & MEA",
            "is_current": True,
            "relevance_notes": "Citizen accused in minor FIR can travel abroad after securing court NOC under GSR 570(E) notification."
        },

        # =========================================================================
        # 17. ALTERNATIVE DISPUTE RESOLUTION (ADR)
        # =========================================================================
        {
            "id": "ARBITRATION_1996_SEC8_9_11",
            "act_name": "The Arbitration and Conciliation Act, 1996",
            "section": "Section 8, Section 9 & Section 11",
            "title": "Power to refer parties to arbitration, Interim measures by Court, and Appointment of Arbitrators",
            "category": CaseCategoryEnum.ADR,
            "keywords": ["arbitration", "arbitrator", "arbitration clause", "section 9 interim relief", "section 11 appointment", "commercial dispute", "arbitral award"],
            "description": "Where an arbitration agreement exists, judicial authority shall refer parties to arbitration under Section 8. Section 9 permits parties to apply to court for interim measures of protection before, during, or after arbitral proceedings.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1978",
            "commencement_date": "1996-08-22",
            "jurisdiction": "Central / High Courts & Commercial Courts",
            "is_current": True,
            "relevance_notes": "Governs contractual disputes where contracts contain mandatory arbitration clauses."
        },
        {
            "id": "MEDIATION_ACT_2023",
            "act_name": "The Mediation Act, 2023",
            "section": "Section 5, Section 19 & Section 27",
            "title": "Pre-litigation mediation and Enforcement of mediated settlement agreements",
            "category": CaseCategoryEnum.ADR,
            "keywords": ["mediation", "pre-litigation mediation", "mediation act 2023", "settlement agreement", "mediator"],
            "description": "Institutionalizes formal mediation in India. Provides that a mediated settlement agreement signed by parties and authenticated by mediator shall be final, binding and enforceable in the same manner as a judgment or decree of a court.",
            "official_url": "https://lawmin.gov.in/",
            "commencement_date": "2023-09-15",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "relevance_notes": "Enacted modern statutory ADR framework granting mediated settlement agreements equivalent standing to court decrees."
        },
        {
            "id": "NALSA_1987_SEC12_19",
            "act_name": "The Legal Services Authorities Act, 1987",
            "section": "Section 12 & Section 19",
            "title": "Criteria for Free Legal Aid and Organization of Lok Adalats",
            "category": CaseCategoryEnum.GENERAL,
            "keywords": ["legal aid", "free lawyer", "nalsa", "dlsa", "15100", "marginalized", "lok adalat", "no court fee"],
            "description": "Section 12 provides free competent legal services through NALSA/SLSA/DLSA to eligible persons (women, children, industrial workers, SC/ST, custody, low income). Section 19 establishes Lok Adalats whose awards are final with refund of court fees.",
            "official_url": "https://nalsa.gov.in/",
            "commencement_date": "1995-11-09",
            "jurisdiction": "Central / All India",
            "is_current": True,
            "relevance_notes": "Citizens facing financial distress can access free counsel via National Legal Aid Helpline 15100 or local DLSA."
        }
    ]

    @classmethod
    def retrieve_grounded_laws(cls, text: str, category: Optional[CaseCategoryEnum] = None, state: Optional[str] = None) -> List[LegalCitation]:
        """
        Retrieves verified statutory citations relevant to the user query and facts.
        Prioritizes direct section/article mentions, specific category relevance,
        and high-signal keywords. Never fabricates provisions.
        """
        lower_query = text.lower()
        query_words = set(re.findall(r"\w+", lower_query))
        matches: List[Tuple[int, Dict]] = []

        for statute in cls.VERIFIED_STATUTES:
            score = 0
            
            # 1. Exact section or act name mention in text (Highest Priority: +15)
            sec_lower = statute["section"].lower()
            sec_numbers = re.findall(r"\b\d+[a-z]?\b", sec_lower)
            act_words = [w for w in re.findall(r"\w+", statute["act_name"].lower()) if len(w) > 3 and w not in ["the", "act", "and", "india"]]
            
            for num in sec_numbers:
                if re.search(rf"\b(section|sec|art|article|order|rule|clause)\s*{num}\b", lower_query):
                    score += 15
                    break
                elif len(num) >= 3 and re.search(rf"\b{num}\b", lower_query) and not re.search(rf"(?:rs\.?|₹|inr|\$)\s*{num}\b", lower_query):
                    score += 12
                    break
                    
            if any(w in lower_query for w in act_words):
                score += 8

            # 2. Category match bonus (+5)
            if category and statute["category"] == category:
                score += 5
            
            # 3. State match (+4)
            if state and state.lower() in statute["jurisdiction"].lower():
                score += 4
                
            # 4. Keyword matching
            for kw in statute["keywords"]:
                kw_lower = kw.lower()
                if kw_lower in lower_query:
                    score += 6
                else:
                    kw_words = set(re.findall(r"\w+", kw_lower))
                    if kw_words and kw_words.issubset(query_words):
                        score += 4
                    elif any(w in query_words for w in kw_words if len(w) > 3):
                        score += 1

            if score > 0:
                matches.append((score, statute))

        # Sort descending by relevance score
        matches.sort(key=lambda x: x[0], reverse=True)
        top_statutes = [item[1] for item in matches[:4]]

        citations = []
        for s in top_statutes:
            citations.append(LegalCitation(
                act_name=s["act_name"],
                section=s["section"],
                title=s["title"],
                description=s["description"],
                official_url=s["official_url"],
                commencement_date=s.get("commencement_date"),
                jurisdiction=s["jurisdiction"],
                is_current=s.get("is_current", True),
                historical_equivalent=s.get("historical_equivalent"),
                portal_source=s.get("official_url"),
                verification_status=VerificationStatusEnum.VERIFIED
            ))

        return citations

    @classmethod
    def verify_citation_claim(cls, act_name: str, section: str) -> Tuple[bool, Optional[LegalCitation], str]:
        """
        Validates if a cited act and section exist in the verified registry.
        Detects hallucinated or invented citations.
        """
        act_clean = act_name.strip().lower()
        sec_clean = section.strip().lower()

        for s in cls.VERIFIED_STATUTES:
            if sec_clean in s["section"].lower() and any(w in s["act_name"].lower() for w in act_clean.split()):
                citation = LegalCitation(
                    act_name=s["act_name"],
                    section=s["section"],
                    title=s["title"],
                    description=s["description"],
                    official_url=s["official_url"],
                    commencement_date=s.get("commencement_date"),
                    jurisdiction=s["jurisdiction"],
                    is_current=s.get("is_current", True),
                    historical_equivalent=s.get("historical_equivalent"),
                    portal_source=s.get("official_url"),
                    verification_status=VerificationStatusEnum.VERIFIED
                )
                return (True, citation, "Verified in official statutory registry.")

        return (
            False,
            None,
            f"Unverified or non-existent section: '{section}' of '{act_name}'. LawPilot AI does not invent or confirm unverified legal provisions."
        )
