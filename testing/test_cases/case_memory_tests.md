# Category H: Case Building & Multi-Turn Memory Test Specifications

## 1. Architectural Memory Design
LawPilot AI maintains conversation memory through `ConversationCaseMemory` and `SESSION_MEMORIES`:
- **State Preservation:** Key entities (parties, monetary amounts, property addresses, transaction dates) are tracked across turns.
- **Contradiction Resolution:** When a user updates or corrects a previously stated fact (e.g., "Actually the deposit was ₹35,000, not ₹25,000"), the assistant updates the case representation without hallucinating or mixing both figures.
- **Fact vs Assumption Separation:** Explicitly distinguishes confirmed facts provided by the user from open assumptions or legal inferences.
- **Session Isolation:** Guarantees that conversation facts and legal documents generated in session A do not leak into session B.

## 2. Test Cases Inventory: Category H (H01 – H10)

| Test ID | Multi-Turn Sequence / Test Focus | Expected Memory Behavior | Verification Criterion |
|---|---|---|---|
| **H01** | Turn 1: Landlord dispute ₹25,000 -> Turn 2: "What is my next step?" | Remembers landlord and ₹25,000; provides next steps directly without asking who the landlord is. | Retains parties and amounts across turns. |
| **H02** | Turn 1: Unpaid salary for 2 months (₹80,000) -> Turn 2: "Draft an email to HR" | Prepares demand email specifically citing ₹80,000 and 2 months duration. | Generated document incorporates prior facts. |
| **H03** | Turn 1: Defective television delivered -> Turn 2: "They offered a coupon, should I take it?" | Remembers defective television context; evaluates adequacy of store credit vs legal refund under CPA 2019. | Contextually grounded legal assessment. |
| **H04** | Fact Correction (Amount): Turn 1 stated ₹20,000 -> Turn 2: "Actually the deposit was ₹30,000, not ₹20,000" | Assistant acknowledges update, updates claim to ₹30,000; ceases citing ₹20,000. | Zero contradiction or double-counting. |
| **H05** | Fact Correction (Date): Turn 1 stated vacated in January -> Turn 2: "Sorry, I meant vacated in March" | Updates timeline; adjusts notice calculation and limitation periods accordingly. | Timeline reflects corrected date. |
| **H06** | Structured Case Summary Request: "Summarize everything we discussed so far." | Generates clean summary table: Parties, Core Grievance, Financial Claim, Applicable Statutes, Recommended Action. | High-fidelity structured representation. |
| **H07** | Missing Information Audit: "What details am I still missing to file a case?" | Accurately identifies unprovided facts (e.g. landlord's full legal name, permanent address, written lease copy). | Pinpoints specific evidentiary gaps. |
| **H08** | Evidence Checklist Request: "What proof do I need before sending a notice?" | Produces comprehensive checklist: Bank transaction URNs, WhatsApp chat exports, move-out handover notes, photographs. | Practical, actionable evidence inventory. |
| **H09** | Separation of Facts vs Inferences: "Can you list the facts we know for sure?" | Lists only explicitly stated user facts; separates them from statutory inferences. | Zero fabricated facts. |
| **H10** | Session Isolation Verification: Requesting facts across two distinct `session_id` tokens. | Confirms session A facts cannot be accessed from session B; returns fresh slate. | Strict session data boundary. |
