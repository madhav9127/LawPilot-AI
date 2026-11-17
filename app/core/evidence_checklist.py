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
