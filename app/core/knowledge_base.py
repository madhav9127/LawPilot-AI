import re
from typing import List, Dict, Optional, Tuple
from app.models.schemas import LegalCitation, VerificationStatusEnum, CaseCategoryEnum

class LegalKnowledgeBase:
    """
    Verified Indian Statutory Knowledge Base and Anti-Hallucination Retrieval Engine (RAG).
    Grounds all legal analysis directly in verified Indian statutes, official portals,
    and established procedural legal frameworks across all major domains of Indian law.
    """
    
    # Official Government & Judicial Portals
    OFFICIAL_PORTALS = {
        "india_code": "https://www.indiacode.nic.in/",
        "ecourts": "https://ecourts.gov.in/",
        "sci": "https://main.sci.gov.in/",
        "consumer_affairs": "https://consumeraffairs.nic.in/",
        "consumer_helpline": "https://consumerhelpline.gov.in/",
        "edaakhil": "https://edaakhil.nic.in/",
        "cybercrime": "https://cybercrime.gov.in/",
        "rbi_cms": "https://cms.rbi.org.in/",
        "nalsa": "https://nalsa.gov.in/",
        "shram_suvidha": "https://shramsuvidha.gov.in/",
        "incometax": "https://incometax.gov.in/",
        "cbic_gst": "https://www.cbic.gov.in/",
        "ngt": "https://greentribunal.gov.in/",
        "cat": "https://cgat.gov.in/",
        "parivahan": "https://parivahan.gov.in/",
        "ipindia": "https://ipindia.gov.in/",
        "wcd": "https://wcd.nic.in/",
        "ncw": "https://ncw.nic.in/",
        "rera_national": "https://mohua.gov.in/"
    }

    # Verified Statutory Provisions Database across 18+ Indian Legal Domains
    VERIFIED_STATUTES: List[Dict] = [
        # =====================================================================
        # 1. CRIMINAL LAW & CRIMINAL PROCEDURE
        # =====================================================================
        {
            "id": "BNS_318",
            "act_name": "The Bharatiya Nyaya Sanhita, 2023",
            "section": "Section 318",
            "title": "Cheating and dishonestly inducing delivery of property",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["cheating", "fraud", "scam", "financial fraud", "dishonest inducement", "420", "dhokhadhadi", "thug", "thagi"],
            "description": "Replaces Section 420 of IPC (effective 1 July 2024). Punishes cheating and dishonestly inducing the delivery of any property or valuable security with imprisonment up to 7 years and fine.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/22002",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Applicable for criminal offences committed on or after 1 July 2024. Prior offences governed by IPC Section 420."
        },
        {
            "id": "BNS_303",
            "act_name": "The Bharatiya Nyaya Sanhita, 2023",
            "section": "Section 303",
            "title": "Theft",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["theft", "stolen", "chori", "stealing", "moveable property", "robbery", "thief"],
            "description": "Replaces Section 378/379 of IPC (effective 1 July 2024). Moving any moveable property out of the possession of any person without consent dishonestly is punishable with up to 3 years imprisonment or fine.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/22002",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Central criminal provision for theft of property, vehicles, or physical items."
        },
        {
            "id": "BNS_351",
            "act_name": "The Bharatiya Nyaya Sanhita, 2023",
            "section": "Section 351",
            "title": "Criminal Intimidation",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["threat", "intimidation", "threatening", "threat to kill", "threaten injury", "dhamki", "blackmail"],
            "description": "Replaces Sections 503 and 506 of IPC (effective 1 July 2024). Punishes threatening another with injury to person, reputation, or property with intent to cause alarm or force any action.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/22002",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Applicable to verbal, written, or electronic criminal threats."
        },
        {
            "id": "BNS_356",
            "act_name": "The Bharatiya Nyaya Sanhita, 2023",
            "section": "Section 356",
            "title": "Defamation",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["defamation", "defame", "reputation", "slander", "libel", "maan hani", "badnaam", "false allegations"],
            "description": "Replaces Sections 499 and 500 of IPC (effective 1 July 2024). Punishes making or publishing imputations intending to harm reputation with simple imprisonment up to 2 years, fine, or community service.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/22002",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Provides community service as a new statutory remedy alongside fine and imprisonment."
        },
        {
            "id": "BNSS_173",
            "act_name": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
            "section": "Section 173",
            "title": "Information in cognizable cases (First Information Report / FIR)",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["fir", "police complaint", "first information report", "police report", "cognizable", "e-fir", "thaney", "zero fir"],
            "description": "Replaces Section 154 of CrPC (effective 1 July 2024). Mandates police officers to reduce cognizable offence information to writing (FIR), enables electronic information (e-FIR) to be signed within 3 days, and codifies Zero FIR to be registered irrespective of territorial jurisdiction.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/22003",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Codifies mandatory registration per Lalita Kumari v. Govt of UP (2014 SC) and institutionalizes Zero FIR."
        },
        {
            "id": "BNSS_35",
            "act_name": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
            "section": "Section 35",
            "title": "When police may arrest without warrant and procedural safeguards",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["arrest", "police arrest", "notice of appearance", "handcuffing", "arrest grounds", "arnesh kumar", "41a"],
            "description": "Replaces Section 41 and 41A of CrPC (effective 1 July 2024). Requires police to issue Notice of Appearance for offences punishable with up to 7 years imprisonment unless specified arrest criteria are satisfied. Requires Deputy SP permission for arrest of persons who are infirm or over 60 years for offences with less than 3 years imprisonment.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/22003",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Incorporates Arnesh Kumar v. State of Bihar arrest safeguards."
        },
        {
            "id": "BNSS_482",
            "act_name": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
            "section": "Section 482",
            "title": "Direction for grant of bail to person apprehending arrest (Anticipatory Bail)",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["anticipatory bail", "pre-arrest bail", "bail", "apprehending arrest", "sessions court", "high court bail", "zamanat"],
            "description": "Replaces Section 438 of CrPC (effective 1 July 2024). Empowers the High Court and Court of Session to grant direction that in the event of arrest for a non-bailable offence, the applicant shall be released on bail.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/22003",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Primary safeguard against malicious or politically motivated arrests in non-bailable matters."
        },
        {
            "id": "BSA_61_63",
            "act_name": "The Bharatiya Sakshya Adhiniyam, 2023",
            "section": "Section 61 & 63",
            "title": "Admissibility of electronic records and electronic certificate",
            "category": CaseCategoryEnum.CRIMINAL,
            "keywords": ["electronic evidence", "whatsapp screenshot", "cctv footage", "email proof", "phone recording", "certificate 65b", "digital record"],
            "description": "Replaces Section 65B of Indian Evidence Act (effective 1 July 2024). Affirms that electronic records are admissible as primary or secondary evidence with prescribed certificate signed by the person managing the device or lawful custodian.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/22004",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Essential for proving WhatsApp chats, SMS, emails, and phone recordings in court."
        },

        # =====================================================================
        # 2. CIVIL DISPUTES & CIVIL PROCEDURE
        # =====================================================================
        {
            "id": "CPC_O39_R1_2",
            "act_name": "The Code of Civil Procedure, 1908",
            "section": "Order 39, Rules 1 & 2",
            "title": "Temporary Injunctions and Interlocutory Orders",
            "category": CaseCategoryEnum.CIVIL,
            "keywords": ["stay order", "injunction", "temporary injunction", "restraining order", "property demolition", "third party rights", "status quo"],
            "description": "Grants court authority to issue temporary injunctions restraining a party from wasting, damaging, alienating, selling, removing, or disposing of disputed property, or from causing injury to plaintiff until final disposal of suit.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2191",
            "commencement_date": "1909-01-01",
            "jurisdiction": "Central",
            "relevance_notes": "Requires establishing: (1) prima facie case, (2) balance of convenience, and (3) irreparable loss."
        },
        {
            "id": "CPC_O37",
            "act_name": "The Code of Civil Procedure, 1908",
            "section": "Order 37",
            "title": "Summary Procedure for recovery of debts and liquidated demands",
            "category": CaseCategoryEnum.CIVIL,
            "keywords": ["summary suit", "money recovery", "promissory note", "bill of exchange", "written contract debt", "fast track civil suit"],
            "description": "Provides an expedited summary civil suit procedure for recovery of debts arising from bills of exchange, hundis, promissory notes, or written contracts where defendant must obtain leave to defend.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2191",
            "commencement_date": "1909-01-01",
            "jurisdiction": "Central",
            "relevance_notes": "Quickest civil remedy for commercial unpaid debts and written financial contracts."
        },
        {
            "id": "SRA_6",
            "act_name": "The Specific Relief Act, 1963",
            "section": "Section 6",
            "title": "Suit by person dispossessed of immovable property",
            "category": CaseCategoryEnum.CIVIL,
            "keywords": ["illegal dispossession", "unlawful eviction", "forcible entry", "lockout", "possession recovery", "6 months limitation"],
            "description": "Provides that if any person is dispossessed without consent of immovable property otherwise than in due course of law, they may recover possession by suit within 6 months, notwithstanding any other title.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1583",
            "commencement_date": "1964-03-01",
            "jurisdiction": "Central",
            "relevance_notes": "Key protection against illegal physical eviction by landlords or land-grabbers without court decree."
        },
        {
            "id": "LIMITATION_3",
            "act_name": "The Limitation Act, 1963",
            "section": "Section 3 & Schedule",
            "title": "Bar of limitation for civil suits and applications",
            "category": CaseCategoryEnum.CIVIL,
            "keywords": ["limitation period", "time barred", "expired claim", "delay in filing", "3 years limitation", "money claim deadline"],
            "description": "Every suit instituted after the prescribed period shall be dismissed. General limitation period is 3 years for money recovery, contract breach, and salary claims; 12 years for immovable property possession.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1566",
            "commencement_date": "1964-01-01",
            "jurisdiction": "Central",
            "relevance_notes": "Fundamental procedural safeguard; claims filed after limitation are legally unenforceable."
        },

        # =====================================================================
        # 3. PROPERTY, LAND & REAL ESTATE
        # =====================================================================
        {
            "id": "RERA_18",
            "act_name": "The Real Estate (Regulation and Development) Act, 2016",
            "section": "Section 18",
            "title": "Return of amount and compensation for delay in handing over possession",
            "category": CaseCategoryEnum.PROPERTY,
            "keywords": ["builder delay", "flat possession delay", "rera complaint", "builder refund", "delay interest", "allottee rights", "possession letter"],
            "description": "If promoter fails to complete or give possession of apartment in accordance with agreement for sale, allottee has the right to withdraw and demand full refund with prescribed interest, or stay in project and receive monthly delay interest.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2158",
            "commencement_date": "2016-05-01",
            "jurisdiction": "Central / State RERA",
            "relevance_notes": "Standard interest rate is State SBI MCLR + 2%. Binding on all registered builders."
        },
        {
            "id": "RERA_31",
            "act_name": "The Real Estate (Regulation and Development) Act, 2016",
            "section": "Section 31",
            "title": "Filing of complaints before the Real Estate Regulatory Authority",
            "category": CaseCategoryEnum.PROPERTY,
            "keywords": ["file rera complaint", "maharera", "up rera", "karnataka rera", "delhi rera", "adjudicating officer", "builder grievance"],
            "description": "Any aggrieved person may file a complaint with the state Real Estate Regulatory Authority or the Adjudicating Officer for violation of provisions or rules by a promoter, allottee, or real estate agent.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2158",
            "commencement_date": "2016-05-01",
            "jurisdiction": "Central / State RERA",
            "relevance_notes": "Fast-track administrative adjudication before approaching civil courts."
        },
        {
            "id": "TPA_54",
            "act_name": "The Transfer of Property Act, 1882",
            "section": "Section 54",
            "title": "'Sale' defined and transfer of immovable property",
            "category": CaseCategoryEnum.PROPERTY,
            "keywords": ["sale deed", "property sale", "agreement to sell", "conveyance deed", "registered sale deed", "property purchase"],
            "description": "Sale is a transfer of ownership in exchange for a price paid or promised. Transfer of tangible immovable property of value ₹100 or upwards can be made only by a registered instrument.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
            "commencement_date": "1882-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Distinguishes 'Agreement to Sell' (contractual right) from registered 'Sale Deed' (actual title transfer)."
        },
        {
            "id": "REG_17",
            "act_name": "The Registration Act, 1908",
            "section": "Section 17",
            "title": "Documents of which registration is compulsory",
            "category": CaseCategoryEnum.PROPERTY,
            "keywords": ["compulsory registration", "unregistered agreement", "notarized deed", "lease registration", "gift deed registration"],
            "description": "Mandates compulsory registration of instruments of gift of immovable property, non-testamentary instruments transferring or extinguishing right/title in immovable property, and leases exceeding 1 year.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2186",
            "commencement_date": "1909-01-01",
            "jurisdiction": "Central",
            "relevance_notes": "Unregistered documents requiring compulsory registration under Sec 17 cannot affect immovable property under Sec 49."
        },

        # =====================================================================
        # 4. FAMILY LAW, MARRIAGE, DIVORCE & MAINTENANCE
        # =====================================================================
        {
            "id": "HMA_13",
            "act_name": "The Hindu Marriage Act, 1955",
            "section": "Section 13",
            "title": "Divorce grounds for Hindu marriages",
            "category": CaseCategoryEnum.FAMILY,
            "keywords": ["divorce", "grounds for divorce", "cruelty", "desertion", "talaq", "matrimonial dispute", "adultery", "mental cruelty"],
            "description": "Provides statutory grounds for dissolution of marriage by decree of divorce, including cruelty, desertion for not less than two years, conversion, unsoundness of mind, venereal disease, and renunciation of the world.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1560",
            "commencement_date": "1955-05-18",
            "jurisdiction": "Central",
            "relevance_notes": "Applicable to Hindus, Buddhists, Jains, and Sikhs. Landmark precedents recognize persistent emotional abuse as cruelty."
        },
        {
            "id": "HMA_13B",
            "act_name": "The Hindu Marriage Act, 1955",
            "section": "Section 13B",
            "title": "Divorce by Mutual Consent",
            "category": CaseCategoryEnum.FAMILY,
            "keywords": ["mutual consent divorce", "amicable divorce", "first motion", "second motion", "cooling off period", "joint divorce petition"],
            "description": "Allows husband and wife to jointly petition the Family Court for divorce on ground of living separately for 1 year or more and inability to live together. Statutory 6-month cooling-off period can be waived per Amardeep Singh v. Harveen Kaur (2017 SC).",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1560",
            "commencement_date": "1955-05-18",
            "jurisdiction": "Central",
            "relevance_notes": "Most dignified and fastest legal procedure for marriage dissolution in India."
        },
        {
            "id": "HMA_24_25",
            "act_name": "The Hindu Marriage Act, 1955",
            "section": "Section 24 & 25",
            "title": "Maintenance pendente lite, expenses of proceedings, and permanent alimony",
            "category": CaseCategoryEnum.FAMILY,
            "keywords": ["interim maintenance", "alimony", "permanent alimony", "maintenance pendente lite", "child support", "kharcha"],
            "description": "Section 24 allows either spouse having no independent income to claim monthly interim maintenance and litigation expenses during matrimonial proceedings. Section 25 provides for permanent alimony and maintenance at decree.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1560",
            "commencement_date": "1955-05-18",
            "jurisdiction": "Central",
            "relevance_notes": "Governed by uniform disclosure guidelines in landmark Supreme Court ruling Rajnesh v. Neha (2020)."
        },
        {
            "id": "PWDVA_12_18_20",
            "act_name": "Protection of Women from Domestic Violence Act, 2005",
            "section": "Sections 12, 18, 19, 20",
            "title": "Application to Magistrate for protection orders, residence, and monetary relief",
            "category": CaseCategoryEnum.FAMILY,
            "keywords": ["domestic violence", "dv act", "shared household", "protection order", "residence order", "beaten by husband", "in-laws harassment"],
            "description": "Empowers aggrieved women in domestic relationships to file an application before Magistrate for emergency protection orders (Sec 18), right to reside in shared household without eviction (Sec 19), and monetary maintenance (Sec 20).",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2012",
            "commencement_date": "2006-10-26",
            "jurisdiction": "Central",
            "relevance_notes": "Civil-law remedy with criminal enforcement; right to reside in shared household affirmed in Satish Chander Ahuja (2020 SC)."
        },
        {
            "id": "BNSS_144",
            "act_name": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
            "section": "Section 144",
            "title": "Order for maintenance of wives, children and parents",
            "category": CaseCategoryEnum.FAMILY,
            "keywords": ["125 crpc", "maintenance 125", "maintenance for parents", "child maintenance", "wife maintenance", "summary maintenance"],
            "description": "Replaces Section 125 of CrPC (effective 1 July 2024). Summary procedure where Magistrate can order any person with sufficient means who neglects or refuses to maintain wife, minor legitimate/illegitimate child, or elderly father/mother to pay a monthly allowance.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/22003",
            "commencement_date": "2024-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Secular provision available to citizens of all religious backgrounds irrespective of personal laws."
        },

        # =====================================================================
        # 5. CONSUMER PROTECTION
        # =====================================================================
        {
            "id": "CPA_2_7",
            "act_name": "The Consumer Protection Act, 2019",
            "section": "Section 2(7)",
            "title": "Definition of 'Consumer'",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["consumer definition", "who is consumer", "buyer rights", "online shopper", "commercial use exclusion", "consumer standing"],
            "description": "Defines a consumer as any person who buys goods or hires services for consideration, including offline transactions, e-commerce, teleshopping, and direct selling. Excludes purchases made for commercial resale.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
            "commencement_date": "2020-07-20",
            "jurisdiction": "Central",
            "relevance_notes": "Repealed and replaced the Consumer Protection Act, 1986. Expressly covers online e-commerce consumers."
        },
        {
            "id": "CPA_35",
            "act_name": "The Consumer Protection Act, 2019",
            "section": "Section 35",
            "title": "Manner in which complaint shall be made before District Commission",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["consumer complaint", "file consumer court", "district consumer forum", "e-daakhil", "consumer compensation", "consumer court fees"],
            "description": "Allows a consumer or recognized consumer association to file a complaint before District Consumer Disputes Redressal Commission for claims up to ₹50 Lakhs (e-filing enabled nationwide via e-Daakhil). Limitation period is 2 years from cause of action.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
            "commencement_date": "2020-07-20",
            "jurisdiction": "Central",
            "relevance_notes": "Pecuniary jurisdiction revised in Dec 2021: District (up to ₹50L), State (₹50L to ₹2Cr), National (>₹2Cr)."
        },
        {
            "id": "CPA_ECOM_2020",
            "act_name": "Consumer Protection (E-Commerce) Rules, 2020",
            "section": "Rules 5 & 6",
            "title": "Duties of e-commerce entities and sellers regarding refunds and grievances",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["ecommerce refund", "amazon refund", "flipkart return", "defective item refund", "cancellation charges", "grievance officer ecommerce"],
            "description": "Mandates e-commerce platforms to appoint a Grievance Officer, acknowledge complaints within 48 hours, redress within 1 month, process refunds within reasonable timelines, and prohibits cancellation charges on consumer if seller cancels.",
            "official_url": "https://consumeraffairs.nic.in/",
            "commencement_date": "2020-07-24",
            "jurisdiction": "Central",
            "relevance_notes": "Statutory rules enforced by Central Consumer Protection Authority (CCPA) and National Consumer Helpline (1915)."
        },

        # =====================================================================
        # 6. EMPLOYMENT, LABOUR & INDUSTRIAL DISPUTES
        # =====================================================================
        {
            "id": "PWA_5",
            "act_name": "The Payment of Wages Act, 1936",
            "section": "Section 5",
            "title": "Time of payment of wages",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["salary delay", "salary payment date", "unpaid wages", "when salary must be paid", "7th day salary", "10th of month"],
            "description": "Mandates that wages in establishments with less than 1,000 workers must be paid before expiry of the 7th day, and in other establishments before expiry of the 10th day after the last day of the wage period.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2361",
            "commencement_date": "1937-03-28",
            "jurisdiction": "Central / State",
            "relevance_notes": "Applicable across commercial and industrial establishments; provides statutory right to timely monthly remuneration."
        },
        {
            "id": "PWA_15",
            "act_name": "The Payment of Wages Act, 1936",
            "section": "Section 15",
            "title": "Claims arising out of deductions from wages or delay in payment of wages",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["claim for unpaid salary", "labour commissioner", "unauthorized deduction", "compensation for unpaid wages", "10 times compensation"],
            "description": "Authorizes employee to file a formal claim before the Authority appointed under the Act / Labour Commissioner for recovery of delayed or unlawfully deducted wages, with statutory compensation up to 10 times the deducted amount.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2361",
            "commencement_date": "1937-03-28",
            "jurisdiction": "Central / State",
            "relevance_notes": "Limitation period is 12 months from the date on which wages were due, extendable on showing sufficient cause."
        },
        {
            "id": "IDA_25F",
            "act_name": "The Industrial Disputes Act, 1947",
            "section": "Section 25F",
            "title": "Conditions precedent to retrenchment of workmen",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["illegal termination", "layoff compensation", "wrongful termination", "retrenchment notice", "severance pay", "1 month notice"],
            "description": "Prohibits retrenchment of a workman in continuous service for not less than one year until workman is given one month written notice (or wages in lieu) and paid retrenchment compensation equal to 15 days average pay for every completed year of service.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1614",
            "commencement_date": "1947-04-01",
            "jurisdiction": "Central / State",
            "relevance_notes": "Failure to comply renders the termination void ab initio with right to reinstatement and back wages."
        },
        {
            "id": "POSH_4_9",
            "act_name": "Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013",
            "section": "Sections 4 & 9",
            "title": "Constitution of Internal Committee and complaint of sexual harassment",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["posh act", "workplace sexual harassment", "internal committee", "ic complaint", "harassment by manager", "hostile work environment"],
            "description": "Mandates every employer with 10 or more employees to constitute an Internal Committee (IC) headed by a senior woman employee. Aggrieved woman may make a written complaint within 3 months of incident (extendable by 3 months).",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2104",
            "commencement_date": "2013-12-09",
            "jurisdiction": "Central",
            "relevance_notes": "Statutory inquiry has powers of Civil Court; failure to constitute IC attracts penalty up to ₹50,000 on employer."
        },
        {
            "id": "GRATUITY_4",
            "act_name": "The Payment of Gratuity Act, 1972",
            "section": "Section 4",
            "title": "Payment of Gratuity on retirement, resignation, death, or disablement",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["gratuity eligibility", "5 years service gratuity", "resignation gratuity", "gratuity formula", "controlling authority gratuity"],
            "description": "Gratuity is payable to an employee on separation after rendering continuous service for not less than 5 years (5-year rule not required in case of death or disablement). Calculated as 15 days wages per completed year of service.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1615",
            "commencement_date": "1972-09-16",
            "jurisdiction": "Central",
            "relevance_notes": "Statutory maximum limit is ₹20 Lakhs; employer cannot forfeit gratuity except for riotous conduct or moral turpitude."
        },

        # =====================================================================
        # 7. TENANT & LANDLORD DISPUTES
        # =====================================================================
        {
            "id": "TPA_106",
            "act_name": "The Transfer of Property Act, 1882",
            "section": "Section 106",
            "title": "Duration of certain leases in absence of written contract or local usage",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["notice period", "eviction", "termination", "15 days notice", "lease duration", "oral tenancy", "no agreement"],
            "description": "In the absence of a contract or local law to the contrary, a lease of immovable property for residential or commercial purposes is deemed to be month-to-month, terminable on 15 days notice expiring with the end of a month of the tenancy.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
            "commencement_date": "1882-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Core statutory baseline for residential tenancies without a registered written agreement."
        },
        {
            "id": "TPA_108",
            "act_name": "The Transfer of Property Act, 1882",
            "section": "Section 108",
            "title": "Rights and liabilities of lessor and lessee",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["security deposit refund", "wear and tear", "painting deduction", "landlord duties", "tenant rights", "essential services cut"],
            "description": "Governs lessor obligations to maintain property in habitable condition and return security deposit upon vacation, subject only to reasonable wear and tear. Landlords cannot arbitrarily deduct painting or re-letting costs without proof of willful damage.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
            "commencement_date": "1882-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Standard civil authority prohibiting arbitrary security deposit withholding."
        },
        {
            "id": "MTA_11",
            "act_name": "Model Tenancy Act, 2021",
            "section": "Section 11",
            "title": "Security deposit limit and refund conditions",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["security deposit cap", "2 months rent deposit", "mta deposit", "deposit refund on vacation", "model tenancy act"],
            "description": "Security deposit for residential premises is strictly capped at a maximum of two months rent, and one month rent for non-residential premises. It must be refunded to the tenant at the time of taking over vacant possession.",
            "official_url": "https://mohua.gov.in/",
            "commencement_date": "2021-06-02",
            "jurisdiction": "Model Guidelines / State Adopted",
            "relevance_notes": "Central model act recommended for state adoption to eliminate predatory 6-10 month deposit demands."
        },
        {
            "id": "MTA_13",
            "act_name": "Model Tenancy Act, 2021",
            "section": "Section 13",
            "title": "Succession of tenancy rights",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["tenancy succession", "death of tenant", "heirs tenancy rights", "transfer of tenancy", "model tenancy succession"],
            "description": "Tenancy rights do not extinguish on death of the tenant; they devolve upon legal heirs residing with the tenant (spouse, children, parents) for the remainder of the agreed tenancy period under identical contractual terms.",
            "official_url": "https://mohua.gov.in/",
            "commencement_date": "2021-06-02",
            "jurisdiction": "Model Guidelines / State Adopted",
            "relevance_notes": "Protects bereaved families from sudden arbitrary eviction following the demise of the primary tenant."
        },
        {
            "id": "MTA_21",
            "act_name": "Model Tenancy Act, 2021",
            "section": "Section 21",
            "title": "Protection against eviction and procedure for recovery of possession",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["illegal eviction", "eviction order", "rent authority", "lockout", "eviction grounds", "non-payment of rent"],
            "description": "No landlord shall evict any tenant except by an application made to the Rent Authority. Grounds include failure to pay agreed rent for 2 consecutive months, unauthorized sub-letting, or structural misuse.",
            "official_url": "https://mohua.gov.in/",
            "commencement_date": "2021-06-02",
            "jurisdiction": "Model Guidelines / State Adopted",
            "relevance_notes": "Strictly prohibits extra-judicial lockouts, cutting electricity/water, or goon intimidation."
        },

        # =====================================================================
        # 8. CYBERCRIME, ONLINE FRAUD & IT LAW
        # =====================================================================
        {
            "id": "IT_66C",
            "act_name": "The Information Technology Act, 2000",
            "section": "Section 66C",
            "title": "Punishment for identity theft",
            "category": CaseCategoryEnum.CYBER,
            "keywords": ["identity theft", "password stolen", "fake profile", "stolen biometric", "impersonation", "unauthorized login", "otp theft"],
            "description": "Punishes fraudulently or dishonestly making use of the electronic signature, password, or other unique identification feature of any other person with imprisonment up to 3 years and fine up to ₹1 Lakh.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
            "commencement_date": "2000-10-17",
            "jurisdiction": "Central",
            "relevance_notes": "Core provision for account takeover, stolen credentials, and simulated social media profiles."
        },
        {
            "id": "IT_66D",
            "act_name": "The Information Technology Act, 2000",
            "section": "Section 66D",
            "title": "Punishment for cheating by personation by using computer resource",
            "category": CaseCategoryEnum.CYBER,
            "keywords": ["online fraud", "upi scam", "phishing", "cyber cheating", "fake job offer", "lottery scam", "kyc fraud", "part time job scam"],
            "description": "Punishes cheating by personation by using any computer resource or communication device with imprisonment up to 3 years and fine up to ₹1 Lakh.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
            "commencement_date": "2000-10-17",
            "jurisdiction": "Central",
            "relevance_notes": "Applied extensively in UPI financial frauds, phishing, and fake customer care scams."
        },
        {
            "id": "IT_67_67A",
            "act_name": "The Information Technology Act, 2000",
            "section": "Sections 67 & 67A",
            "title": "Publishing or transmitting obscene or sexually explicit material electronically",
            "category": CaseCategoryEnum.CYBER,
            "keywords": ["morphing", "leaked photos", "intimate photos", "nude blackmail", "cyber blackmail", "sextortion", "revenge porn"],
            "description": "Punishes publishing, transmitting, or causing to be published in electronic form sexually explicit or obscene material. First conviction punishable with imprisonment up to 5 years and fine up to ₹10 Lakhs.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
            "commencement_date": "2000-10-17",
            "jurisdiction": "Central",
            "relevance_notes": "Primary cyber law protection against non-consensual image sharing, photo morphing, and sextortion."
        },
        {
            "id": "CYBER_1930",
            "act_name": "Citizen Financial Cyber Fraud Reporting Management System (CFCFRMS)",
            "section": "National Cybercrime Helpline 1930 & Portal",
            "title": "Emergency blocking of defrauded amounts in banking channels",
            "category": CaseCategoryEnum.CYBER,
            "keywords": ["1930", "cyber crime portal", "bank fraud helpline", "golden hour cyber", "stop payment cyber", "cybercrime.gov.in"],
            "description": "Operated by Ministry of Home Affairs (I4C). Calling 1930 within the 'golden hour' of a financial cyber fraud triggers auto-alerts across victim bank, intermediary payment gateways, and beneficiary banks to freeze stolen funds.",
            "official_url": "https://cybercrime.gov.in/",
            "commencement_date": "2021-04-01",
            "jurisdiction": "Central",
            "relevance_notes": "Fastest practical mechanism to recover money lost in UPI, credit card, and internet banking scams."
        },
        {
            "id": "DPDP_2023",
            "act_name": "Digital Personal Data Protection Act, 2023",
            "section": "Sections 6 & 11",
            "title": "Consent requirements and rights of the Data Principal",
            "category": CaseCategoryEnum.CYBER,
            "keywords": ["dpdp act", "data privacy", "personal data leak", "unauthorized data sharing", "right to erasure", "data protection board"],
            "description": "Personal data can only be processed with free, specific, informed, and unambiguous consent. Citizens have rights to access summaries of personal data, right to correction and erasure, and right to grievance redressal before Data Protection Board.",
            "official_url": "https://www.meity.gov.in/",
            "commencement_date": "2023-08-11",
            "jurisdiction": "Central",
            "relevance_notes": "Statutory framework governing personal digital privacy per Supreme Court K.S. Puttaswamy judgment."
        },

        # =====================================================================
        # 9. BANKING, LOANS & FINANCIAL DISPUTES
        # =====================================================================
        {
            "id": "NI_138",
            "act_name": "The Negotiable Instruments Act, 1881",
            "section": "Section 138",
            "title": "Dishonour of cheque for insufficiency of funds in the account",
            "category": CaseCategoryEnum.BANKING,
            "keywords": ["cheque bounce", "dishonoured cheque", "138 ni act", "15 days demand notice", "insufficient funds", "bounced cheque notice"],
            "description": "Where a cheque drawn for discharge of debt/liability is returned unpaid due to insufficient funds, the drawer commits an offence punishable with up to 2 years imprisonment or twice the cheque amount. Requires: (1) presentment within 3 months, (2) statutory notice within 30 days of return memo, (3) 15-day payment window, and (4) complaint within 30 days of notice expiry.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2281",
            "commencement_date": "1882-03-01",
            "jurisdiction": "Central",
            "relevance_notes": "Strict statutory timelines: non-service of 15-day statutory notice is fatal to prosecution."
        },
        {
            "id": "SARFAESI_13_2",
            "act_name": "The SARFAESI Act, 2002",
            "section": "Section 13(2)",
            "title": "Enforcement of security interest and 60-day demand notice",
            "category": CaseCategoryEnum.BANKING,
            "keywords": ["sarfaesi", "home loan default", "npa notice", "bank auction", "possession notice", "drt", "loan default notice"],
            "description": "When borrower defaults and account is classified as Non-Performing Asset (NPA), secured creditor must serve 60-day written demand notice giving full details of dues. Borrower has right to submit representation/objection under Sec 13(3A) which bank must consider.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2006",
            "commencement_date": "2002-06-21",
            "jurisdiction": "Central",
            "relevance_notes": "Borrower can challenge bank auction or possession measures before Debts Recovery Tribunal (DRT) under Sec 17."
        },
        {
            "id": "RBI_OMBUDSMAN_2021",
            "act_name": "Reserve Bank of India Integrated Ombudsman Scheme, 2021",
            "section": "Clause 8 & 10",
            "title": "Grievance redressal for deficiency in banking and NBFC services",
            "category": CaseCategoryEnum.BANKING,
            "keywords": ["rbi ombudsman", "bank complaint", "loan app harassment", "recovery agent harassment", "unauthorized bank debit", "cms rbi"],
            "description": "Integrated scheme covering all commercial banks, NBFCs, and payment system participants. Customers can file online complaints at https://cms.rbi.org.in if bank fails to resolve grievance within 30 days. Grants compensation up to ₹20 Lakhs for financial loss and up to ₹1 Lakh for mental anguish.",
            "official_url": "https://www.rbi.org.in/",
            "commencement_date": "2021-11-12",
            "jurisdiction": "Central",
            "relevance_notes": "Effective remedy against aggressive third-party recovery agent harassment violating RBI Fair Practices Code."
        },

        # =====================================================================
        # 10. CONTRACT & BUSINESS LAW
        # =====================================================================
        {
            "id": "ICA_10",
            "act_name": "The Indian Contract Act, 1872",
            "section": "Section 10",
            "title": "What agreements are contracts",
            "category": CaseCategoryEnum.CONTRACT,
            "keywords": ["valid contract", "free consent", "agreement validity", "competent parties", "lawful consideration", "enforceable agreement"],
            "description": "All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object, and are not hereby expressly declared to be void.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2187",
            "commencement_date": "1872-09-01",
            "jurisdiction": "Central",
            "relevance_notes": "Foundation of Indian commercial, business, employment, and rental agreements."
        },
        {
            "id": "ICA_73_74",
            "act_name": "The Indian Contract Act, 1872",
            "section": "Sections 73 & 74",
            "title": "Compensation for loss or damage caused by breach of contract and liquidated damages",
            "category": CaseCategoryEnum.CONTRACT,
            "keywords": ["breach of contract", "damages", "contract compensation", "liquidated damages", "penalty clause", "contract cancellation loss"],
            "description": "When a contract has been broken, the party who suffers by such breach is entitled to receive from the defaulting party compensation for any loss or damage naturally arising in the usual course of things. If a sum is named as liquidated damages, court awards reasonable compensation not exceeding the penalty amount.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2187",
            "commencement_date": "1872-09-01",
            "jurisdiction": "Central",
            "relevance_notes": "Per Kailash Nath Associates v. DDA (2015 SC), proof of actual damage or loss is required to claim liquidated damages."
        },
        {
            "id": "SOGA_16",
            "act_name": "The Sale of Goods Act, 1930",
            "section": "Section 16",
            "title": "Implied conditions as to quality or fitness",
            "category": CaseCategoryEnum.CONTRACT,
            "keywords": ["sale of goods", "merchantable quality", "fitness for purpose", "commercial goods defect", "buyer right to reject"],
            "description": "Where goods are bought by description from a seller who deals in goods of that description, there is an implied condition that the goods shall be of merchantable quality and reasonably fit for the purpose communicated by buyer.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2360",
            "commencement_date": "1930-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Applies to business-to-business (B2B) goods transactions outside the Consumer Protection Act."
        },

        # =====================================================================
        # 11. INTELLECTUAL PROPERTY RIGHTS
        # =====================================================================
        {
            "id": "COPYRIGHT_51_52",
            "act_name": "The Copyright Act, 1957",
            "section": "Sections 51 & 52",
            "title": "Infringement of copyright and fair dealing exceptions",
            "category": CaseCategoryEnum.IPR,
            "keywords": ["copyright infringement", "plagiarism", "piracy", "fair dealing", "stolen video", "stolen content", "youtube strike"],
            "description": "Section 51 establishes copyright infringement when unauthorized reproduction, sale, or distribution is made. Section 52 codifies fair dealing exceptions for private or personal use, research, criticism, review, and reporting of current events.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1564",
            "commencement_date": "1958-01-21",
            "jurisdiction": "Central",
            "relevance_notes": "Grants both civil remedies (injunction, damages) and criminal remedies (police seizure under Sec 64)."
        },
        {
            "id": "TRADEMARK_29",
            "act_name": "The Trade Marks Act, 1999",
            "section": "Section 29",
            "title": "Infringement of registered trade marks",
            "category": CaseCategoryEnum.IPR,
            "keywords": ["trademark infringement", "brand name copied", "counterfeit brand", "fake logo", "passing off", "deceptively similar"],
            "description": "A registered trade mark is infringed by a person who, not being a registered proprietor, uses in the course of trade a mark which is identical with, or deceptively similar to, the trade mark in relation to similar goods or services, causing public confusion.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1993",
            "commencement_date": "2003-09-15",
            "jurisdiction": "Central",
            "relevance_notes": "Common law action for 'passing off' protects unregistered trade marks with established reputation."
        },

        # =====================================================================
        # 12. MOTOR VEHICLE & ACCIDENT CLAIMS
        # =====================================================================
        {
            "id": "MVA_166",
            "act_name": "The Motor Vehicles Act, 1988 (as amended in 2019)",
            "section": "Section 166",
            "title": "Application for compensation before the Motor Accidents Claims Tribunal (MACT)",
            "category": CaseCategoryEnum.MOTOR_VEHICLE,
            "keywords": ["mact", "accident claim", "car accident compensation", "motor vehicle accident", "road accident death", "injury compensation"],
            "description": "An application for compensation arising out of an accident involving death of or bodily injury to persons, or damage to any property of a third party, may be made by the injured person or legal representatives of the deceased to the Claims Tribunal having local jurisdiction where accident occurred or where claimant resides.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
            "commencement_date": "1989-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "2019 amendment introduces a 6-month limitation period from accident date for filing claim petition."
        },
        {
            "id": "MVA_161",
            "act_name": "The Motor Vehicles Act, 1988 (as amended in 2019)",
            "section": "Section 161",
            "title": "Special scheme for compensation to victims of hit and run motor accidents",
            "category": CaseCategoryEnum.MOTOR_VEHICLE,
            "keywords": ["hit and run", "unidentified vehicle accident", "hit and run compensation", "solatium fund", "scheme for hit and run"],
            "description": "Provides statutory compensation for death or grievous hurt in hit and run accidents where vehicle identity cannot be ascertained: ₹2 Lakhs in case of death, and ₹50,000 in case of grievous hurt under the Central Government Scheme.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
            "commencement_date": "1989-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Claim submitted to Sub-Divisional Officer / Claims Enquiry Officer in the district."
        },

        # =====================================================================
        # 13. CONSTITUTIONAL & FUNDAMENTAL RIGHTS
        # =====================================================================
        {
            "id": "CONST_21",
            "act_name": "The Constitution of India, 1950",
            "section": "Article 21",
            "title": "Protection of life and personal liberty",
            "category": CaseCategoryEnum.CONSTITUTIONAL,
            "keywords": ["article 21", "fundamental rights", "right to life", "right to privacy", "speedy trial", "clean environment", "human dignity"],
            "description": "No person shall be deprived of his life or personal liberty except according to procedure established by law. Judicially expanded to include right to live with dignity, right to privacy (Puttaswamy 2017), right to clean water/air, right against custodial torture, and right to speedy trial.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1522",
            "commencement_date": "1950-01-26",
            "jurisdiction": "Central",
            "relevance_notes": "The bedrock of Indian human rights jurisprudence enforceable against state action."
        },
        {
            "id": "CONST_32_226",
            "act_name": "The Constitution of India, 1950",
            "section": "Articles 32 & 226",
            "title": "Remedies for enforcement of Fundamental Rights and Writ Jurisdiction",
            "category": CaseCategoryEnum.CONSTITUTIONAL,
            "keywords": ["writ petition", "habeas corpus", "mandamus", "article 226", "article 32", "high court writ", "supreme court writ", "illegal detention"],
            "description": "Article 32 guarantees right to move Supreme Court, and Article 226 empowers High Courts to issue directions, orders, or writs (Habeas Corpus for unlawful detention, Mandamus for public duty, Certiorari, Prohibition, Quo Warranto) for enforcement of rights.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1522",
            "commencement_date": "1950-01-26",
            "jurisdiction": "Central",
            "relevance_notes": "Article 226 has wider reach than Article 32 as High Court can issue writs for fundamental rights as well as ordinary legal rights."
        },

        # =====================================================================
        # 14. TAXATION & REGULATORY MATTERS
        # =====================================================================
        {
            "id": "ITA_148",
            "act_name": "The Income-tax Act, 1961",
            "section": "Section 148 & 148A",
            "title": "Issue of notice where income has escaped assessment and mandatory preliminary enquiry",
            "category": CaseCategoryEnum.TAXATION,
            "keywords": ["income tax notice", "148 notice", "tax scrutiny", "escaped assessment", "148a show cause", "tax assessment"],
            "description": "Before issuing a reassessment notice under Section 148, Assessing Officer must conduct inquiry under Section 148A, provide show-cause notice with information suggesting income escape, give 7 to 30 days to reply, and pass reasoned order with prior sanction.",
            "official_url": "https://incometaxindia.gov.in/",
            "commencement_date": "1962-04-01",
            "jurisdiction": "Central",
            "relevance_notes": "Standard limitation is 3 years from relevant assessment year, extendable up to 10 years only if escaped income exceeds ₹50 Lakhs."
        },
        {
            "id": "RTI_6",
            "act_name": "The Right to Information Act, 2005",
            "section": "Section 6 & 7",
            "title": "Request for obtaining information and disposal of request",
            "category": CaseCategoryEnum.TAXATION,
            "keywords": ["rti application", "right to information", "pio", "file rti", "first appeal rti", "30 days rti", "government information"],
            "description": "A citizen desiring information from a Public Authority may apply in writing or electronically with prescribed fee (₹10). Public Information Officer (PIO) must provide information or reject request within 30 days (within 48 hours where life or liberty of a person is involved).",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2065",
            "commencement_date": "2005-06-15",
            "jurisdiction": "Central / State",
            "relevance_notes": "Right of First Appeal lies before senior officer within 30 days, and Second Appeal before Information Commission within 90 days."
        },

        # =====================================================================
        # 15. INHERITANCE, WILLS & SUCCESSION
        # =====================================================================
        {
            "id": "HSA_6",
            "act_name": "The Hindu Succession Act, 1956",
            "section": "Section 6",
            "title": "Devolution of interest in coparcenary property (Daughter's Equal Rights)",
            "category": CaseCategoryEnum.SUCCESSION,
            "keywords": ["daughter property share", "ancestral property", "coparcenary rights", "hindu succession 2005", "vineeta sharma", "father ancestral property"],
            "description": "In a joint Hindu family governed by Mitakshara law, the daughter of a coparcener becomes a coparcener by birth in her own right in the same manner as the son, with identical rights and liabilities. Affirmed in landmark Supreme Court ruling Vineeta Sharma v. Rakesh Sharma (2020) irrespective of whether father was alive in 2005.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1559",
            "commencement_date": "1956-06-17",
            "jurisdiction": "Central",
            "relevance_notes": "Daughters hold an equal, unalienable birthright in ancestral coparcenary property."
        },
        {
            "id": "ISA_59_63",
            "act_name": "The Indian Succession Act, 1925",
            "section": "Sections 59 & 63",
            "title": "Person capable of making wills and execution of unprivileged wills",
            "category": CaseCategoryEnum.SUCCESSION,
            "keywords": ["will", "making a will", "testamentary succession", "probate", "two witnesses will", "vasiyat", "registered will"],
            "description": "Every person of sound mind not being a minor may dispose of property by will. Section 63 mandates that the testator shall sign the will, and it shall be attested by two or more witnesses, each of whom has seen the testator sign or received personal acknowledgment.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2385",
            "commencement_date": "1925-09-30",
            "jurisdiction": "Central",
            "relevance_notes": "Registration of will is optional under Section 18 of Registration Act, but attestation by two witnesses is mandatory."
        },

        # =====================================================================
        # 16. WOMEN & CHILD PROTECTION
        # =====================================================================
        {
            "id": "POCSO_19",
            "act_name": "Protection of Children from Sexual Offences (POCSO) Act, 2012",
            "section": "Section 19",
            "title": "Recording of information and mandatory reporting of offences",
            "category": CaseCategoryEnum.WOMEN_CHILD,
            "keywords": ["pocso", "child sexual assault", "mandatory reporting", "child abuse", "special juvenile police unit", "child protection"],
            "description": "Mandates that any person (including doctors, teachers, or family) who has apprehension or knowledge that an offence under the Act has been committed shall provide such information to the Special Juvenile Police Unit or local police. Failure to report is punishable under Section 21.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2079",
            "commencement_date": "2012-11-14",
            "jurisdiction": "Central",
            "relevance_notes": "Identity of child victim is protected by law; publication of child identity is an offence under Section 23."
        },
        {
            "id": "DOWRY_3_4",
            "act_name": "The Dowry Prohibition Act, 1961",
            "section": "Sections 3 & 4",
            "title": "Penalty for giving, taking, or demanding dowry",
            "category": CaseCategoryEnum.WOMEN_CHILD,
            "keywords": ["dowry", "dowry demand", "dahej", "dowry harassment", "dowry prohibition", "wedding gift extortion"],
            "description": "Giving, taking, or abetting the giving or taking of dowry is punishable with imprisonment not less than 5 years and fine not less than ₹15,000 or value of dowry. Demanding dowry directly or indirectly is punishable with up to 2 years imprisonment.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1547",
            "commencement_date": "1961-05-20",
            "jurisdiction": "Central",
            "relevance_notes": "Complemented by Section 85/86 of BNS 2023 (formerly Section 498A IPC) for matrimonial cruelty."
        },

        # =====================================================================
        # 17. EDUCATION & SERVICE-RELATED DISPUTES
        # =====================================================================
        {
            "id": "RTE_12",
            "act_name": "The Right of Children to Free and Compulsory Education Act, 2009",
            "section": "Section 12(1)(c)",
            "title": "Mandatory 25% admission quota for disadvantaged groups in private schools",
            "category": CaseCategoryEnum.EDUCATION_SERVICE,
            "keywords": ["rte admission", "25 percent quota", "free school admission", "right to education", "ews admission", "disadvantaged child admission"],
            "description": "Private unaided schools shall admit in class I, to the extent of at least 25 per cent of the strength of that class, children belonging to weaker sections and disadvantaged groups in the neighbourhood and provide free and compulsory elementary education.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2088",
            "commencement_date": "2010-04-01",
            "jurisdiction": "Central",
            "relevance_notes": "State reimburses per-child expenditure incurred by school to the extent of state per-child cost."
        },
        {
            "id": "CAT_19",
            "act_name": "The Administrative Tribunals Act, 1985",
            "section": "Section 19",
            "title": "Applications to Central Administrative Tribunal (CAT) for service matters",
            "category": CaseCategoryEnum.EDUCATION_SERVICE,
            "keywords": ["central administrative tribunal", "cat application", "government employee grievance", "promotion dispute", "pension withheld", "service matter"],
            "description": "A person aggrieved by any order pertaining to any matter within the jurisdiction of a Tribunal (recruitment, promotion, seniority, disciplinary action, pension for central/state government civil servants) may make an application for redressal after exhausting departmental remedies.",
            "official_url": "https://cgat.gov.in/",
            "commencement_date": "1985-07-01",
            "jurisdiction": "Central / State AT",
            "relevance_notes": "Orders of CAT are subject to supervisory writ review before the High Court Division Bench under Art 226 (L. Chandra Kumar 1997 SC)."
        },

        # =====================================================================
        # 18. ENVIRONMENTAL LAW
        # =====================================================================
        {
            "id": "NGT_14_15",
            "act_name": "The National Green Tribunal Act, 2010",
            "section": "Sections 14 & 15",
            "title": "Jurisdiction of the National Green Tribunal and power to grant relief and compensation",
            "category": CaseCategoryEnum.ENVIRONMENTAL,
            "keywords": ["ngt", "national green tribunal", "pollution complaint", "factory smoke", "river pollution", "tree felling", "environmental compensation"],
            "description": "The Tribunal has jurisdiction over all civil cases where a substantial question relating to environment arises out of implementation of Water, Air, and Environment Protection Acts. Empowers Tribunal to grant relief and compensation to victims of pollution and order restitution of environment.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2034",
            "commencement_date": "2010-10-18",
            "jurisdiction": "Central",
            "relevance_notes": "Limitation period is 6 months from the date on which the cause of action first arose, extendable up to 60 days on sufficient cause."
        },

        # =====================================================================
        # 19. FREE LEGAL AID & ACCESS TO JUSTICE
        # =====================================================================
        {
            "id": "NALSA_12",
            "act_name": "The Legal Services Authorities Act, 1987",
            "section": "Section 12",
            "title": "Criteria for giving free legal services",
            "category": CaseCategoryEnum.GENERAL,
            "keywords": ["free legal aid", "nalsa", "dlsa", "free lawyer", "government lawyer", "legal aid for women", "legal aid eligibility"],
            "description": "Guarantees free legal services to women, children, members of Scheduled Castes and Scheduled Tribes, victims of human trafficking or beggar, persons with disabilities, victims of mass disasters/violence, industrial workmen, persons in custody, and citizens with annual income below statutory state limits (₹3 Lakhs in most states).",
            "official_url": "https://nalsa.gov.in/",
            "commencement_date": "1995-11-09",
            "jurisdiction": "Central / State SLSA",
            "relevance_notes": "Available through District Legal Services Authorities (DLSA) in every district court complex across India."
        }
    ]

    @classmethod
    def retrieve_grounded_laws(
        cls,
        text: str,
        category: Optional[CaseCategoryEnum] = None,
        state: Optional[str] = None
    ) -> List[LegalCitation]:
        """
        Retrieves verified statutory citations relevant to the user query and facts.
        Scans all 18+ domains of Indian law using semantic keyword matching,
        category affinity, and state jurisdiction. Never fabricates provisions.
        """
        STOP_WORDS = {
            "in", "on", "at", "to", "for", "of", "and", "or", "the", "a", "an", "is", "was",
            "be", "with", "from", "by", "not", "this", "that", "these", "those", "have", "has",
            "had", "me", "my", "you", "your", "how", "do", "i", "can", "what", "where", "which"
        }
        text_lower = text.lower()
        query_words = set(w for w in re.findall(r"\w+", text_lower) if w not in STOP_WORDS)
        matches: List[Tuple[int, Dict]] = []

        for statute in cls.VERIFIED_STATUTES:
            score = 0
            
            # Exact or specific Category match bonus
            if category and statute["category"] == category:
                score += 5
            
            # State match bonus
            if state and statute.get("jurisdiction") and state.lower() in statute["jurisdiction"].lower():
                score += 5
                
            # Keyword matching
            for kw in statute["keywords"]:
                kw_lower = kw.lower()
                # Direct phrase match
                if kw_lower in text_lower:
                    score += 10
                    continue
                kw_words = [w for w in re.findall(r"\w+", kw_lower) if len(w) >= 3 and w not in STOP_WORDS]
                if not kw_words:
                    continue
                # All words in keyword present in query or subword match
                if all(any(w == qw or (len(w) >= 4 and len(qw) >= 4 and (w in qw or qw in w)) for qw in query_words) for w in kw_words):
                    score += 6
                # Any word in keyword present in query
                elif any(any(w == qw or (len(w) >= 4 and len(qw) >= 4 and (w in qw or qw in w)) for qw in query_words) for w in kw_words):
                    score += 2

            # Act name match bonus
            for act_word in [w for w in re.findall(r"\w+", statute["act_name"].lower()) if len(w) >= 4 and w not in STOP_WORDS]:
                if act_word in text_lower:
                    score += 3

            # Section number match bonus
            sec_num = re.search(r"\b(?:section|sec|order|article|rule)\s*(\d+[a-z]?)", text_lower)
            if sec_num:
                target_sec = sec_num.group(1)
                if target_sec in statute["section"].lower():
                    score += 10

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
                verification_status=VerificationStatusEnum.VERIFIED
            ))

        return citations

    @classmethod
    def verify_citation_claim(cls, act_name: str, section: str) -> Tuple[bool, Optional[LegalCitation], str]:
        """
        Validates if a cited act and section exist in the verified registry.
        Detects hallucinated or invented citations (e.g. Section 999).
        """
        act_clean = act_name.strip().lower()
        sec_clean = section.strip().lower()

        for s in cls.VERIFIED_STATUTES:
            if sec_clean in s["section"].lower() and any(w in s["act_name"].lower() for w in act_clean.split() if len(w) > 3):
                citation = LegalCitation(
                    act_name=s["act_name"],
                    section=s["section"],
                    title=s["title"],
                    description=s["description"],
                    official_url=s["official_url"],
                    commencement_date=s.get("commencement_date"),
                    jurisdiction=s["jurisdiction"],
                    verification_status=VerificationStatusEnum.VERIFIED
                )
                return (True, citation, "Verified in official statutory registry.")

        return (
            False,
            None,
            f"Unverified or non-existent section: '{section}' of '{act_name}'. LawPilot AI does not invent or confirm unverified legal provisions."
        )
