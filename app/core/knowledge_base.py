import re
from typing import List, Dict, Optional, Tuple
from app.models.schemas import LegalCitation, VerificationStatusEnum, CaseCategoryEnum

class LegalKnowledgeBase:
    """
    Verified Indian Statutory Knowledge Base and Anti-Hallucination Retrieval Engine.
    Grounds all legal analysis directly in verified Indian statutes, official portals,
    and established procedural legal frameworks.
    """
    
    # Official Government & Judicial Portals
    OFFICIAL_PORTALS = {
        "india_code": "https://www.indiacode.nic.in/",
        "consumer_affairs": "https://consumeraffairs.nic.in/",
        "consumer_helpline": "https://consumerhelpline.gov.in/",
        "nalsa": "https://nalsa.gov.in/",
        "ecourts": "https://ecourts.gov.in/",
        "shram_suvidha": "https://shramsuvidha.gov.in/"
    }

    # Verified Statutory Provisions Database
    VERIFIED_STATUTES: List[Dict] = [
        # --- TENANT & LANDLORD DISPUTES ---
        {
            "id": "TPA_106",
            "act_name": "The Transfer of Property Act, 1882",
            "section": "Section 106",
            "title": "Duration of certain leases in absence of written contract or local usage",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["notice period", "eviction", "termination", "15 days notice", "lease duration", "oral tenancy", "no agreement"],
            "description": "In the absence of a contract or local law to the contrary, a lease of immovable property for other than agricultural or manufacturing purposes is deemed to be month-to-month, terminable on 15 days' notice expiring with the end of a month of the tenancy.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2338?view_type=browse&sam_handle=123456789/1362",
            "commencement_date": "1882-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Applies where there is no registered agreement or where state rent control does not apply. Requires proper formal notice before any eviction can be sought."
        },
        {
            "id": "TPA_108",
            "act_name": "The Transfer of Property Act, 1882",
            "section": "Section 108(m) & (o)",
            "title": "Rights and liabilities of lessor and lessee - Repairs and Reasonable Wear and Tear",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["painting", "deduction", "wear and tear", "repairs", "maintenance", "security deposit", "damage"],
            "description": "Lessee is bound to keep and restore the property in as good condition as it was at the time he was put in possession, subject only to reasonable wear and tear and irresistible force. Landlord cannot make arbitrary deductions for normal usage painting without explicit contractual basis.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2338?view_type=browse&sam_handle=123456789/1362",
            "commencement_date": "1882-07-01",
            "jurisdiction": "Central",
            "relevance_notes": "Crucial protection against arbitrary security deposit deductions for standard repainting or normal weathering."
        },
        {
            "id": "MTA_2021_SEC11",
            "act_name": "Model Tenancy Act, 2021 (Guidelines & State Enactments)",
            "section": "Section 11 & Section 13",
            "title": "Cap on Security Deposit and Condition for Deductions",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["security deposit", "deposit refund", "maximum deposit", "deduction", "handover"],
            "description": "Limits security deposit for residential premises to a maximum of two months' rent. Requires refund of security deposit to the tenant at the time of taking over vacant possession of the premises, after making valid deductions agreed under the tenancy agreement.",
            "official_url": "https://mohua.gov.in/upload/uploadfiles/files/Model_Tenancy_Act_English.pdf",
            "commencement_date": "2021-06-02",
            "jurisdiction": "Model Central Act (Adopted by States such as AP, TN, UP)",
            "relevance_notes": "Statutory benchmark used by Rent Authorities and civil courts regarding fair return of security deposit."
        },
        {
            "id": "SRA_SEC6",
            "act_name": "The Specific Relief Act, 1963",
            "section": "Section 6",
            "title": "Suit by person dispossessed of immovable property without due process",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["eviction", "threat", "forceful eviction", "locks changed", "whatsapp threat", "dispossession", "police"],
            "description": "If any person is dispossessed without his consent of immovable property otherwise than in due course of law, he or any person claiming through him may, by suit, recover possession thereof notwithstanding any other title that may be set up.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1583",
            "commencement_date": "1964-03-01",
            "jurisdiction": "Central",
            "relevance_notes": "A landlord CANNOT unilaterally disconnect water/electricity or throw out tenant's belongings without a court order."
        },
        {
            "id": "MAHA_RENT_1999",
            "act_name": "Maharashtra Rent Control Act, 1999",
            "section": "Section 15 & Section 29",
            "title": "Relief against forfeiture and prohibition against cutting off essential supplies",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["maharashtra", "mumbai", "pune", "water cut", "electricity cut", "essential services", "eviction"],
            "description": "No landlord shall without just or sufficient cause cut off or withhold any essential supply or service (water, electricity, lifts) enjoyed by the tenant. Violation is punishable with imprisonment or fine.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2513",
            "commencement_date": "2000-03-31",
            "jurisdiction": "State: Maharashtra",
            "relevance_notes": "State-specific protection for tenants residing in Maharashtra."
        },
        {
            "id": "DELHI_RENT_1958",
            "act_name": "Delhi Rent Control Act, 1958",
            "section": "Section 14 & Section 45",
            "title": "Protection of tenant against eviction and restoration of essential amenities",
            "category": CaseCategoryEnum.TENANT,
            "keywords": ["delhi", "ncr", "essential supply", "eviction protection", "rent controller"],
            "description": "Strict grounds required for eviction; prohibits withholding essential amenities without reasonable cause. Tenant may approach Rent Controller for summary restoration.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/1393",
            "commencement_date": "1959-02-09",
            "jurisdiction": "State: Delhi (NCT)",
            "relevance_notes": "Applicable to tenancies in notified areas of Delhi within statutory rent thresholds."
        },

        # --- CONSUMER PROTECTION ---
        {
            "id": "CPA_2019_SEC2_7",
            "act_name": "The Consumer Protection Act, 2019",
            "section": "Section 2(7)",
            "title": "Definition of Consumer (Including E-commerce and Offline Purchases)",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["consumer", "buyer", "online purchase", "flipkart", "amazon", "e-commerce", "offline store"],
            "description": "Defines a consumer as any person who buys goods or hires/avails any services for a consideration paid or promised, including offline or online transactions through electronic means or by teleshopping or direct selling.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
            "commencement_date": "2020-07-20",
            "jurisdiction": "Central",
            "relevance_notes": "Confirms standing to seek redressal for online shopping, apps, and digital services."
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
            "relevance_notes": "Direct legal basis for mandating refund/replacement for defective smartphones, electronics, or wrong deliveries."
        },
        {
            "id": "CPA_2019_SEC35",
            "act_name": "The Consumer Protection Act, 2019",
            "section": "Section 35 & Section 38",
            "title": "Manner in which complaint shall be made and Procedure before District Commission",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["consumer court", "district commission", "file complaint", "edaakhil", "pecuniary jurisdiction"],
            "description": "A complaint in relation to any goods sold or delivered or agreed to be sold or delivered or any service provided or agreed to be provided may be filed with a District Commission by the consumer, including online through the e-Daakhil portal.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
            "commencement_date": "2020-07-20",
            "jurisdiction": "Central",
            "relevance_notes": "Allows direct electronic filing without advocate mandatory appearance up to statutory pecuniary jurisdiction."
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
            "relevance_notes": "Mandates platforms to resolve delivery failures and refund delays systematically."
        },
        {
            "id": "NCH_PORTAL",
            "act_name": "National Consumer Helpline (Department of Consumer Affairs)",
            "section": "Portal & Toll-Free 1915 Redressal Process",
            "title": "Pre-litigation Conciliation and Dispute Resolution via NCH / INGRAM",
            "category": CaseCategoryEnum.CONSUMER,
            "keywords": ["1915", "national consumer helpline", "ingram", "pre-litigation", "complaint docket"],
            "description": "Official Department of Consumer Affairs portal (https://consumerhelpline.gov.in) enabling consumers to register grievances against registered convergence companies for quick pre-litigation resolution.",
            "official_url": "https://consumerhelpline.gov.in/",
            "commencement_date": "Continuous Service",
            "jurisdiction": "Central",
            "relevance_notes": "Recommended first step before filing a formal case in consumer commission."
        },

        # --- EMPLOYMENT & SALARY ISSUES ---
        {
            "id": "PWA_1936_SEC5",
            "act_name": "The Payment of Wages Act, 1936",
            "section": "Section 5 & Section 15",
            "title": "Time of payment of wages and Claims arising out of deductions from wages or delay in payment",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["unpaid salary", "delayed salary", "wages", "7th day", "10th day", "salary dues", "claim"],
            "description": "Wages must be paid before the expiry of the 7th day after the wage period (or 10th day if more than 1,000 persons employed). Section 15 provides for application to the designated Authority for delayed wages with compensation up to ten times the amount deducted/delayed.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2405",
            "commencement_date": "1937-03-28",
            "jurisdiction": "Central",
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
            "relevance_notes": "Protects against mysterious deductions from final settlement / full and final (FnF) statement."
        },
        {
            "id": "SHOPS_EST_ACT",
            "act_name": "State Shops and Commercial Establishments Acts",
            "section": "Settlement of Dues and Service Conditions Provision",
            "title": "Statutory Payment of Earned Salary and Notice Pay for Private/Commercial Employees",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["private company", "it employee", "shops and establishments", "settlement", "relieving letter", "resignation"],
            "description": "State-specific legislation (e.g., Delhi Shops Act, Karnataka Shops & Commercial Establishments Act, Maharashtra Shops Act) governing commercial and IT/office establishments. Mandates clearance of earned wages and final settlement upon termination or resignation within 3 to 15 days.",
            "official_url": "https://shramsuvidha.gov.in/",
            "commencement_date": "State Specific",
            "jurisdiction": "State Specific",
            "relevance_notes": "Directly covers corporate, IT, startup, and private commercial office employees."
        },
        {
            "id": "ICA_1872_SEC73",
            "act_name": "The Indian Contract Act, 1872",
            "section": "Section 73",
            "title": "Compensation for loss or damage caused by breach of contract",
            "category": CaseCategoryEnum.EMPLOYMENT,
            "keywords": ["employment contract", "offer letter", "oral contract", "bank statement", "salary slips", "breach of contract"],
            "description": "When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, compensation for any loss or damage caused to him thereby.",
            "official_url": "https://www.indiacode.nic.in/handle/123456789/2187",
            "commencement_date": "1872-09-01",
            "jurisdiction": "Central",
            "relevance_notes": "Applies where appointment letter or oral contract is substantiated through salary slips and bank transfers."
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
            "jurisdiction": "Central",
            "relevance_notes": "Statutory recovery forum for employees classified as workmen."
        },

        # --- ACCESS TO JUSTICE & LEGAL AID ---
        {
            "id": "NALSA_1987_SEC12",
            "act_name": "The Legal Services Authorities Act, 1987",
            "section": "Section 12",
            "title": "Criteria for giving legal services (Free Legal Aid via NALSA / SLSA / DLSA)",
            "category": CaseCategoryEnum.GENERAL,
            "keywords": ["legal aid", "free lawyer", "nalsa", "dlsa", "15100", "marginalized", "low income"],
            "description": "Provides free competent legal services to eligible persons, including women, children, industrial workmen, and persons with annual income below specified statutory thresholds.",
            "official_url": "https://nalsa.gov.in/",
            "commencement_date": "1995-11-09",
            "jurisdiction": "Central / All India",
            "relevance_notes": "Citizens facing financial hardship can access free appointed legal counsel via DLSA."
        }
    ]

    @classmethod
    def retrieve_grounded_laws(cls, text: str, category: Optional[CaseCategoryEnum] = None, state: Optional[str] = None) -> List[LegalCitation]:
        """
        Retrieves verified statutory citations relevant to the user query and facts.
        Never fabricates provisions.
        """
        query_words = set(re.findall(r"\w+", text.lower()))
        matches: List[Tuple[int, Dict]] = []

        for statute in cls.VERIFIED_STATUTES:
            score = 0
            # Category match bonus
            if category and statute["category"] == category:
                score += 3
            
            # State match
            if state and state.lower() in statute["jurisdiction"].lower():
                score += 5
                
            # Keyword matching
            for kw in statute["keywords"]:
                kw_words = set(re.findall(r"\w+", kw.lower()))
                if kw_words.issubset(query_words):
                    score += 4
                elif any(w in query_words for w in kw_words):
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
                verification_status=VerificationStatusEnum.VERIFIED
            ))

        return citations

    @classmethod
    def verify_citation_claim(cls, act_name: str, section: str) -> Tuple[bool, Optional[LegalCitation], str]:
        """
        Validates if a cited act and section exist in the verified registry.
        Detects hallucinated or invented citations (e.g. Test A1, A9).
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
                    verification_status=VerificationStatusEnum.VERIFIED
                )
                return (True, citation, "Verified in official statutory registry.")

        return (
            False,
            None,
            f"Unverified or non-existent section: '{section}' of '{act_name}'. LawPilot AI does not invent or confirm unverified legal provisions."
        )
