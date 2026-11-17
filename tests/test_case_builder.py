import pytest
from app.core.case_builder import CaseBuilder
from app.models.schemas import CaseCategoryEnum, LanguageEnum

def test_tenant_extraction_t1():
    text = "Tenant paid ₹25,000 as security deposit. Landlord refuses to return it after the tenant vacates."
    case = CaseBuilder.extract_case(text)
    assert case.category == CaseCategoryEnum.TENANT
    assert case.financial_amounts.get("primary_amount") == 25000
    assert case.user_role == "Tenant"
    assert "Landlord" in case.counterparty_role

def test_consumer_extraction_c1():
    text = "Customer purchased a ₹15,000 smartphone online. It arrived defective and the seller refuses a refund."
    case = CaseBuilder.extract_case(text)
    assert case.category == CaseCategoryEnum.CONSUMER
    assert case.financial_amounts.get("primary_amount") == 15000
    assert case.user_role == "Consumer / Purchaser"

def test_employment_extraction_e1():
    text = "Employee has not received two months of salary from employer."
    case = CaseBuilder.extract_case(text)
    assert case.category == CaseCategoryEnum.EMPLOYMENT
    assert case.user_role == "Employee"

def test_missing_info_detection():
    # Text with no amount and no state
    text = "Landlord is not returning my deposit."
    case = CaseBuilder.extract_case(text)
    assert any("financial amount" in m.lower() for m in case.missing_information)
    assert any("state" in m.lower() for m in case.missing_information)

def test_follow_up_questions_multilingual():
    text = "Landlord deposit nahi de raha"
    case = CaseBuilder.extract_case(text)
    q_hi = CaseBuilder.generate_follow_up_questions(case, language=LanguageEnum.HINDI)
    q_hinglish = CaseBuilder.generate_follow_up_questions(case, language=LanguageEnum.HINGLISH)
    q_en = CaseBuilder.generate_follow_up_questions(case, language=LanguageEnum.ENGLISH)
    
    assert len(q_hi) > 0
    assert len(q_hinglish) > 0
    assert len(q_en) > 0
