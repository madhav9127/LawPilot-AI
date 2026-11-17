# LawPilot AI — Legal Grounding & Retrieval-Augmented Generation (RAG)

## 1. Grounding Architecture
LawPilot AI employs an active Retrieval-Augmented Generation (RAG) pipeline paired with a curated Statutory Knowledge Base (`LegalKnowledgeBase`):
- **Domain Categorization:** Incoming user grievances are classified into Tenancy, Consumer, or Employment categories via `CaseBuilder`.
- **Statutory Retrieval:** Relevant central and state statutory sections are fetched with official act names, section numbers, titles, and statutory descriptions.
- **Citation Injection:** Verified provisions are injected into the system prompt as grounding context, strictly bounding the model's legal generation.
- **Verification Metadata:** Each retrieved statute contains official verification status (`Verified source available`), commencement date, and jurisdiction.

---

## 2. Statutory Knowledge Base Coverage

| Domain | Primary Acts & Codes | Verified Sections Included |
|---|---|---|
| **Tenancy & Housing** | Model Tenancy Act, 2021<br>Transfer of Property Act, 1882<br>State Rent Control Acts (Maharashtra, Karnataka, Delhi) | Sec 13 (MTA - Security Deposit Limit)<br>Sec 21 (MTA - Eviction Protection)<br>Sec 106 (TPA - Notice of Termination)<br>Sec 108 (TPA - Rights & Liabilities of Lessee/Lessor) |
| **Consumer Protection** | Consumer Protection Act, 2019<br>Consumer Protection (E-Commerce) Rules, 2020 | Sec 2(7) (Consumer Definition)<br>Sec 2(11) (Deficiency of Service)<br>Sec 2(47) (Unfair Trade Practice)<br>Sec 35 (Manner of Filing Complaint)<br>Sec 84 (Product Liability)<br>Rule 5 (E-Commerce Refund Deadlines) |
| **Employment & Wages** | Payment of Wages Act, 1936<br>Industrial Disputes Act, 1947<br>State Shops & Commercial Establishments Acts | Sec 5 (Time of Payment of Wages: 7th/10th day)<br>Sec 7 (Deductions Permissible by Law)<br>Sec 15 (Claims Arising from Deductions/Delays) |
| **Free Legal Aid** | Legal Services Authorities Act, 1987 | Sec 12 (Criteria for Free Legal Aid via NALSA / SLSA / DLSA) |

---

## 3. Anti-Hallucination Safeguards

1. **Repealed Act Handling:** Detects queries referencing the repealed *Consumer Protection Act, 1986* and actively informs the user of its replacement by the modern *Consumer Protection Act, 2019*.
2. **Non-Existent Section Refusal:** When queried about fictional sections (e.g., *Section 999* of the Model Tenancy Act), the assistant explicitly states that the section does not exist and redirects the user to genuine statutory mechanisms.
3. **No Fabricated Supreme Court Precedents:** When prompted to invent case laws or automatic 24-hour refund rulings, LawPilot AI refuses to fabricate citations, stating that judicial precedents must be verified in official law reporters (SCC / AIR).
4. **State Jurisdictional Awareness:** Explicitly clarifies when a provision depends on State government notification (such as adoption of the Model Tenancy Act) rather than universal central application.
