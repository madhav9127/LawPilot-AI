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
    Dedicated Legal Document Generator for Indian Legal-Tech workflows across all legal domains.
    Generates professional legal demand letters, formal legal notices, police complaints (BNSS Sec 173),
    cyber fraud reports, cheque bounce statutory notices (Sec 138 NI Act), RTI applications,
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
        amt_str = req.disputed_amount or "[Amount in ₹]"
        user_nm = req.user_name or "[Your Full Name]"
        user_addr = req.user_address or "[Your Complete Address]"
        c_nm = req.counterparty_name or "[Opposing Party / Company Name]"
        c_addr = req.counterparty_address or "[Opposing Party Address]"
        inc_date = req.incident_date or "[Date of Incident / Handover / Notice]"
        deadline = req.deadline_days or 15
        facts_text = req.facts or "[Detailed chronological facts of the matter]"
        demands_text = req.demands or f"Immediate payment of {amt_str} with statutory interest"
        state_str = req.state or "[State / District]"
        lang_str = req.language.value if hasattr(req.language, "value") else str(req.language).lower()

        # 1. SECURITY DEPOSIT DEMAND
        if req.doc_type == DocumentTypeEnum.SECURITY_DEPOSIT_DEMAND:
            if lang_str in ["gu", "gujarati"]:
                return (
                    f"સિક્યોરિટી ડિપોઝિટ પરત મેળવવા માટેનું ઔપચારિક લેખિત માંગ પત્ર (Formal Demand Notice)\n"
                    f"(રજિસ્ટર્ડ પોસ્ટ / સ્પીડ પોસ્ટ / ઈમેઈલ દ્વારા મોકલવા માટે)\n\n"
                    f"તારીખ: {date_str}\n\n"
                    f"પ્રેષક (ભાડૂઆત):\n{user_nm}\n{user_addr}\n\n"
                    f"પ્રતિ (મકાનમાલિક):\n{c_nm}\n{c_addr}\n\n"
                    f"વિષય: ભાડાના મકાનની {amt_str} ની સિક્યોરિટી ડિપોઝિટ તાત્કાલિક પરત કરવા બાબત.\n\n"
                    f"મહોદય / મહોદયા,\n\n"
                    f"૧. હું આપના રહેણાંક મકાનમાં કાયદેસરના ભાડૂઆત તરીકે રહેતો હતો, અને મેં શરૂઆતમાં આપને {amt_str} ની રિફંડેબલ સિક્યોરિટી ડિપોઝિટ ચૂકવી હતી.\n\n"
                    f"૨. ભાડૂઆત તરીકેના સમગ્ર સમયગાળા દરમિયાન મેં તમામ માસિક ભાડું અને બિલ નિયમિતપણે ચૂકવ્યા છે અને તમામ કાનૂની શરતોનું પાલન કર્યું છે.\n\n"
                    f"૩. મેં મકાન ખાલી કરીને તેનો શાંતિપૂર્ણ કબજો {inc_date} ના રોજ સુપરત કરી દીધો છે. મિલકત સામાન્ય ઘસારા (reasonable wear and tear) સિવાય યોગ્ય સ્થિતિમાં પરત સોંપવામાં આવી છે (ટ્રાન્સફર ઓફ પ્રોપર્ટી એક્ટ, ૧૮૮૨ ની કલમ ૧૦૮).\n\n"
                    f"૪. વારંવારની વિનંતી છતાં આપે કોઈપણ કાયદેસર કારણ કે હિસાબ વગર મારી {amt_str} ની ડિપોઝિટ પરત કરવામાં અયોગ્ય વિલંબ કર્યો છે.\n\n"
                    f"૫. માંગણી: આ નોટિસ મળ્યાના {deadline} દિવસની અંદર {amt_str} ની સંપૂર્ણ રકમ મારા બેંક ખાતામાં જમા કરવા વિનંતી છે. જો નિર્ધારિત સમયમાં રકમ નહીં મળે તો સક્ષમ રેન્ટ ઓથોરિટી / અદાલતમાં કાનૂની કાર્યવાહી શરૂ કરવામાં આવશે.\n\n"
                    f"આપનો વિશ્વાસુ,\n\n"
                    f"{user_nm}\n(ભાડૂઆત / અરજદાર)\n\n"
                    f"--------------------------------------------------\n"
                    f"કાનૂની સૂચના (DISCLAIMER):\n{cls.MANDATORY_DISCLAIMER}"
                )
            elif lang_str in ["hi", "hindi"]:
                return (
                    f"सुरक्षा जमा (Security Deposit) वापसी हेतु औपचारिक मांग पत्र (Demand Notice)\n"
                    f"(रजिस्टर्ड डाक / स्पीड पोस्ट / ईमेल द्वारा प्रेषित)\n\n"
                    f"दिनांक: {date_str}\n\n"
                    f"प्रेषक (किरायेदार):\n{user_nm}\n{user_addr}\n\n"
                    f"प्रति (मकान मालिक):\n{c_nm}\n{c_addr}\n\n"
                    f"विषय: किराये के परिसर की {amt_str} की सुरक्षा जमा राशि तुरंत वापस करने बाबत।\n\n"
                    f"महोदय / महोदया,\n\n"
                    f"1. मैं आपके स्वामित्व वाले आवासीय परिसर में वैध किरायेदार के रूप में निवासरत था और मैंने अग्रिम रूप से {amt_str} की प्रतिदेय सुरक्षा जमा राशि का भुगतान किया था।\n\n"
                    f"2. किरायेदारी की पूरी अवधि के दौरान मैंने बिना किसी चूक के नियमित रूप से मासिक किराया चुकाया है।\n\n"
                    f"3. परिसर का शांतिपूर्ण और रिक्त कब्जा {inc_date} को औपचारिक रूप से सौंप दिया गया था (संपत्ति अंतरण अधिनियम, 1882 की धारा 108(m))।\n\n"
                    f"4. बार-बार अनुरोध के बावजूद आपने {amt_str} की जमा राशि अवैध रूप से रोक रखी है।\n\n"
                    f"5. मांग: यह नोटिस प्राप्त होने के {deadline} दिनों के भीतर {amt_str} की पूरी राशि मेरे बैंक खाते में वापस करें, अन्यथा सक्षम रेंट अथॉरिटी में कानूनी कार्रवाई की जाएगी।\n\n"
                    f"भवदीय,\n\n"
                    f"{user_nm}\n(किरायेदार)\n\n"
                    f"--------------------------------------------------\n"
                    f"कानूनी अस्वीकरण:\n{cls.MANDATORY_DISCLAIMER}"
                )
            return (
                f"FORMAL WRITTEN DEMAND FOR REFUND OF SECURITY DEPOSIT\n"
                f"(Sent via Registered Post A.D. / Speed Post / Email)\n\n"
                f"Date: {date_str}\n\n"
                f"FROM:\n{user_nm}\n{user_addr}\n\n"
                f"TO:\n{c_nm}\n{c_addr}\n\n"
                f"SUBJECT: Formal Demand for immediate refund of Security Deposit amount of {amt_str} "
                f"in respect of tenancy at the subject premises.\n\n"
                f"Sir / Madam,\n\n"
                f"1. That I was inducted as a lawful tenant into the residential premises under your ownership/management, "
                f"having paid an upfront refundable security deposit amounting to {amt_str}.\n\n"
                f"2. That during the entire subsistence of the tenancy, I regularly cleared monthly rent and utility charges "
                f"without default, fulfilling all reciprocal obligations under law.\n\n"
                f"3. That peaceful and vacant possession of the premises was formally handed over on or about {inc_date}. "
                f"The premises was delivered in clean, habitable condition, subject only to normal wear and tear recognized under "
                f"Section 108(m) of the Transfer of Property Act, 1882.\n\n"
                f"4. That despite repeated amicable requests and follow-ups, you have wrongfully withheld/delayed refunding "
                f"the said security deposit of {amt_str}, without any legitimate justification or itemized damage proofs.\n\n"
                f"5. DEMAND: You are hereby called upon to refund the entire sum of {amt_str} to my bank account "
                f"within {deadline} days of receipt of this notice, failing which I shall be constrained to initiate appropriate "
                f"legal remedies before the competent Rent Authority / Civil Court under applicable laws, including claiming statutory "
                f"interest @ 18% p.a. and litigation costs entirely at your risk.\n\n"
                f"Yours sincerely,\n\n"
                f"{user_nm}\n(Tenant / Aggrieved Party)\n\n"
                f"--------------------------------------------------\n"
                f"LEGAL NOTICE DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 2. STATUTORY CHEQUE BOUNCE NOTICE (SECTION 138 NI ACT)
        elif req.doc_type == DocumentTypeEnum.CHEQUE_BOUNCE_NOTICE:
            return (
                f"STATUTORY DEMAND NOTICE UNDER SECTION 138 OF THE NEGOTIABLE INSTRUMENTS ACT, 1881\n"
                f"(SENT THROUGH REGISTERED POST WITH ACKNOWLEDGEMENT DUE / SPEED POST)\n\n"
                f"Date: {date_str}\n\n"
                f"TO:\n{c_nm}\n{c_addr}\n\n"
                f"FROM (PAYEE / HOLDER IN DUE COURSE):\n{user_nm}\n{user_addr}\n\n"
                f"SUBJECT: Statutory Demand Notice under Section 138 of the Negotiable Instruments Act, 1881 regarding dishonour of Cheque No. [Cheque Number] for {amt_str}.\n\n"
                f"Sir / Madam,\n\n"
                f"Under instructions from my Client aforesaid (or written on my own behalf as Payee), notice is hereby served upon you as follows:\n\n"
                f"1. That towards discharge of your legally enforceable debt and liability, you issued in favour of My Client Cheque bearing No. [______], dated [______], for an amount of {amt_str}, drawn on [Bank Name and Branch].\n\n"
                f"2. That My Client presented the said cheque for encashment through their bankers [Client Bank Name], but the same was dishonoured and returned unpaid vide Bank Return Memo dated {inc_date} with the endorsement: 'Funds Insufficient' / 'Exceeds Arrangement'.\n\n"
                f"3. That this statutory demand notice is issued to you within the mandatory period of thirty (30) days from the receipt of the return memo by My Client, as prescribed under Section 138, Proviso (b) of the Negotiable Instruments Act, 1881.\n\n"
                f"4. DEMAND: You are hereby called upon to pay the said cheque amount of {amt_str} to My Client within fifteen (15) days of the receipt of this notice.\n\n"
                f"5. TAKE NOTICE that if you fail to make payment of the said amount within the stipulated fifteen (15) days, My Client shall be constrained to initiate criminal proceedings against you under Section 138 of the Negotiable Instruments Act, 1881 before the competent Court of Judicial Magistrate / Metropolitan Magistrate, holding you liable for imprisonment up to two years and fine up to twice the cheque amount, along with legal expenses entirely at your peril.\n\n"
                f"Yours faithfully,\n\n"
                f"{user_nm}\n(Payee / Holder in Due Course)\n\n"
                f"--------------------------------------------------\n"
                f"LEGAL DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 3. POLICE COMPLAINT DRAFT (SECTION 173 BNSS 2023)
        elif req.doc_type == DocumentTypeEnum.POLICE_COMPLAINT:
            return (
                f"WRITTEN COMPLAINT UNDER SECTION 173 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (BNSS)\n"
                f"FOR REGISTRATION OF FIRST INFORMATION REPORT (FIR) IN A COGNIZABLE OFFENCE\n\n"
                f"Date: {date_str}\n\n"
                f"TO:\n"
                f"The Station House Officer (SHO),\n"
                f"Police Station: [Name of Police Station, {state_str}]\n\n"
                f"COPY FOR INTIMATION:\n"
                f"The Superintendent of Police / Deputy Commissioner of Police,\n"
                f"District: [{state_str}]\n\n"
                f"COMPLAINANT:\n{user_nm}\nS/o or D/o [Father/Spouse Name]\nResident of: {user_addr}\nMobile: [Contact Number] | Email: [Email Address]\n\n"
                f"ACCUSED / SUSPECT:\n{c_nm}\nAddress / Particulars: {c_addr}\n\n"
                f"SUBJECT: Written Complaint for registration of FIR under relevant sections of Bharatiya Nyaya Sanhita, 2023 (including Section 318 - Cheating, Section 316 - Criminal Breach of Trust, Section 351 - Criminal Intimidation) and applicable special statutes.\n\n"
                f"Sir / Madam,\n\n"
                f"I, the Complainant aforesaid, respectfully state the true facts of the matter as under:\n\n"
                f"1. STATEMENT OF FACTS:\n{facts_text}\n\n"
                f"2. That the accused person(s) acted with dishonest and fraudulent intention from the inception, inducing me to part with money / property totaling {amt_str} on or about {inc_date}.\n\n"
                f"3. That despite repeated requests, the accused has wrongfully misappropriated the said property and issued direct threats, causing severe mental distress and financial deprivation.\n\n"
                f"4. EVIDENCE ANNEXED:\n"
                f"   - Annexure A: Bank statements / UPI transaction proof of {amt_str}.\n"
                f"   - Annexure B: WhatsApp chat transcripts and audio records.\n"
                f"   - Annexure C: Invoices / relevant contractual documents.\n\n"
                f"5. PRAYER:\n"
                f"In view of the above cognizable offences, it is respectfully requested that:\n"
                f"  a) A formal FIR be registered under Section 173 BNSS 2023 against the accused person(s);\n"
                f"  b) A stamped receiving acknowledgment / Zero FIR number be issued to the Complainant immediately;\n"
                f"  c) Thorough investigation be initiated to recover the defrauded amount of {amt_str}.\n\n"
                f"Yours sincerely,\n\n"
                f"{user_nm}\n(Complainant / Informant)\n\n"
                f"--------------------------------------------------\n"
                f"LEGAL DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 4. CYBER CRIME COMPLAINT (1930 / CYBERCRIME.GOV.IN)
        elif req.doc_type == DocumentTypeEnum.CYBER_COMPLAINT:
            return (
                f"FORMAL CYBER CRIME INCIDENT REPORT\n"
                f"(For Submission to National Cyber Crime Reporting Portal - cybercrime.gov.in & Helpline 1930)\n\n"
                f"Date of Report: {date_str}\n\n"
                f"1. COMPLAINANT PARTICULARS:\n"
                f"   - Full Name: {user_nm}\n"
                f"   - Address: {user_addr}\n"
                f"   - Mobile No: [Registered Mobile Number]\n"
                f"   - State / Union Territory: {state_str}\n\n"
                f"2. SUSPECT / ACCUSED PARTICULARS:\n"
                f"   - Name / Profile Alias: {c_nm}\n"
                f"   - Suspect Phone / UPI ID / Account No.: {c_addr}\n"
                f"   - Platform / Medium: [WhatsApp / Telegram / Phishing Link / Fake Portal]\n\n"
                f"3. FINANCIAL LOSS DETAILS:\n"
                f"   - Total Amount Defrauded: {amt_str}\n"
                f"   - Complainant Bank & Account No.: [Bank Name & Account]\n"
                f"   - UTR / Transaction Reference Number(s): [Transaction IDs]\n"
                f"   - Date & Time of Debits: {inc_date}\n\n"
                f"4. INCIDENT NARRATIVE:\n{facts_text}\n\n"
                f"5. STATUTORY OFFENCES INVOLVED:\n"
                f"   - Section 66C (Identity Theft) & Section 66D (Cheating by Personation using computer resource) of Information Technology Act, 2000.\n"
                f"   - Section 318 (Cheating) of Bharatiya Nyaya Sanhita, 2023 (BNS).\n\n"
                f"6. RELIEF REQUESTED:\n"
                f"   - Immediate intimation to beneficiary bank/nodal officer to freeze destination accounts/wallets under Section 107 BNSS.\n"
                f"   - Registration of formal Cyber Crime FIR.\n\n"
                f"Complainant Signature: _______________________\n{user_nm}\n\n"
                f"--------------------------------------------------\n"
                f"LEGAL DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 5. RIGHT TO INFORMATION (RTI) APPLICATION (SECTION 6 RTI ACT 2005)
        elif req.doc_type == DocumentTypeEnum.RTI_APPLICATION:
            return (
                f"APPLICATION UNDER SECTION 6(1) OF THE RIGHT TO INFORMATION ACT, 2005\n\n"
                f"Date: {date_str}\n\n"
                f"TO:\n"
                f"The Public Information Officer (PIO) / Assistant Public Information Officer (APIO),\n"
                f"[Name of Public Authority / Department / Ministry],\n"
                f"[Office Address, {state_str}]\n\n"
                f"1. Full Name of the Applicant: {user_nm}\n"
                f"2. Address for Correspondence: {user_addr}\n"
                f"3. Citizenship: Indian Citizen (eligible under Section 3 of RTI Act, 2005)\n\n"
                f"4. PARTICULARS OF INFORMATION SOUGHT:\n"
                f"   Background: {facts_text}\n\n"
                f"   Specific Information Requested:\n"
                f"   (a) Please provide certified copies of file notings, orders, and action taken reports in respect of the above matter.\n"
                f"   (b) Please state the current official status and designated dealing officer responsible for the disposal.\n"
                f"   (c) Please provide the reasons recorded for delay, if any, in concluding the proceedings.\n\n"
                f"5. APPLICATION FEE DETAILS:\n"
                f"   Enclosed herewith Application Fee of ₹10/- vide [IPO No. / Demand Draft / Online RTI Receipt No. ______].\n\n"
                f"6. STATUTORY TIMELINE:\n"
                f"   As mandated under Section 7(1) of the RTI Act, 2005, the requested information may kindly be furnished within thirty (30) days of receipt.\n\n"
                f"Applicant Signature:\n\n"
                f"{user_nm}\n\n"
                f"--------------------------------------------------\n"
                f"LEGAL DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 6. CONSUMER COMPLAINT DRAFT (SECTION 35 CPA 2019)
        elif req.doc_type == DocumentTypeEnum.CONSUMER_COMPLAINT:
            return (
                f"BEFORE THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION\n"
                f"AT: {state_str.upper() if state_str else 'DISTRICT HEADQUARTERS'}\n\n"
                f"CONSUMER COMPLAINT NO. _______ / {datetime.now().year}\n"
                f"(Under Section 35 of the Consumer Protection Act, 2019)\n\n"
                f"IN THE MATTER OF:\n\n"
                f"{user_nm}\n{user_addr}\n... COMPLAINANT\n\n"
                f"VERSUS\n\n"
                f"{c_nm}\n{c_addr}\n... OPPOSITE PARTY\n\n"
                f"COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019 FOR DEFICIENCY IN SERVICE "
                f"AND UNFAIR TRADE PRACTICE RESULTING IN PECUNIARY LOSS.\n\n"
                f"MOST RESPECTFULLY SHOWETH:\n\n"
                f"1. That the Complainant is a consumer within the meaning of Section 2(7) of the Consumer Protection Act, 2019, "
                f"having purchased/availed goods/services from the Opposite Party against valuable consideration of {amt_str}.\n\n"
                f"2. That the Opposite Party is a commercial entity engaging in sales/services to the public.\n\n"
                f"3. BRIEF FACTS:\n{facts_text}\n\n"
                f"4. That the goods supplied were defective / delivery was deficient / promised refund of {amt_str} "
                f"was unlawfully denied, constituting gross deficiency in service and unfair trade practice under Section 2(47) of the Act.\n\n"
                f"5. PRAYER:\n"
                f"It is therefore most respectfully prayed that this Hon'ble Commission may graciously be pleased to:\n"
                f"  a) Direct the Opposite Party to refund the full consideration of {amt_str} along with interest @ 12% p.a.;\n"
                f"  b) Award compensation of ₹25,000/- towards mental agony, harassment, and severe inconvenience;\n"
                f"  c) Award litigation expenses to the Complainant;\n"
                f"  d) Pass any other order deemed just and equitable in the interest of justice.\n\n"
                f"DATED: {date_str}\nPLACE: {state_str}\n\n"
                f"{user_nm}\n(Complainant in Person)\n\n"
                f"--------------------------------------------------\n"
                f"DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 7. UNPAID SALARY / EMPLOYMENT DEMAND
        elif req.doc_type == DocumentTypeEnum.UNPAID_SALARY_DEMAND:
            return (
                f"FORMAL NOTICE AND DEMAND FOR DISBURSEMENT OF OUTSTANDING WAGES & STATUTORY DUES\n\n"
                f"Date: {date_str}\n\n"
                f"TO:\n"
                f"The Management / Human Resources,\n"
                f"{c_nm}\n{c_addr}\n\n"
                f"FROM:\n"
                f"{user_nm}\n{user_addr}\n\n"
                f"SUBJECT: Formal demand for clearance of earned salary and full and final settlement amounting to {amt_str}.\n\n"
                f"Sir / Madam,\n\n"
                f"1. That I was employed with {c_nm} and diligently performed my official duties in accordance with "
                f"company policy and terms of employment.\n\n"
                f"2. STATEMENT OF FACTS:\n{facts_text}\n\n"
                f"3. That despite having rendered bona fide service, my earned remuneration / settlement dues totaling {amt_str} "
                f"have remained unpaid beyond mandatory statutory timelines under Section 5 of the Payment of Wages Act, 1936 and applicable "
                f"State Shops and Commercial Establishments legislation.\n\n"
                f"4. That withholding an employee's legitimately earned remuneration is unlawful and constitutes a direct breach of contract "
                f"under Section 73 of the Indian Contract Act, 1872.\n\n"
                f"5. DEMAND: You are hereby called upon to remit the entire outstanding sum of {amt_str} to my bank account "
                f"and issue my Experience and Relieving Letter within {deadline} days of receipt of this notice. "
                f"In the event of failure, I shall lodge a formal complaint before the Labour Commissioner / Authority under Section 15 "
                f"of the Payment of Wages Act and pursue appropriate civil proceedings at your sole cost and consequence.\n\n"
                f"Yours faithfully,\n\n"
                f"{user_nm}\n(Employee)\n\n"
                f"--------------------------------------------------\n"
                f"DISCLAIMER:\n{cls.MANDATORY_DISCLAIMER}"
            )

        # 8. GENERAL FORMAL LEGAL NOTICE (FOR ADVOCATE REVIEW)
        elif req.doc_type in [DocumentTypeEnum.LEGAL_NOTICE, DocumentTypeEnum.GENERAL_LEGAL_NOTICE]:
            return (
                f"LEGAL NOTICE (DRAFT FOR ADVOCATE REVIEW)\n"
                f"(SENT THROUGH REGISTERED POST WITH ACKNOWLEDGEMENT DUE / SPEED POST)\n\n"
                f"Date: {date_str}\n\n"
                f"TO:\n{c_nm}\n{c_addr}\n\n"
                f"UNDER INSTRUCTIONS FROM AND ON BEHALF OF MY CLIENT:\n"
                f"{user_nm}, residing at {user_addr} (hereinafter referred to as 'My Client').\n\n"
                f"Sir / Madam,\n\n"
                f"Under instructions from my Client aforesaid, I hereby serve upon you this Legal Notice:\n\n"
                f"1. That My Client had lawful dealings with you in respect of the following matter:\n{facts_text}\n\n"
                f"2. That by your wrongful acts, omissions, and unilateral non-compliance, you have caused wrongful financial injury "
                f"amounting to {amt_str} to My Client on or about {inc_date}.\n\n"
                f"3. That your conduct is arbitrary, unlawful, and actionable under applicable substantive and civil laws of India.\n\n"
                f"4. DEMAND: I therefore call upon you, through this notice, to unconditionally fulfill the demands of My Client:\n"
                f"   - {demands_text}\n"
                f"   - Remit the sum of {amt_str} along with interest @ 18% p.a.\n\n"
                f"within a period of {deadline} days from the date of receipt hereof, failing which My Client has given "
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
                f"Complainant / Claimant: {user_nm} ({user_addr})\n"
                f"Respondent / Counterparty: {c_nm} ({c_addr})\n\n"
                f"DISPUTED AMOUNT: {amt_str}\n"
                f"KEY INCIDENT DATE: {inc_date}\n\n"
                f"SUMMARY OF FACTS:\n{facts_text}\n\n"
                f"RELIEF SOUGHT:\n{demands_text}\n\n"
                f"STATUTORY BASIS:\n"
                f"- Relevant provisions of Indian law governing breach, deficiency, or rights as applicable.\n"
                f"- Time given for voluntary compliance: {deadline} days.\n\n"
                f"Signature: _______________________\n"
                f"{user_nm}\n\n"
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
            alignment=1,
            spaceAfter=12
        )

        disclaimer_style = ParagraphStyle(
            'DisclaimerStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=11,
            textColor=red_alert,
            alignment=0,
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
        elements.append(Paragraph(f"<b>LEGAL DRAFT NOTICE:</b> {cls.MANDATORY_DISCLAIMER}", disclaimer_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceBefore=2, spaceAfter=12))

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

        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        title_p = doc.add_paragraph()
        title_run = title_p.add_run(title.upper())
        title_run.bold = True
        title_run.font.size = Pt(13)
        title_run.font.color.rgb = RGBColor(15, 23, 42)
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        disc_p = doc.add_paragraph()
        disc_run = disc_p.add_run(f"LEGAL NOTICE: {cls.MANDATORY_DISCLAIMER}")
        disc_run.bold = True
        disc_run.font.size = Pt(8.5)
        disc_run.font.color.rgb = RGBColor(153, 27, 27)

        doc.add_paragraph("-" * 75)

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
