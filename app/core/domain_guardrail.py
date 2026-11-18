"""
LawPilot AI — Legal Domain Specialisation & Scope Guardrail
Enforces comprehensive Indian legal scope covering all substantive and procedural
areas of Indian law (Constitutional, Criminal, Civil, Family, Property, Consumer,
Employment, Cyber, Banking, Tax, IPR, Motor Accident, Insurance, Environment, RTI, Immigration, ADR).
Delegates to IntentClassifier to:
- Politely redirect purely general-purpose non-legal inquiries (trivia, math, coding, jokes, sports)
- Provide targeted clarification questions for ambiguous messages
- Provide immediate emergency guidance for urgent safety situations
- Naturally handle greetings and conversational pleasantries
- Seamlessly process all genuine Indian legal queries across all domains
"""

from typing import Tuple, Optional, List, Dict
from app.core.intent_classifier import (
    IntentClassifier,
    UserIntentEnum,
    NON_LEGAL_SCOPE_RESPONSES,
    AMBIGUOUS_CLARIFYING_RESPONSES,
    URGENT_SAFETY_RESPONSES
)

OUT_OF_SCOPE_RESPONSES = NON_LEGAL_SCOPE_RESPONSES

class DomainGuardrail:
    """
    Evaluates whether user input falls within LawPilot AI's comprehensive Indian legal assistance scope.
    """

    @classmethod
    def inspect_query_scope(
        cls,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        lang_str: str = "en"
    ) -> Tuple[bool, Optional[str], bool]:
        """
        Inspects message scope using IntentClassifier.
        Returns:
            (is_diverted: bool, diversion_response: Optional[str], is_mixed: bool)
        """
        if not message or not message.strip():
            return False, None, False

        intent, resp_text, is_mixed, _ = IntentClassifier.classify_intent(
            message=message,
            conversation_history=conversation_history,
            language=lang_str
        )

        # 1. Non-legal, Ambiguous, or Urgent Safety: divert immediately with direct response
        if intent in [UserIntentEnum.NON_LEGAL_QUERY, UserIntentEnum.AMBIGUOUS_QUERY, UserIntentEnum.URGENT_SAFETY]:
            return True, resp_text, False

        # 2. Mixed Legal Query: proceed to legal response with mixed flag enabled
        if intent == UserIntentEnum.LEGAL_QUERY and is_mixed:
            return False, None, True

        # 3. Standard Legal Query or Greeting: proceed to normal pipeline
        return False, None, False
