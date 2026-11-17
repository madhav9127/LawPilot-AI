import pytest
from app.core.escalation import EscalationDetector

def test_escalation_summons():
    text = "I received a court summons and notice to appear within 3 days."
    alert = EscalationDetector.analyze(text)
    assert alert.is_escalated is True
    assert alert.urgency_level == "critical"
    assert any("summons" in r.lower() for r in alert.reasons)
    assert any(h["number"] == "15100" for h in alert.helplines)

def test_escalation_violence():
    text = "The landlord brought bouncers and threatened violence if I don't leave."
    alert = EscalationDetector.analyze(text)
    assert alert.is_escalated is True
    assert alert.urgency_level == "critical"

def test_no_escalation_standard():
    text = "My landlord has not returned my security deposit of ₹20,000."
    alert = EscalationDetector.analyze(text)
    assert alert.is_escalated is False
    assert alert.urgency_level == "low"
