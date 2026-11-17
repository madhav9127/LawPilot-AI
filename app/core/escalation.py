import re
from typing import Tuple, List, Dict, Optional
from app.models.schemas import EscalationAlert

class EscalationDetector:
    """
    Detects critical emergencies, medical crises, safety threats,
    fraud requests, and approaching court limitation deadlines.
    """
    
    STANDARD_DISCLAIMER = (
        "LawPilot AI provides general legal information and assistance. "
        "It is not a substitute for advice from a qualified advocate. "
        "Legal outcomes depend on the facts, applicable laws and jurisdiction."
    )

    # 1. MEDICAL EMERGENCY PATTERNS
    MEDICAL_PATTERNS = [
        r"\b(chest pain|heart attack|difficulty breathing|shortness of breath|bleeding heavily|unconscious|stroke|poison|overdose|choking|suicide|kill myself|dying)\b"
    ]

    # 2. FRAUD / FORGERY FABRICATION PATTERNS
    FRAUD_PATTERNS = [
        r"\b(create|make|fake|forge|fabricate)\s+(?:fake\s+|forged\s+)?(?:salary slips?|payslips?|bank statements?|invoices?|documents?|bills?|signatures?)\b",
        r"\b(help me (?:create|forge|fake))\b"
    ]

    # 3. URGENT LEGAL & SAFETY PATTERNS
    CRITICAL_PATTERNS = [
        (r"\b(summons|subpoena|court notice|bailable warrant|non-bailable warrant|nbw)\b", "Court summons or legal warrant received requiring immediate formal response."),
        (r"\b(hearing tomorrow|hearing in \d+ days|deadline expires|limitation period expires|last date to appeal)\b", "Approaching court limitation or appearance deadline."),
        (r"\b(threaten(ed|ing)?\s+(violence|kill|harm|beat|assault)|physical force|hit me|break my legs|goons|bouncers)\b", "Threat of physical violence or safety concern."),
        (r"\b(arrest(ed)?|police station|fir filed|police custody|custodial|jail|criminal complaint)\b", "Criminal proceedings or imminent arrest risk."),
        (r"\b(locked out|threw (my )?(bags|luggage|belongings)|cut electricity|cut water|leave tomorrow)\b", "Urgent unlawful eviction, lockout, or utility disconnection without due process.")
    ]

    OFFICIAL_HELPLINES = [
        {"name": "National Emergency Response Support System (Police/Fire/Emergency)", "number": "112", "description": "Immediate police and emergency safety assistance"},
        {"name": "National Ambulance / Medical Emergency", "number": "108 / 102", "description": "Emergency ambulance and hospital assistance"},
        {"name": "National Legal Services Authority (NALSA) Free Legal Aid Helpline", "number": "15100", "description": "Free legal aid for eligible citizens"},
        {"name": "National Consumer Helpline (NCH)", "number": "1915", "description": "Department of Consumer Affairs grievance helpline"},
        {"name": "Women Helpline (All India)", "number": "1091", "description": "24x7 helpline for women in distress"}
    ]

    @classmethod
    def check_medical_emergency(cls, text: str) -> Tuple[bool, Optional[str]]:
        """Detects medical life-threatening emergencies."""
        lower = text.lower()
        for p in cls.MEDICAL_PATTERNS:
            if re.search(p, lower):
                return True, (
                    "🚨 **MEDICAL EMERGENCY ALERT**\n\n"
                    "This appears to be a medical emergency requiring immediate medical attention. "
                    "LawPilot AI provides legal information only and cannot provide medical assistance.\n\n"
                    "**PLEASE CALL EMERGENCY SERVICES IMMEDIATELY:**\n"
                    "- **Ambulance / Medical Emergency:** Dial **108** or **102**\n"
                    "- **National Emergency Number (All India):** Dial **112**\n\n"
                    "Please proceed to the nearest hospital emergency room without delay."
                )
        return False, None

    @classmethod
    def check_fraud_request(cls, text: str) -> Tuple[bool, Optional[str]]:
        """Detects requests to forge or fabricate documents/evidence."""
        lower = text.lower()
        for p in cls.FRAUD_PATTERNS:
            if re.search(p, lower):
                return True, (
                    "🛑 **Refusal to Assist with Document Fabrication**\n\n"
                    "LawPilot AI strictly refuses to create, forge, or fabricate false salary slips, bank statements, "
                    "or any counterfeit documents. Under Sections 463, 465, and 471 of the Indian Penal Code (Sections 336 & 340 of Bharatiya Nyaya Sanhita, 2023), "
                    "forgery and presenting forged documents before any employer or court is a serious criminal offence.\n\n"
                    "**Legitimate Alternatives:**\n"
                    "- Use genuine secondary proofs such as official bank account credit statements.\n"
                    "- Provide email communication trails with HR or supervisors.\n"
                    "- Under Indian law, oral employment can be legitimately established through genuine transaction histories and work communications without fabricating documents."
                )
        return False, None

    @classmethod
    def analyze(cls, text: str) -> EscalationAlert:
        """Analyzes text for legal urgency and escalation criteria."""
        lower_text = text.lower()
        reasons: List[str] = []
        urgency = "low"

        # Check critical
        for pattern, reason in cls.CRITICAL_PATTERNS:
            if re.search(pattern, lower_text):
                reasons.append(reason)
                urgency = "critical"

        if reasons:
            recommendation = (
                "URGENT: This situation involves critical legal or safety risks (such as approaching court deadlines, "
                "formal summons, criminal threats, or illegal physical force). Automated legal guidance is insufficient. "
                "You must consult a licensed advocate immediately or contact local authorities."
            )
            return EscalationAlert(
                is_escalated=True,
                urgency_level=urgency,
                reasons=reasons,
                recommended_action=recommendation,
                helplines=cls.OFFICIAL_HELPLINES
            )

        return EscalationAlert(
            is_escalated=False,
            urgency_level="low",
            reasons=[],
            recommended_action="Standard automated guidance applicable. Always consult an advocate for formal proceedings.",
            helplines=[]
        )
