import os
import io
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.models.schemas import DocumentTypeEnum, DocumentGenerationRequest, DocumentResponse

class DocumentGenerator:
    """
    Dedicated Legal Document Generator for Indian Legal-Tech workflows.
    Generates professional legal demand letters, formal legal notices,
    consumer complaint drafts, and advocate summaries.
    Exports to plain text, PDF, and DOCX formats with mandatory draft disclaimers.
    """

    MANDATORY_DISCLAIMER = (
        "CONFIDENTIAL DRAFT — PREPARED BY LAWPILOT AI FOR INFORMATIONAL & PRE-LITIGATION GUIDANCE ONLY. "
        "THIS DRAFT MUST BE CAREFULLY REVIEWED, VERIFIED, AND APPROVED BY A QUALIFIED ADVOCATE BEFORE FORMAL SERVICE, "
        "EXECUTION, OR FILING IN ANY COURT OR TRIBUNAL IN INDIA."
    )

    @classmethod
    def generate_document_text(cls, req: DocumentGenerationRequest) -> str:
        """Generates structured legal document text based on document type and case facts."""
        date_str = datetime.now().strftime("%d %B %Y")
        
        # 1. SECURITY DEPOSIT DEMAND
        if req.doc_type == DocumentTypeEnum.SECURITY_DEPOSIT_DEMAND:
            return (
                f"FORMAL WRITTEN DEMAND FOR REFUND OF SECURITY DEPOSIT\n"
                f"(Sent via Registered Post A.D. / Speed Post / Email)\n\n"
                f"Date: {date_str}\n\n"
                f"FROM:\n{req.user_name}\n{req.user_address}\n\n"
                f"TO:\n{req.counterparty_name}\n{req.counterparty_address}\n\n"
                f"SUBJECT: Formal Demand for immediate refund of Security Deposit amount of {req.disputed_amount} "
                f"in respect of tenancy at the subject premises.\n\n"
                f"Sir / Madam,\n\n"
                f"1. That I was inducted as a lawful tenant into the residential premises under your ownership/management, "
                f"having paid an upfront refundable security deposit amounting to {req.disputed_amount}.\n\n"
                f"2. That during the entire subsistence of the tenancy, I regularly cleared monthly rent and utility charges "
                f"without default, fulfilling all reciprocal obligations under law.\n\n"
                f"3. That peaceful and vacant possession of the premises was formally handed over on or about {req.incident_date}. "
                f"The premises was delivered in clean, habitable condition, subject only to normal wear and tear recognized under "
                f"Section 108(m) of the Transfer of Property Act, 1882.\n\n"
                f"4. That despite repeated amicable requests and follow-ups, you have wrongfully withheld/delayed refunding "
                f"the said security deposit of {req.disputed_amount}, without any legitimate justification or itemized damage proofs.\n\n"
                f"5. DEMAND: You are hereby called upon to refund the entire sum of {req.disputed_amount} to my bank account "
                f"within {req.deadline_days} days of receipt of this notice, failing which I shall be constrained to initiate appropriate "
                f"legal remedies before the competent Rent Authority / Civil Court under applicable laws, including claiming statutory "
                f"interest @ 18% p.a. and litigation costs entirely at your risk.\n\n"
                f"Yours sincerely,\n\n"
                f"{req.user_name}\n"
                f"(Tenant / Aggrieved Party)\n\n"
                f"--------------------------------------------------\n"
                f"LEGAL NOTICE DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 2. CONSUMER COMPLAINT DRAFT (DISTRICT COMMISSION)
        elif req.doc_type == DocumentTypeEnum.CONSUMER_COMPLAINT:
            return (
                f"BEFORE THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION\n"
                f"AT: {req.state.upper() if req.state else 'DISTRICT HEADQUARTERS'}\n\n"
                f"CONSUMER COMPLAINT NO. _______ / {datetime.now().year}\n"
                f"(Under Section 35 of the Consumer Protection Act, 2019)\n\n"
                f"IN THE MATTER OF:\n\n"
                f"{req.user_name}\n{req.user_address}\n... COMPLAINANT\n\n"
                f"VERSUS\n\n"
                f"{req.counterparty_name}\n{req.counterparty_address}\n... OPPOSITE PARTY\n\n"
                f"COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019 FOR DEFICIENCY IN SERVICE "
                f"AND UNFAIR TRADE PRACTICE RESULTING IN PECUNIARY LOSS.\n\n"
                f"MOST RESPECTFULLY SHOWETH:\n\n"
                f"1. That the Complainant is a consumer within the meaning of Section 2(7) of the Consumer Protection Act, 2019, "
                f"having purchased/availed goods/services from the Opposite Party against full valuable consideration of {req.disputed_amount}.\n\n"
                f"2. That the Opposite Party is a registered merchant/e-commerce platform engaging in commercial sales to the general public.\n\n"
                f"3. BRIEF FACTS:\n{req.facts}\n\n"
                f"4. That the goods supplied were inherently defective / delivery was deficient / promised refund of {req.disputed_amount} "
                f"was unlawfully denied, constituting gross deficiency in service and unfair trade practice under Section 2(47) of the Act.\n\n"
                f"5. PRAYER:\n"
                f"It is therefore most respectfully prayed that this Hon'ble Commission may graciously be pleased to:\n"
                f"  a) Direct the Opposite Party to refund the full consideration of {req.disputed_amount} along with interest @ 12% p.a.;\n"
                f"  b) Award compensation of ₹25,000/- towards mental agony, harassment, and severe inconvenience;\n"
                f"  c) Award litigation expenses to the Complainant;\n"
                f"  d) Pass any other order deemed just and equitable in the interest of justice.\n\n"
                f"DATED: {date_str}\nPLACE: {req.state}\n\n"
                f"{req.user_name}\n(Complainant in Person)\n\n"
                f"--------------------------------------------------\n"
                f"DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 3. UNPAID SALARY / EMPLOYMENT DEMAND
        elif req.doc_type == DocumentTypeEnum.UNPAID_SALARY_DEMAND:
            return (
                f"FORMAL NOTICE AND DEMAND FOR DISBURSEMENT OF OUTSTANDING WAGES & STATUTORY DUES\n\n"
                f"Date: {date_str}\n\n"
                f"TO:\n"
                f"The Management / Human Resources,\n"
                f"{req.counterparty_name}\n{req.counterparty_address}\n\n"
                f"FROM:\n"
                f"{req.user_name}\n{req.user_address}\n\n"
                f"SUBJECT: Formal demand for clearance of earned salary and full and final settlement amounting to {req.disputed_amount}.\n\n"
                f"Sir / Madam,\n\n"
                f"1. That I was employed with {req.counterparty_name} and diligently performed my official duties in accordance with "
                f"company policy and terms of employment.\n\n"
                f"2. STATEMENT OF FACTS:\n{req.facts}\n\n"
                f"3. That despite having rendered bona fide service, my earned remuneration / settlement dues totaling {req.disputed_amount} "
                f"have remained unpaid beyond the mandatory statutory timelines provided under the Payment of Wages Act, 1936 and applicable "
                f"Shops and Commercial Establishments legislation.\n\n"
                f"4. That withholding an employee's legitimately earned remuneration is unlawful and constitutes a direct breach of contract "
                f"under Section 73 of the Indian Contract Act, 1872.\n\n"
                f"5. DEMAND: You are hereby called upon to remit the entire outstanding sum of {req.disputed_amount} to my bank account "
                f"and issue my Experience and Relieving Letter within {req.deadline_days} days of receipt of this notice. "
                f"In the event of failure, I shall lodge a formal complaint before the Labour Commissioner / Authority under Section 15 "
                f"of the Payment of Wages Act and pursue appropriate civil proceedings at your sole cost and consequence.\n\n"
                f"Yours faithfully,\n\n"
                f"{req.user_name}\n"
                f"(Employee)\n\n"
                f"--------------------------------------------------\n"
                f"DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 4. FORMAL LEGAL NOTICE DRAFT (GENERAL)
        elif req.doc_type == DocumentTypeEnum.LEGAL_NOTICE:
            return (
                f"LEGAL NOTICE (DRAFT FOR ADVOCATE REVIEW)\n"
                f"(SENT THROUGH REGISTERED POST WITH ACKNOWLEDGEMENT DUE / SPEED POST)\n\n"
                f"Date: {date_str}\n\n"
                f"TO:\n{req.counterparty_name}\n{req.counterparty_address}\n\n"
                f"UNDER INSTRUCTIONS FROM AND ON BEHALF OF MY CLIENT:\n"
                f"{req.user_name}, residing at {req.user_address} (hereinafter referred to as 'My Client').\n\n"
                f"Sir / Madam,\n\n"
                f"Under instructions from my Client aforesaid, I hereby serve upon you this Legal Notice:\n\n"
                f"1. That My Client had lawful dealings with you in respect of the following matter:\n{req.facts}\n\n"
                f"2. That by your acts, omissions, and unilateral non-compliance, you have caused wrongful financial injury "
                f"amounting to {req.disputed_amount} to My Client.\n\n"
                f"3. That your conduct is arbitrary, unlawful, and actionable under applicable civil and statutory laws of India.\n\n"
                f"4. I therefore call upon you, through this notice, to unconditionally fulfill the demands of My Client:\n"
                f"   - {req.demands}\n"
                f"   - Remit the sum of {req.disputed_amount} along with interest @ 18% p.a.\n\n"
                f"within a period of {req.deadline_days} days from the date of receipt hereof, failing which My Client has given "
                f"clear instructions to institute appropriate legal proceedings against you in a court of competent jurisdiction "
                f"holding you liable for all consequential losses, costs, and expenses.\n\n"
                f"Copy retained in my office for future legal action.\n\n"
                f"Advocate for the Client\n"
                f"(DRAFT — TO BE SIGNED & DISPATCHED BY ADVOCATE ON RECORD)\n\n"
                f"--------------------------------------------------\n"
                f"DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # Default fallback: General Demand / Advocate Summary
        else:
            return (
                f"LEGAL DISPUTE SUMMARY & DEMAND NOTICE DRAFT\n\n"
                f"Date: {date_str}\n\n"
                f"PARTIES:\n"
                f"Complainant / Claimant: {req.user_name} ({req.user_address})\n"
                f"Respondent / Counterparty: {req.counterparty_name} ({req.counterparty_address})\n\n"
                f"DISPUTED AMOUNT: {req.disputed_amount}\n"
                f"KEY INCIDENT DATE: {req.incident_date}\n\n"
                f"SUMMARY OF FACTS:\n{req.facts}\n\n"
                f"RELIEF SOUGHT:\n{req.demands}\n\n"
                f"STATUTORY BASIS:\n"
                f"- Relevant provisions of Indian law governing breach, deficiency, or tenancy as applicable.\n"
                f"- Time given for voluntary compliance: {req.deadline_days} days.\n\n"
                f"Signature: _______________________\n"
                f"{req.user_name}\n\n"
                f"--------------------------------------------------\n"
                f"DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

    @classmethod
    def generate_pdf(cls, text_content: str, title: str = "LawPilot AI - Legal Document Draft") -> bytes:
        """Generates a professionally styled PDF document using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        
        # Custom palette: Navy #0F172A, Teal #0D9488
        navy = colors.HexColor("#0F172A")
        teal = colors.HexColor("#0D9488")
        gray = colors.HexColor("#475569")
        red_alert = colors.HexColor("#991B1B")

        title_style = ParagraphStyle(
            'LegalTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=navy,
            alignment=1, # Center
            spaceAfter=12
        )

        disclaimer_style = ParagraphStyle(
            'DisclaimerStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=11,
            textColor=red_alert,
            alignment=0, # Left
            spaceAfter=14
        )

        body_style = ParagraphStyle(
            'LegalBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.black,
            spaceAfter=8
        )

        elements = []
        elements.append(Paragraph(title.upper(), title_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=teal, spaceBefore=4, spaceAfter=12))
        
        # Stamp top disclaimer
        elements.append(Paragraph(f"<b>LEGAL DRAFT NOTICE:</b> {cls.MANDATORY_DISCLAIMER}", disclaimer_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceBefore=2, spaceAfter=12))

        # Split paragraphs
        paragraphs = text_content.split("\n\n")
        for p in paragraphs:
            clean_p = p.strip().replace("\n", "<br/>")
            if clean_p:
                if clean_p.startswith("SUBJECT:") or clean_p.startswith("BEFORE THE") or clean_p.startswith("IN THE MATTER OF"):
                    elements.append(Paragraph(f"<b>{clean_p}</b>", body_style))
                elif "DISCLAIMER" in clean_p:
                    elements.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceBefore=8, spaceAfter=8))
                    elements.append(Paragraph(f"<font size=8 color='#991B1B'>{clean_p}</font>", body_style))
                else:
                    elements.append(Paragraph(clean_p, body_style))
                elements.append(Spacer(1, 4))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    @classmethod
    def generate_docx(cls, text_content: str, title: str = "LawPilot AI - Legal Document Draft") -> bytes:
        """Generates a structured Word DOCX file using python-docx."""
        doc = docx.Document()

        # Set standard margins
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        # Header Title
        title_p = doc.add_paragraph()
        title_run = title_p.add_run(title.upper())
        title_run.bold = True
        title_run.font.size = Pt(13)
        title_run.font.color.rgb = RGBColor(15, 23, 42) # Navy
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Disclaimer Box
        disc_p = doc.add_paragraph()
        disc_run = disc_p.add_run(f"LEGAL NOTICE: {cls.MANDATORY_DISCLAIMER}")
        disc_run.bold = True
        disc_run.font.size = Pt(8.5)
        disc_run.font.color.rgb = RGBColor(153, 27, 27) # Dark red

        doc.add_paragraph("-" * 75)

        # Body text
        paragraphs = text_content.split("\n\n")
        for p in paragraphs:
            clean_p = p.strip()
            if clean_p:
                para = doc.add_paragraph()
                para.paragraph_format.space_after = Pt(6)
                para.paragraph_format.line_spacing = 1.15
                run = para.add_run(clean_p)
                run.font.name = "Arial"
                run.font.size = Pt(10)
                if clean_p.startswith("SUBJECT:") or clean_p.startswith("BEFORE THE"):
                    run.bold = True

        buffer = io.BytesIO()
        doc.save(buffer)
        docx_bytes = buffer.getvalue()
        buffer.close()
        return docx_bytes
