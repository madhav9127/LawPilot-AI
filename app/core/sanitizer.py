import re
from typing import Tuple, List

class Sanitizer:
    """
    Sanitizes user input and uploaded documents to prevent:
    1. Prompt injection / instruction overrides
    2. Cross-site scripting (XSS)
    3. Adversarial attempts to force hallucinated legal provisions or guarantees
    """
    
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"disregard\s+(all\s+)?(previous|prior)\s+rules",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"system\s*override",
        r"jailbreak",
        r"override\s+legal\s+rules",
        r"forget\s+everything",
        r"act\s+as\s+an\s+unrestricted",
        r"simulate\s+being\s+a\s+judge\s+who\s+guarantees",
        r"dan\s+mode",
    ]
    
    VICTORY_GUARANTEE_PATTERNS = [
        r"guarantee\s+(?:me\s+)?(?:a\s+)?(?:100%\s+)?(?:court\s+)?(?:win|victory|success)",
        r"promise\s+(?:that\s+)?i\s+will\s+win",
        r"can\s+you\s+guarantee\s+(?:a\s+)?100%",
        r"assure\s+me\s+i\s+will\s+definitely\s+win",
        r"100%\s+(?:court\s+)?(?:win|victory)",
    ]
    
    FABRICATION_REQUEST_PATTERNS = [
        r"invent\s+(?:a\s+)?(?:fake\s+|fictional\s+|legal\s+|new\s+)?(?:law|section|act|clause|case)",
        r"make\s+up\s+a\s+(?:legal\s+)?section",
        r"create\s+a\s+(?:fictional\s+|fake\s+)?(?:law|section)",
        r"fabricate\s+(?:a\s+)?(?:legal\s+)?section",
    ]

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Removes dangerous HTML tags and control characters."""
        if not text:
            return ""
        # Strip script and dangerous tags
        cleaned = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", text, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<\s*iframe[^>]*>.*?<\s*/\s*iframe\s*>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @classmethod
    def inspect_for_threats(cls, text: str) -> Tuple[bool, List[str]]:
        """
        Detects prompt injection or adversarial attacks.
        Returns (is_threat, list_of_threat_descriptions).
        """
        threats = []
        lower_text = text.lower()
        
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, lower_text):
                threats.append("Detected prompt injection or system override attempt.")
                break
                
        for pattern in cls.VICTORY_GUARANTEE_PATTERNS:
            if re.search(pattern, lower_text):
                threats.append("Detected request for guaranteed legal outcome.")
                break
                
        for pattern in cls.FABRICATION_REQUEST_PATTERNS:
            if re.search(pattern, lower_text):
                threats.append("Detected request to invent or fabricate legal sections.")
                break
                
        return (len(threats) > 0, threats)
