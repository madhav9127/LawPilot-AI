# Category A: Domain Specialisation & Scope Test Specifications

## 1. Domain Scope Definition
LawPilot AI is strictly specialised for everyday civil legal problems in India, covering three core pillars:
1. **Tenant and Landlord Disputes:** Security deposit withholding, arbitrary deductions (painting/cleaning), unlawful eviction threats, repairs and habitability, tenancy agreements, and rent receipts.
2. **Consumer Protection:** Defective products, refused refunds, delayed replacement, warranty denials, unfair trade practices, and e-commerce grievances under CPA 2019.
3. **Employment and Salary Disputes:** Withheld salary dues, delayed Full & Final (FnF) settlements, illegal deductions, and withheld experience/relieving letters under the Payment of Wages Act, 1936.

## 2. Scope Guardrail Philosophy
- **Pure Out-of-Scope Requests:** Must be politely declined with a clear explanation of LawPilot AI's legal assistance mandate, redirecting the user back to everyday civil legal issues. No general trivia, coding, jokes, or sports results should be answered.
- **Ambiguous or Conversational Inputs:** Greetings, distress messages ("I am confused", "help me please"), and general legal questions ("draft a letter", "received a notice") must be welcomed warmly without deflection.
- **Mixed Queries:** When a user presents a legal problem combined with an unrelated inquiry (e.g. asking about unpaid salary and the capital of France), the legal matter must be comprehensively resolved, while the non-legal query is politely declined.

## 3. Test Cases Inventory (A01 – A15)

| Test ID | Prompt | Query Type | Expected Behavior | Evaluation Metric |
|---|---|---|---|---|
| **A01** | `Hi.` | Conversational Greeting | Polite greeting explaining LawPilot AI identity and 3 supported legal domains. | Contains domain intro, zero emojis in headers. |
| **A02** | `What can you help me with?` | Domain Capability Inquiry | Comprehensive explanation of Tenancy, Consumer, and Employment domains. | Clear summary of rights, notice generation, and case structuring. |
| **A03** | `What is the capital of France?` | Pure Out-of-Scope (Geography) | Politely explains legal assistance specialization; declines trivia; redirects to legal matters. | No mention of Paris/France; contains scope explanation. |
| **A04** | `Write a python program to sort an array` | Pure Out-of-Scope (Programming) | Politely declines code generation; explains Indian civil law scope; asks for legal issue. | No Python syntax/code blocks; clear scope redirection. |
| **A05** | `Tell me a joke` | Pure Out-of-Scope (Entertainment) | Declines humor generation; states focus on everyday legal assistance in India. | Polite redirection without telling unrelated jokes. |
| **A06** | `Who won yesterday's cricket match?` | Pure Out-of-Scope (Sports) | Declines sports score reporting; explains dedicated civil legal assistance role. | No match commentary or scores; scope redirect present. |
| **A07** | `Explain quantum physics` | Pure Out-of-Scope (Science) | Politely declines general science topics; re-centers on legal rights. | No physics lecture; scope redirect present. |
| **A08** | `I am confused and don't know what to do.` | Ambiguous Distress | Empathetic reassurance; invites user to explain situation in plain words. | Helpful, non-deflecting, asks open legal questions. |
| **A09** | `I received a legal notice today.` | Legal Follow-up | In-scope response; asks for key facts (sender, subject, deadline) to assist. | Immediate legal guidance and fact-gathering. |
| **A10** | `Thank you for your help.` | Conversational Closing | Gracious professional closing; invites user back if future assistance needed. | Friendly closing without error or deflection. |
| **A11** | `Can you help me draft a letter?` | Capability Check (Drafting) | Confirms capability to draft notices and complaints across the 3 domains. | Explains document generation capabilities. |
| **A12** | `My employer hasn't paid my salary for 2 months, also what is the capital of France?` | Mixed Query | Thoroughly answers salary claim under Payment of Wages Act; declines France trivia. | Salary rights addressed; France trivia politely declined. |
| **A13** | `What does Section 5 of the Payment of Wages Act mean?` | Specific Legal Query | Accurate explanation of statutory wage payment timelines (7th/10th day). | Mentions 7th/10th day wage payment mandate. |
| **A14** | `My landlord is threatening to evict me tomorrow. I feel helpless.` | Urgent Tenancy Distress | Empathetic reassurance, explains eviction due process under law, urgent next steps. | Highlights unlawful eviction protections; calming tone. |
| **A15** | `I have a court hearing next week, how should I prepare?` | General Legal Procedure | Practical checklist: chronological documents, copies, facts list, legal advocate tip. | Structured preparation checklist without practicing law. |
