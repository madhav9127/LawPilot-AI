"""
LawPilot AI — Legal Domain Specialisation & Scope Guardrail
Delegates to the dedicated IntentGate to enforce:
- Comprehensive Indian legal scope across all domains
- Exclusion of general-purpose topics (programming, trivia, science, entertainment, etc.)
- Emergency guidance for urgent safety crises
- Clarifications for ambiguous inputs
"""

from typing import Tuple, Optional, List, Dict
from app.core.intent_gate import (
    IntentGate,
    UserIntentEnum,
    STANDARD_NON_LEGAL_RESPONSES,
    AMBIGUOUS_CLARIFICATION_RESPONSES,
    URGENT_SAFETY_RESPONSES
)

OUT_OF_SCOPE_RESPONSES = STANDARD_NON_LEGAL_RESPONSES

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
        Inspects message scope using IntentGate.
        Returns:
            (is_diverted: bool, diversion_response: Optional[str], is_mixed: bool)
        """
        if not message or not message.strip():
            return False, None, False

        decision = IntentGate.evaluate(
            message=message,
            conversation_history=conversation_history,
            language=lang_str
        )

        # Non-Legal, Ambiguous, or Urgent Safety: divert immediately with direct response
        if decision.intent in [UserIntentEnum.NON_LEGAL_QUERY, UserIntentEnum.AMBIGUOUS, UserIntentEnum.URGENT_SAFETY]:
            return True, decision.direct_response, False

        # Mixed Legal Query: proceed to legal response with mixed flag enabled
        if decision.intent == UserIntentEnum.LEGAL_QUERY and decision.is_mixed:
            return False, None, True

        # Standard Legal Query or Greeting: proceed to normal pipeline
        return False, None, False
