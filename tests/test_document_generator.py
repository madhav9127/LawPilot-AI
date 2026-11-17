import pytest
from app.core.document_generator import DocumentGenerator
from app.models.schemas import DocumentGenerationRequest, DocumentTypeEnum

def test_generate_security_deposit_demand():
    req = DocumentGenerationRequest(
        doc_type=DocumentTypeEnum.SECURITY_DEPOSIT_DEMAND,
        user_name="Aman Sharma",
        user_address="Bengaluru",
        counterparty_name="Ramesh Kumar",
        counterparty_address="Bengaluru",
        facts="Vacated on 1st March. Deposit ₹25,000 not refunded.",
        disputed_amount="₹25,000",
        incident_date="1st March",
        demands="Refund ₹25,000 within 15 days"
    )
    doc_text = DocumentGenerator.generate_document_text(req)
    assert "FORMAL WRITTEN DEMAND" in doc_text
    assert "₹25,000" in doc_text
    assert "Ramesh Kumar" in doc_text
    assert DocumentGenerator.MANDATORY_DISCLAIMER in doc_text

def test_generate_pdf():
    req = DocumentGenerationRequest(
        doc_type=DocumentTypeEnum.CONSUMER_COMPLAINT,
        user_name="Priya Patel",
        counterparty_name="XYZ E-Commerce",
        facts="Received broken smartphone.",
        disputed_amount="₹15,000",
        demands="Full refund of ₹15,000"
    )
    doc_text = DocumentGenerator.generate_document_text(req)
    pdf_bytes = DocumentGenerator.generate_pdf(doc_text, "Test Consumer Complaint")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500  # Valid PDF binary
    assert pdf_bytes.startswith(b"%PDF")

def test_generate_docx():
    req = DocumentGenerationRequest(
        doc_type=DocumentTypeEnum.UNPAID_SALARY_DEMAND,
        user_name="Rohit Verma",
        counterparty_name="Tech Services Pvt Ltd",
        facts="Two months salary unpaid.",
        disputed_amount="₹80,000",
        demands="Clear outstanding salary"
    )
    doc_text = DocumentGenerator.generate_document_text(req)
    docx_bytes = DocumentGenerator.generate_docx(doc_text, "Test Salary Demand")
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 500  # Valid DOCX zip binary
    assert docx_bytes.startswith(b"PK")
