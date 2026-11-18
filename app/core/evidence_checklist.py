from typing import List, Dict
from app.models.schemas import EvidenceItem, CaseCategoryEnum, EvidenceStatusEnum

class EvidenceChecklistManager:
    """
    Generates dynamic evidence checklists tailored to the legal category,
    explaining statutory importance under Indian Evidence Act, 1872 / BSA, 2023.
    """

    TENANT_EVIDENCE: List[Dict] = [
        {
            "id": "ten_1",
            "name": "Rental / Lease Agreement",
            "category": "Contractual Standing",
            "legal_importance": "Crucial to establish the agreed monthly rent, initial security deposit amount, lock-in period, and notice period terms.",
            "description": "Registered or notarized agreement; even an expired agreement establishes terms of tenancy."
        },
        {
            "id": "ten_2",
            "name": "Deposit Payment Proof",
            "category": "Financial Transaction",
            "legal_importance": "Indisputable evidence that the landlord received the deposit funds.",
            "description": "Bank transfer receipt (NEFT/RTGS/UPI), cheque counterfoil, or signed cash receipt."
        },
        {
            "id": "ten_3",
            "name": "Bank Account Statements",
            "category": "Financial Trail",
            "legal_importance": "Corroborates regular rent payments and absence of rent arrears.",
            "description": "Monthly bank statements covering the tenancy duration showing regular rent debits."
        },
        {
            "id": "ten_4",
            "name": "Move-out & Handover Photographs/Video",
            "category": "Physical Condition",
            "legal_importance": "Rebuts false landlord claims of tenant damage or abnormal wear & tear.",
            "description": "Date-stamped photos or video walkthrough taken upon vacating and handing over keys."
        },
        {
            "id": "ten_5",
            "name": "Notice of Move-out / Email Correspondence",
            "category": "Procedural Compliance",
            "legal_importance": "Proves that the tenant fulfilled the contractual or statutory 15/30 days notice requirement.",
            "description": "Emails, written letters, or registered post slips notifying intent to vacate."
        },
        {
            "id": "ten_6",
            "name": "WhatsApp / SMS Chat Records",
            "category": "Electronic Evidence",
            "legal_importance": "Admissible under Section 65B of Indian Evidence Act (BSA Section 63) to prove admissions of refund liability or inspection acknowledgements.",
            "description": "Exported chat history with phone numbers clearly visible."
        }
    ]

    CONSUMER_EVIDENCE: List[Dict] = [
        {
            "id": "con_1",
            "name": "GST Tax Invoice / Cash Memo",
            "category": "Proof of Purchase",
            "legal_importance": "Establishes legal consumer relationship under CPA 2019 Section 2(7) and exact consideration paid.",
            "description": "Official seller invoice with GSTIN, product description, and date."
        },
        {
            "id": "con_2",
            "name": "Order Confirmation & Tracking Record",
            "category": "Transaction History",
            "legal_importance": "Demonstrates delivery timelines, promised delivery date, and order specifics.",
            "description": "Order details page, shipment confirmation, or courier tracking screenshot."
        },
        {
            "id": "con_3",
            "name": "Bank / UPI / Card Transaction Receipt",
            "category": "Payment Record",
            "legal_importance": "Establishes actual deduction from consumer's account and merchant account receipt.",
            "description": "Payment gateway confirmation, UPI transaction ID, or bank debit advice."
        },
        {
            "id": "con_4",
            "name": "Photographs / Unboxing Video of Defect or Wrong Item",
            "category": "Product Condition",
            "legal_importance": "Direct prima facie evidence of defective goods or delivery of wrong/counterfeit item.",
            "description": "High-resolution photos showing defect, serial number, or wrong package contents."
        },
        {
            "id": "con_5",
            "name": "Customer Support Tickets & Complaint Reference IDs",
            "category": "Pre-litigation Redressal",
            "legal_importance": "Proves that consumer gave reasonable opportunity to the seller/platform before approaching court.",
            "description": "Support chat logs, grievance ticket numbers, and automated acknowledgment emails."
        },
        {
            "id": "con_6",
            "name": "National Consumer Helpline (NCH) Docket",
            "category": "Regulatory Conciliation",
            "legal_importance": "Records pre-litigation conciliation status; useful when submitting before District Commission.",
            "description": "NCH complaint docket number and company response history from consumerhelpline.gov.in."
        }
    ]

    EMPLOYMENT_EVIDENCE: List[Dict] = [
        {
            "id": "emp_1",
            "name": "Appointment Letter / Employment Agreement",
            "category": "Contractual Basis",
            "legal_importance": "Establishes employer-employee relationship, agreed monthly remuneration, role, and notice terms.",
            "description": "Signed offer letter, employment contract, or formal onboarding email."
        },
        {
            "id": "emp_2",
            "name": "Salary Slips (Last 3 to 6 Months)",
            "category": "Wage Documentation",
            "legal_importance": "Conclusive evidence of monthly gross/net earnings, basic wage components, and habitual deductions.",
            "description": "Authorized monthly payslips issued by HR or payroll portal."
        },
        {
            "id": "emp_3",
            "name": "Bank Account Statements Showing Salary Credits",
            "category": "Financial Evidence",
            "legal_importance": "Proves customary salary payment dates and highlights the exact months where salary was withheld or delayed.",
            "description": "Bank account statement showing regular monthly credit history and subsequent stoppage."
        },
        {
            "id": "emp_4",
            "name": "Attendance Logs / Timesheets / Biometric Records",
            "category": "Proof of Service Rendered",
            "legal_importance": "Rebuts false employer allegations of unauthorized absence or abandonment of duty.",
            "description": "Biometric logs, daily timesheet approvals, login records, or client email trails."
        },
        {
            "id": "emp_5",
            "name": "Formal Resignation Email & Acceptance Confirmation",
            "category": "Separation Protocol",
            "legal_importance": "Proves lawful service of notice period and clean exit under employment terms.",
            "description": "Resignation email, manager/HR acceptance, or handover completion sign-off."
        },
        {
            "id": "emp_6",
            "name": "Written Demands for Full & Final (FnF) Settlement",
            "category": "Notice of Dues",
            "legal_importance": "Proves demand for unpaid salary and establishes the employer's failure or refusal to clear statutory dues.",
            "description": "Sent reminder emails, follow-up messages to finance/HR, or formal demand letters."
        }
    ]

    CYBER_EVIDENCE: List[Dict] = [
        {
            "id": "cyb_1",
            "name": "Bank / UPI Transaction Reference & SMS Alerts",
            "category": "Financial Trail",
            "legal_importance": "Critical to establish UPI reference number (UTR), debit timestamp, and beneficiary account.",
            "description": "Bank transaction statement showing debit, UTR number, and SMS received from bank."
        },
        {
            "id": "cyb_2",
            "name": "Screenshots of Fraudulent Chat & Link",
            "category": "Digital Evidence",
            "legal_importance": "Admissible under Section 63 BSA 2023 / Section 65B IEA to prove inducement and cyber communication.",
            "description": "Unedited screenshots of WhatsApp, Telegram, email, or phishing link showing sender phone/ID."
        },
        {
            "id": "cyb_3",
            "name": "National Cybercrime Portal / 1930 Acknowledgement",
            "category": "Official Intimation",
            "legal_importance": "Proves immediate intimation within the golden hour enabling account freeze.",
            "description": "Acknowledgement number generated by 1930 helpline or cybercrime.gov.in complaint receipt."
        }
    ]

    BANKING_EVIDENCE: List[Dict] = [
        {
            "id": "bnk_1",
            "name": "Original Cheque & Bank Return Memo",
            "category": "Statutory Instrument",
            "legal_importance": "Foundational requirement under Section 138 NI Act proving dishonour for 'Funds Insufficient'.",
            "description": "Original dishonoured cheque and the signed return memo issued by the drawee bank."
        },
        {
            "id": "bnk_2",
            "name": "Statutory 15-Day Demand Notice & Speed Post Receipt",
            "category": "Pre-litigation Notice",
            "legal_importance": "Mandatory under Section 138 proviso (b); proves service within 30 days of dishonour memo.",
            "description": "Copy of formal demand notice with India Post speed post receipt and online delivery tracking report."
        },
        {
            "id": "bnk_3",
            "name": "Account Statement & Underlying Debt Agreement",
            "category": "Legally Enforceable Debt",
            "legal_importance": "Proves cheque was issued for discharge of a legally enforceable debt or liability.",
            "description": "Invoice, loan agreement, promissory note, or ledger account showing transaction history."
        }
    ]

    PROPERTY_EVIDENCE: List[Dict] = [
        {
            "id": "prop_1",
            "name": "Builder-Buyer Agreement (BBA) / Registered Allotment Letter",
            "category": "Contractual Commitment",
            "legal_importance": "Establishes committed possession date, grace period, and payment milestones under RERA Section 18.",
            "description": "Executed agreement with promoter specifying flat/unit number, total consideration, and delivery schedule."
        },
        {
            "id": "prop_2",
            "name": "Payment Receipts & Bank Home Loan Disbursal Trail",
            "category": "Financial Consideration",
            "legal_importance": "Proves payment of earnest money, stage-wise installments, and interest calculation.",
            "description": "All builder payment receipts, demand letters paid, and home loan statement of accounts."
        },
        {
            "id": "prop_3",
            "name": "Written Communications Regarding Construction Delay",
            "category": "Breach Notice",
            "legal_importance": "Demonstrates allottee's ongoing inquiry and promoter's failure to deliver within agreed schedule.",
            "description": "Email correspondence, letters, and site photographs showing incomplete construction."
        }
    ]

    FAMILY_EVIDENCE: List[Dict] = [
        {
            "id": "fam_1",
            "name": "Marriage Certificate / Wedding Invitation & Photographs",
            "category": "Marital Status",
            "legal_importance": "Statutory proof of marriage under Section 8 Hindu Marriage Act or Special Marriage Act.",
            "description": "Government marriage registration certificate, or wedding card and ceremonial photographs."
        },
        {
            "id": "fam_2",
            "name": "Income Affidavits & Bank Statements (Per Rajnesh v. Neha Guidelines)",
            "category": "Financial Capability",
            "legal_importance": "Supreme Court mandated disclosure of assets and liabilities to calculate equitable maintenance.",
            "description": "3 years ITR returns, salary slips, bank statements, and asset/liability affidavit."
        },
        {
            "id": "fam_3",
            "name": "Incident Documentation / Police or Protection Officer Reports",
            "category": "Cruelty or Domestic Violence",
            "legal_importance": "Corroborates claims of domestic cruelty or harassment under Section 12 PWDVA or HMA Sec 13.",
            "description": "Medical prescription records, police complaints, photographs of injuries, or audio/video recordings."
        }
    ]

    MOTOR_VEHICLE_EVIDENCE: List[Dict] = [
        {
            "id": "mva_1",
            "name": "Certified Copy of Police FIR & Site Panchanama",
            "category": "Police Investigation",
            "legal_importance": "Primary document for MACT claim establishing vehicle involvement, driver identity, and date/place.",
            "description": "Certified FIR copy, charge sheet, and site inspection report (panchanama) from police station."
        },
        {
            "id": "mva_2",
            "name": "Medico-Legal Certificate (MLC) & Original Medical Bills",
            "category": "Injury & Treatment",
            "legal_importance": "Proves nature of injuries, disability percentage, and out-of-pocket medical expenditures.",
            "description": "Hospital discharge summary, MLC report, disability certificate, and all original medical bills."
        },
        {
            "id": "mva_3",
            "name": "Offending Vehicle Insurance Policy & Registration Certificate",
            "category": "Insurer Liability",
            "legal_importance": "Identifies insurance company liable to indemnify the award under Section 149 MVA.",
            "description": "Copy of vehicle insurance cover note, RC copy, and driver's driving licence."
        }
    ]

    @classmethod
    def get_checklist_for_category(cls, category: CaseCategoryEnum) -> List[EvidenceItem]:
        """Returns standard evidence items for the category with default pending status."""
        raw_items = []
        if category == CaseCategoryEnum.TENANT:
            raw_items = cls.TENANT_EVIDENCE
        elif category == CaseCategoryEnum.CONSUMER:
            raw_items = cls.CONSUMER_EVIDENCE
        elif category == CaseCategoryEnum.EMPLOYMENT:
            raw_items = cls.EMPLOYMENT_EVIDENCE
        elif category == CaseCategoryEnum.CYBER:
            raw_items = cls.CYBER_EVIDENCE
        elif category == CaseCategoryEnum.BANKING:
            raw_items = cls.BANKING_EVIDENCE
        elif category == CaseCategoryEnum.PROPERTY:
            raw_items = cls.PROPERTY_EVIDENCE
        elif category == CaseCategoryEnum.FAMILY:
            raw_items = cls.FAMILY_EVIDENCE
        elif category == CaseCategoryEnum.MOTOR_VEHICLE:
            raw_items = cls.MOTOR_VEHICLE_EVIDENCE
        else:
            raw_items = cls.TENANT_EVIDENCE[:2] + cls.CONSUMER_EVIDENCE[:2] + cls.EMPLOYMENT_EVIDENCE[:2]

        return [
            EvidenceItem(
                id=item["id"],
                name=item["name"],
                category=item["category"],
                status=EvidenceStatusEnum.PENDING,
                legal_importance=item["legal_importance"],
                description=item["description"]
            )
            for item in raw_items
        ]
