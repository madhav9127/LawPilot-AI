import pytest
from app.core.knowledge_base import LegalKnowledgeBase
from app.models.schemas import CaseCategoryEnum, VerificationStatusEnum

def test_grounded_retrieval_tenant():
    citations = LegalKnowledgeBase.retrieve_grounded_laws("security deposit refund wear and tear painting", CaseCategoryEnum.TENANT)
    assert len(citations) > 0
    # Should contain Transfer of Property Act
    act_names = [c.act_name for c in citations]
    assert any("Transfer of Property" in a or "Model Tenancy" in a for a in act_names)
    for c in citations:
        assert c.official_url.startswith("http")
        assert c.verification_status == VerificationStatusEnum.VERIFIED

def test_grounded_retrieval_consumer():
    citations = LegalKnowledgeBase.retrieve_grounded_laws("defective smartphone online refund", CaseCategoryEnum.CONSUMER)
    assert len(citations) > 0
    act_names = [c.act_name for c in citations]
    assert any("Consumer Protection" in a for a in act_names)

def test_grounded_retrieval_employment():
    citations = LegalKnowledgeBase.retrieve_grounded_laws("unpaid salary delayed wages deduction", CaseCategoryEnum.EMPLOYMENT)
    assert len(citations) > 0
    act_names = [c.act_name for c in citations]
    assert any("Payment of Wages" in a or "Contract Act" in a or "Shops" in a for a in act_names)

def test_citation_verification_real():
    is_valid, citation, msg = LegalKnowledgeBase.verify_citation_claim("Transfer of Property Act", "Section 108")
    assert is_valid is True
    assert citation is not None

def test_citation_verification_fake():
    is_valid, citation, msg = LegalKnowledgeBase.verify_citation_claim("Rent Control Act", "Section 999")
    assert is_valid is False
    assert citation is None
    assert "Unverified" in msg
