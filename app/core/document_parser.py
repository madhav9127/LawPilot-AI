import io
import re
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
import docx
from app.core.sanitizer import Sanitizer
from app.core.case_builder import CaseBuilder

class DocumentParser:
    """
    Parses user-uploaded documents (Rental agreements, Invoices, Salary Slips, Notices).
    Extracts dates, financial figures, parties, clauses, and sanitizes against prompt injection.
    """

    @classmethod
    def extract_text_from_file(cls, filename: str, content_bytes: bytes) -> str:
        """Extracts plain text from PDF, DOCX, or text file."""
        lower_name = filename.lower()
        extracted = ""

        try:
            if lower_name.endswith(".pdf"):
                reader = PdfReader(io.BytesIO(content_bytes))
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted += text + "\n"
            elif lower_name.endswith(".docx"):
                doc = docx.Document(io.BytesIO(content_bytes))
                for p in doc.paragraphs:
                    extracted += p.text + "\n"
            else:
                # Fallback text/markdown decode
                extracted = content_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            extracted = f"Error reading document contents: {str(e)}"

        return extracted.strip()

    @classmethod
    def analyze_uploaded_document(cls, filename: str, content_bytes: bytes) -> Dict[str, Any]:
        """
        Extracts legal facts and protects against prompt injection from untrusted files.
        """
        raw_text = cls.extract_text_from_file(filename, content_bytes)
        
        # 1. Inspect for prompt injection threats
        is_threat, threat_details = Sanitizer.inspect_for_threats(raw_text)
        if is_threat:
            return {
                "success": False,
                "error": "Security Warning: Document contains potential prompt injection or unauthorized system override instructions.",
                "threat_details": threat_details,
                "sanitized_preview": Sanitizer.sanitize_text(raw_text[:300])
            }

        sanitized_text = Sanitizer.sanitize_text(raw_text)
        
        # 2. Extract financial figures
        amounts_info = CaseBuilder.extract_amounts(sanitized_text)

        # 3. Extract dates & check conflicts
        dates, conflict = CaseBuilder.extract_dates_and_check_conflicts(sanitized_text)

        # 4. Extract key clauses / summaries
        clauses = []
        lower = sanitized_text.lower()
        if "lock-in" in lower or "lock in" in lower:
            clauses.append("Lock-in period clause identified.")
        if "notice period" in lower:
            clauses.append("Notice period clause identified.")
        if "wear and tear" in lower:
            clauses.append("Reasonable wear and tear exception identified.")
        if "probation" in lower:
            clauses.append("Probation or employment tenure terms identified.")
        if "warranty" in lower or "guarantee" in lower:
            clauses.append("Warranty / guarantee clause identified.")

        # 5. Extract category
        category, sub_category = CaseBuilder.classify_category(sanitized_text)

        return {
            "success": True,
            "filename": filename,
            "category": category.value,
            "sub_category": sub_category,
            "extracted_amounts": amounts_info,
            "detected_dates": dates,
            "detected_clauses": clauses,
            "summary_snippet": sanitized_text[:400] + ("..." if len(sanitized_text) > 400 else ""),
            "confirmation_prompt": (
                "Please verify the extracted details above. LawPilot AI does not automatically assume "
                "uploaded documents are legally valid or binding under Indian law until verified."
            )
        }
