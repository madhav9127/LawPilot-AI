import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import json
import io

from app.config import settings
from app.models.schemas import (
    ChatRequest, ChatMessage, CaseData, CaseCategoryEnum,
    DocumentGenerationRequest, DocumentResponse, DocumentTypeEnum,
    LanguageEnum, EvidenceItem
)
from app.core.llm_provider import LLMProviderFactory
from app.core.case_builder import CaseBuilder
from app.core.evidence_checklist import EvidenceChecklistManager
from app.core.document_generator import DocumentGenerator
from app.core.document_parser import DocumentParser
from app.core.knowledge_base import LegalKnowledgeBase
from app.core.escalation import EscalationDetector

app = FastAPI(
    title=settings.app_name,
    description="Intelligent, Multilingual Legal Assistant for Everyday Legal Rights in India",
    version=settings.app_version
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# In-memory session store (prototype scope)
SESSION_STORE = {}

@app.get("/", response_class=HTMLResponse)
def serve_home():
    """Serves the main application page."""
    index_path = os.path.join(templates_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>LawPilot AI is running. (templates/index.html not found)</h1>"

@app.get("/api/health")
def health_check():
    """Returns application status and LLM provider mode."""
    return {
        "status": "online",
        "app_name": settings.app_name,
        "active_provider": settings.active_provider,
        "is_demo_mode": settings.is_demo_mode,
        "version": settings.app_version
    }

@app.post("/api/chat", response_model=ChatMessage)
def chat_endpoint(request: ChatRequest):
    """Processes legal conversation message and returns grounded analysis."""
    provider = LLMProviderFactory.get_provider()
    response = provider.generate_response(
        message=request.message,
        conversation_history=request.conversation_history,
        language=request.language,
        state_jurisdiction=request.state_jurisdiction,
        session_id=request.session_id or "default_session"
    )
    return response

@app.post("/api/case/extract", response_model=CaseData)
def extract_case_endpoint(request: ChatRequest):
    """Extracts structured case facts from user text."""
    case = CaseBuilder.extract_case(
        text=request.message,
        state_jurisdiction=request.state_jurisdiction
    )
    SESSION_STORE[request.session_id] = case
    return case

@app.get("/api/evidence/{category}", response_model=List[EvidenceItem])
def get_evidence_checklist(category: str):
    """Retrieves dynamic evidence checklist for the given category."""
    try:
        cat_enum = CaseCategoryEnum(category.lower())
    except ValueError:
        cat_enum = CaseCategoryEnum.GENERAL
    return EvidenceChecklistManager.get_checklist_for_category(cat_enum)

@app.post("/api/document/generate", response_model=DocumentResponse)
def generate_document(req: DocumentGenerationRequest):
    """Generates draft legal notice or demand text."""
    content = DocumentGenerator.generate_document_text(req)
    titles = {
        DocumentTypeEnum.SECURITY_DEPOSIT_DEMAND: "Formal Demand for Security Deposit Refund",
        DocumentTypeEnum.CONSUMER_COMPLAINT: "Draft Consumer Complaint (District Commission)",
        DocumentTypeEnum.UNPAID_SALARY_DEMAND: "Formal Demand for Unpaid Wages and Dues",
        DocumentTypeEnum.LEGAL_NOTICE: "Draft Legal Notice Under Advocate Instructions",
        DocumentTypeEnum.REFUND_REQUEST_LETTER: "Refund Request Letter",
        DocumentTypeEnum.FINAL_SETTLEMENT_REQUEST: "Full & Final Settlement Clearance Notice",
        DocumentTypeEnum.NOTICE_REPLY: "Reply to Legal Notice",
        DocumentTypeEnum.ADVOCATE_BRIEF: "Advocate Briefing Summary"
    }
    title = titles.get(req.doc_type, "Legal Notice Draft")
    return DocumentResponse(
        title=title,
        doc_type=req.doc_type,
        content_text=content,
        disclaimer=DocumentGenerator.MANDATORY_DISCLAIMER
    )

@app.post("/api/document/download/pdf")
def download_pdf(req: DocumentGenerationRequest):
    """Generates and downloads PDF file."""
    content = DocumentGenerator.generate_document_text(req)
    title = f"LawPilot AI - {req.doc_type.value.replace('_', ' ').title()}"
    pdf_bytes = DocumentGenerator.generate_pdf(content, title=title)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=LawPilot_{req.doc_type.value}.pdf"
        }
    )

@app.post("/api/document/download/docx")
def download_docx(req: DocumentGenerationRequest):
    """Generates and downloads DOCX Word file."""
    content = DocumentGenerator.generate_document_text(req)
    title = f"LawPilot AI - {req.doc_type.value.replace('_', ' ').title()}"
    docx_bytes = DocumentGenerator.generate_docx(content, title=title)
    
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename=LawPilot_{req.doc_type.value}.docx"
        }
    )

@app.post("/api/upload")
def upload_document(file: UploadFile = File(...)):
    """Parses and sanitizes user-uploaded documents (Rental agreement, invoice, pay slip)."""
    # Size and extension verification
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed: {settings.allowed_extensions}")
    
    content = file.file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size of {settings.max_upload_size_mb} MB.")
    
    result = DocumentParser.analyze_uploaded_document(file.filename, content)
    return result

@app.post("/api/session/reset")
def reset_session(session_id: Optional[str] = "default_session"):
    """Resets conversation state for privacy protection."""
    from app.core.llm_provider import reset_memory
    if session_id in SESSION_STORE:
        del SESSION_STORE[session_id]
    reset_memory(session_id)
    return {"status": "success", "message": f"Session context cleared securely for {session_id}."}
