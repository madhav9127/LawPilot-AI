from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class LanguageEnum(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    HINGLISH = "hinglish"

class CaseCategoryEnum(str, Enum):
    TENANT = "tenant"
    CONSUMER = "consumer"
    EMPLOYMENT = "employment"
    GENERAL = "general"

class EvidenceStatusEnum(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PENDING = "pending"

class VerificationStatusEnum(str, Enum):
    VERIFIED = "Verified source available"
    RECOMMENDED = "Additional verification recommended"
    INSUFFICIENT = "Insufficient information"

class LegalCitation(BaseModel):
    act_name: str
    section: str
    title: str
    description: str
    official_url: str
    commencement_date: Optional[str] = None
    jurisdiction: str = "Central"  # Central or specific State (e.g., Delhi, Maharashtra)
    verification_status: VerificationStatusEnum = VerificationStatusEnum.VERIFIED

class ChatMessage(BaseModel):
    role: str # "user", "assistant", "system"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    citations: List[LegalCitation] = []
    verification_status: Optional[VerificationStatusEnum] = None
    missing_info: List[str] = []
    follow_up_questions: List[str] = []
    escalation_detected: bool = False
    escalation_details: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []
    language: LanguageEnum = LanguageEnum.ENGLISH
    session_id: Optional[str] = "default_session"
    state_jurisdiction: Optional[str] = None

class EvidenceItem(BaseModel):
    id: str
    name: str
    category: str
    status: EvidenceStatusEnum = EvidenceStatusEnum.PENDING
    legal_importance: str
    description: str

class CaseData(BaseModel):
    case_id: str = "CASE-" + datetime.now().strftime("%Y%m%d%H%M%S")
    category: CaseCategoryEnum = CaseCategoryEnum.GENERAL
    sub_category: Optional[str] = None
    user_role: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_role: Optional[str] = None
    incident_description: Optional[str] = None
    timeline: List[Dict[str, str]] = []
    financial_amounts: Dict[str, Any] = {}
    agreements: Optional[str] = None
    communication_history: Optional[str] = None
    available_evidence: List[str] = []
    actions_already_taken: List[str] = []
    desired_resolution: Optional[str] = None
    missing_information: List[str] = []
    state_jurisdiction: Optional[str] = None
    confidence_score: float = 0.85
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

class DocumentTypeEnum(str, Enum):
    SECURITY_DEPOSIT_DEMAND = "security_deposit_demand"
    LEGAL_NOTICE = "formal_legal_notice"
    CONSUMER_COMPLAINT = "consumer_complaint_draft"
    REFUND_REQUEST_LETTER = "refund_request_letter"
    UNPAID_SALARY_DEMAND = "unpaid_salary_demand"
    FINAL_SETTLEMENT_REQUEST = "final_settlement_request"
    NOTICE_REPLY = "notice_reply"
    ADVOCATE_BRIEF = "advocate_brief_summary"

class DocumentGenerationRequest(BaseModel):
    doc_type: DocumentTypeEnum
    case_id: Optional[str] = None
    user_name: str
    user_address: Optional[str] = "Address not provided (Draft template)"
    counterparty_name: str
    counterparty_address: Optional[str] = "Address not provided (Draft template)"
    facts: str
    disputed_amount: Optional[str] = "Unspecified"
    incident_date: Optional[str] = "As specified in communication"
    demands: str
    deadline_days: int = 15
    state: Optional[str] = "India"
    language: LanguageEnum = LanguageEnum.ENGLISH

class DocumentResponse(BaseModel):
    title: str
    doc_type: DocumentTypeEnum
    content_text: str
    disclaimer: str
    pdf_available: bool = True
    docx_available: bool = True

class EscalationAlert(BaseModel):
    is_escalated: bool = False
    urgency_level: str = "low" # "low", "medium", "high", "critical"
    reasons: List[str] = []
    recommended_action: str = ""
    helplines: List[Dict[str, str]] = []

class EvaluationMetric(BaseModel):
    test_id: str
    scenario_name: str
    category: str
    legal_accuracy_score: float
    relevance_score: float
    extraction_score: float
    safety_score: float
    document_score: float
    multilingual_score: float
    ux_score: float
    weighted_total: float
    pass_status: bool
    notes: str
