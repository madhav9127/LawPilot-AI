import re
from typing import Tuple, List, Dict
from app.models.schemas import EscalationAlert

class EscalationDetector:
    """
    Detects critical legal emergencies, approaching court limitation deadlines,
    criminal threats, violence, summons, or urgent evictions.
    Directs the user to qualified advocates and official helplines immediately.
    """
    
    STANDARD_DISCLAIMER = (
        "LawPilot AI provides general legal information and assistance. "
        "It is not a substitute for advice from a qualified advocate. "
        "Legal outcomes depend on the facts, applicable laws and jurisdiction."
    )

    CRITICAL_PATTERNS = [
        (r"\b(summons|subpoena|court notice|bailable warrant|non-bailable warrant|nbw)\b", "Court summons or legal warrant received requiring immediate formal response."),
        (r"\b(hearing tomorrow|hearing in \d+ days|deadline expires|limitation period expires|last date to appeal)\b", "Approaching court limitation or appearance deadline."),
        (r"\b(threaten(ed|ing)?\s+(violence|kill|harm|beat|assault)|physical force|hit me|break my legs)\b", "Threat of physical violence or safety concern."),
        (r"\b(arrest(ed)?|police station|fir filed|police custody|custodial|jail|criminal complaint)\b", "Criminal proceedings or imminent arrest risk."),
        (r"\b(locked out|threw (my )?(bags|luggage|belongings)|cut electricity|cut water|thug|goons|bouncers)\b", "Urgent illegal dispossession or physical eviction without due process."),
    ]

    HIGH_RISK_PATTERNS = [
        (r"\b(crore|lakhs? of rupees|high value dispute)\b", "High financial exposure or complex commercial liability."),
        (r"\b(fraud|cheating|forgery|sec 420|extortion)\b", "Potential criminal allegations intersecting civil dispute."),
    ]

    OFFICIAL_HELPLINES = [
        {"name": "National Legal Services Authority (NALSA) Free Legal Aid Helpline", "number": "15100", "description": "Free legal aid for eligible citizens (women, workers, economically weaker sections)"},
        {"name": "National Emergency Response Support System (ERSS)", "number": "112", "description": "Immediate police and emergency safety assistance"},
        {"name": "National Consumer Helpline (NCH)", "number": "1915", "description": "Department of Consumer Affairs grievance helpline"},
        {"name": "Women Helpline (All India)", "number": "1091", "description": "24x7 helpline for women in distress or facing threats"}
    ]

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

        # Check high
        if urgency != "critical":
            for pattern, reason in cls.HIGH_RISK_PATTERNS:
                if re.search(pattern, lower_text):
                    reasons.append(reason)
                    urgency = "high"

        if reasons:
            if urgency == "critical":
                recommendation = (
                    "URGENT: This situation involves critical legal or safety risks (such as approaching court deadlines, "
                    "formal summons, criminal threats, or illegal physical force). Automated legal guidance is insufficient. "
                    "You must consult a licensed advocate immediately or contact local authorities."
                )
            else:
                recommendation = (
                    "ATTENTION: Your matter involves significant risks or potential statutory complexity. "
                    "While LawPilot AI can assist with procedural drafts and facts, we strongly advise having an advocate review your documents."
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
