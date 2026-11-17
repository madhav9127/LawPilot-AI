# Category I: Document Generation Test Specifications

## 1. Document Generation Architecture
LawPilot AI enables users to generate structured legal demand notices, formal complaints, and employer escalation emails:
- **Statutory Precision:** Explicitly grounds demands in applicable statutory provisions (e.g. Model Tenancy Act, Consumer Protection Act 2019, Payment of Wages Act 1936).
- **Placeholder Handling:** When essential party or timeline facts are missing (such as landlord's full address, lease execution date), clean placeholders `[Like This]` are inserted rather than hallucinating details.
- **Multilingual Drafting:** Drafts notices entirely in the user's preferred Indian language (e.g. Gujarati, Hindi, Marathi) when requested.
- **Anti-Hallucination Integrity:** Firmly refuses to insert fabricated sections or non-existent judicial citations into formal legal drafts.

## 2. Test Cases Inventory: Category I (I01 – I10)

| Test ID | Document Type & Scope | Input Prompt | Expected Draft Characteristics |
|---|---|---|---|
| **I01** | Security Deposit Demand Notice | `Draft a formal legal notice to my landlord for refunding ₹25,000 security deposit.` | Includes sender/recipient blocks, premises description, ₹25,000 claim, 15-day refund deadline, statutory reference, notice of legal action. |
| **I02** | Consumer Forum Complaint Draft | `Draft a consumer complaint for a defective phone costing ₹18,000.` | Structured with forum title, complainant/opposite party details, transaction chronology, deficiency description, prayer for refund + compensation. |
| **I03** | Unpaid Salary Demand Email to HR | `Draft an email to HR demanding my unpaid salary of ₹75,000.` | Professional, firm tone; employee ID placeholders; cites Payment of Wages Act Sec 5; 7-day compliance window. |
| **I04** | Notice with Missing Details | `Draft a notice to my landlord (I don't know his full address or last name).` | Successfully generates draft using clean placeholders: `[Landlord Full Name]`, `[Landlord Registered Address]`. |
| **I05** | Gujarati Consumer Complaint | `ખામીયુક્ત ફોન માટે ગ્રાહક ફરિયાદનો ડ્રાફ્ટ તૈયાર કરો.` | Complete draft generated in 100% fluent Gujarati script; CPA 2019 provisions; 0 English fallback; 0 mojibake. |
| **I06** | Hindi Salary Recovery Notice | `बकाया वेतन ₹50,000 की वसूली के लिए कानूनी नोटिस तैयार करें।` | Complete formal notice in pure Devanagari Hindi; Payment of Wages Act references; formal Hindi legal nomenclature. |
| **I07** | Marathi Tenancy Notice | `घरमालकाला अनामत रक्कम ₹20,000 परत करण्यासाठी कायदेशीर नोटीस तयार करा.` | Fluent Devanagari Marathi notice draft; 15-day demand period; 0 mojibake. |
| **I08** | English Reply to Landlord Notice | `My landlord sent me an eviction notice claiming I damaged walls. Draft my reply.` | Firm, evidence-backed reply denying unlawful deductions; highlights reasonable wear and tear under TPA Sec 108. |
| **I09** | Fact Correction & Regeneration | Turn 1: Drafts notice for ₹20,000 -> Turn 2: "Update amount to ₹28,000 and regenerate." | Immediately regenerates the full legal notice with updated ₹28,000 claim across all paragraphs. |
| **I10** | Refusal of Fabricated Citation | `Draft a legal notice citing Section 999 of the Model Tenancy Act which mandates 500% penalty.` | Assistant refuses to cite fictional Section 999; drafts notice based solely on authentic statutory provisions. |
