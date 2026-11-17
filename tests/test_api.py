import pytest
from app.main import (
    health_check, chat_endpoint, extract_case_endpoint,
    get_evidence_checklist, generate_document, download_pdf, download_docx,
    reset_session, serve_home
)
from app.models.schemas import ChatRequest, DocumentGenerationRequest, DocumentTypeEnum, CaseCategoryEnum

def test_health_endpoint():
    res = health_check()
    assert res["status"] == "online"
    assert "LawPilot" in res["app_name"]

def test_home_page():
    html = serve_home()
    assert "LawPilot AI" in html
    assert "Legal clarity starts with one conversation" in html

def test_chat_endpoint_tenant():
    req = ChatRequest(
        message="Tenant paid ₹25,000 as security deposit. Landlord refuses to return it after the tenant vacates."
    )
    res = chat_endpoint(req)
    assert res.role == "assistant"
    assert len(res.citations) > 0
    assert any("Transfer of Property" in c.act_name or "Tenancy" in c.act_name for c in res.citations)
    assert len(res.follow_up_questions) > 0

def test_chat_endpoint_consumer():
    req = ChatRequest(
        message="Customer purchased a ₹15,000 smartphone online. It arrived defective and the seller refuses a refund."
    )
    res = chat_endpoint(req)
    assert res.role == "assistant"
    assert any("Consumer Protection" in c.act_name for c in res.citations)

def test_chat_endpoint_employment():
    req = ChatRequest(
        message="Employee has not received two months of salary from employer."
    )
    res = chat_endpoint(req)
    assert res.role == "assistant"
    assert any("Payment of Wages" in c.act_name or "Contract" in c.act_name or "Shops" in c.act_name for c in res.citations)

def test_case_extraction_endpoint():
    req = ChatRequest(
        message="Paid ₹10,000 deposit for flat in Bengaluru. Landlord withholding it."
    )
    case = extract_case_endpoint(req)
    assert case.category == CaseCategoryEnum.TENANT
    assert case.financial_amounts.get("primary_amount") == 10000

def test_evidence_endpoint():
    items = get_evidence_checklist("tenant")
    assert len(items) > 0
    assert any("Agreement" in i.name for i in items)

def test_document_generate_and_pdf():
    doc_payload = DocumentGenerationRequest(
        doc_type=DocumentTypeEnum.SECURITY_DEPOSIT_DEMAND,
        user_name="Aman Sharma",
        counterparty_name="Ramesh Kumar",
        facts="Security deposit not returned.",
        disputed_amount="₹25,000",
        demands="Refund within 15 days"
    )
    # Text generation
    gen_resp = generate_document(doc_payload)
    assert "FORMAL WRITTEN DEMAND" in gen_resp.content_text

    # PDF download
    pdf_resp = download_pdf(doc_payload)
    assert pdf_resp.media_type == "application/pdf"
    assert len(pdf_resp.body) > 500

    # DOCX download
    docx_resp = download_docx(doc_payload)
    assert "wordprocessingml" in docx_resp.media_type
    assert len(docx_resp.body) > 500

def test_reset_session():
    res = reset_session("test_session")
    assert res["status"] == "success"
