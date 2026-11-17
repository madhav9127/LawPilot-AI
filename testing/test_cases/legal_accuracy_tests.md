# Categories B, C & D: Legal Accuracy & Grounding Test Specifications

## 1. Domain Coverage & Statutory Grounding Framework
LawPilot AI evaluates legal disputes against authentic Indian statutes without inventing sections, penalties, or deadlines:
1. **Tenant & Landlord Disputes (Category B):** Model Tenancy Act, 2021 (Sec 13, 21), Transfer of Property Act, 1882 (Sec 106, 108), State Rent Control Acts. Key principles: reasonable wear & tear, mandatory notice before eviction, itemized deduction statements, proof of tenancy via bank/UPI records.
2. **Consumer Protection Disputes (Category C):** Consumer Protection Act, 2019 (Sec 2(7), 2(47), 35, 84), Consumer Protection (E-Commerce) Rules, 2020 (Rule 5). Key principles: deficiency of service, product liability, unfair trade practice ("No Refund" clauses voided), e-commerce platform responsibilities.
3. **Employment & Salary Disputes (Category D):** Payment of Wages Act, 1936 (Sec 5, 7, 15), Industrial Disputes Act, 1947, Contract Labour Act, 1970. Key principles: timely wage payment (7th/10th day), unauthorized deduction prohibitions, recovery through Labour Commissioner.

## 2. Test Inventory: Category B — Tenant & Landlord Disputes (B01 – B12)

| Test ID | Scenario / Legal Issue | Key Statutory Grounding | Expected Assistant Response |
|---|---|---|---|
| **B01** | ₹25,000 security deposit withheld after vacating premises. | Model Tenancy Act 2021 / State Rent Control | Identifies deposit retention; recommends formal written demand granting 15-30 days; Rent Authority escalation. |
| **B02** | ₹30,000 deposit; landlord deducts ₹15,000 for repainting without agreement clause. | MTA 2021 Sec 13 / TPA Sec 108(m) | Differentiates reasonable wear and tear from tenant damage; landlord cannot unilaterally deduct painting without clause. |
| **B03** | Tenancy without written lease; tenant has UPI transaction receipts. | Indian Evidence Act / Section 107 TPA | Explains that oral tenancy is recognized; bank/UPI statements prove monthly rent and deposit transactions. |
| **B04** | Severe water leakage; landlord refuses structural repairs. | MTA 2021 / TPA Sec 108(f) | Distinguishes structural maintenance (landlord duty) from minor upkeep; advises formal repair notice. |
| **B05** | Threat of immediate eviction tomorrow despite rent being paid. | MTA Sec 21 / TPA Sec 106 | Clarifies that summary self-help eviction is illegal in India; eviction requires due process of law and court order. |
| **B06** | Landlord falsely denies receiving initial deposit. | Banking evidence / Sec 91 Evidence Act | Recommends retrieving bank transaction IDs and statement stamps to establish factual payment. |
| **B07** | Partial deposit returned; ₹10,000 withheld without reason. | Natural justice / Section 13 MTA | Demands written itemized deduction breakdown and receipts; prepares demand notice for remaining balance. |
| **B08** | Pre-existing dampness and wall cracks blamed on vacating tenant. | Move-in inspection / Wear & tear principles | Advises using move-in photographs, move-in checklists, and witness testimony to rebut damage claims. |
| **B09** | Landlord refuses to provide itemized bills for repair deductions. | Transparency under MTA / CPA | Advises that deductions without supporting invoices are unsubstantiated; prepares formal audit demand. |
| **B10** | Landlord ignoring all WhatsApp messages and phone calls. | Formal legal notice delivery | Recommends issuing legal demand notice via Speed Post with Acknowledgment Due (AD) to establish legal proof. |
| **B11** | Tenant has no physical rent receipts but clean bank passbook. | TPA Sec 107 / Evidence Act | Reassures tenant that bank passbooks with recurring monthly credits establish regular tenancy. |
| **B12** | Tenant unsure whether MTA or State Rent Control Act applies. | Jurisdictional clarity & state adoption | Explains that tenancy is a State subject; distinguishes MTA model framework from enacted State Rent Acts. |

## 3. Test Inventory: Category C — Consumer Protection Disputes (C01 – C12)

| Test ID | Scenario / Legal Issue | Key Statutory Grounding | Expected Assistant Response |
|---|---|---|---|
| **C01** | Brand new smartphone (₹15,000) defective on arrival; seller refuses refund. | CPA 2019 Sec 2(47), Sec 35 | Explains consumer right to defect-free goods; identifies unfair trade practice; recommends Consumer Forum (e-Daakhil). |
| **C02** | E-commerce return approved; refund not credited for 15 business days. | E-Commerce Rules 2020 Rule 5 | Identifies unjust enrichment and deficiency in service; recommends formal escalation to grievance officer. |
| **C03** | Wrong laptop model delivered (₹60,000); seller refuses return. | CPA 2019 Sec 2(11) Deficiency | Highlights seller's statutory obligation to deliver ordered specification; advises chargeback and consumer notice. |
| **C04** | ₹1,00,000 paid for interior design service; contractor never showed up. | CPA 2019 Sec 2(11) Deficiency of Service | Explains complete failure of consideration; prepares legal notice for full refund plus interest. |
| **C05** | TV screen failed at 6 months; brand refuses in-warranty replacement. | CPA 2019 Sec 84 Product Liability | Explains manufacturer warranty bindingness; cites statutory remedy against warranty repudiation. |
| **C06** | E-commerce marketplace claims it is merely an intermediary. | E-Commerce Rules 2020 / CPA Sec 86 | Explains marketplace liability for returns, refunds, and verified merchant tracking under 2020 Rules. |
| **C07** | Restaurant or service provider levying non-consensual service charges. | CCPA Guidelines 2022 | Clarifies that mandatory service charges are illegal; consumer can demand removal or lodge NCH complaint. |
| **C08** | Defective product purchased without paper invoice (has SMS/UPI proof). | CPA 2019 Sec 2(7) Consumer definition | Confirms digital payment record establishes consumer relationship even in absence of paper invoice. |
| **C09** | Fragile package damaged during transit; courier disclaims liability. | Carriage by Road Act / CPA Deficiency | Identifies carrier deficiency; explains sender/recipient consumer standing to claim compensation. |
| **C10** | Merchant displays "Goods once sold will not be taken back or refunded". | CPA 2019 Sec 2(47) Unfair Trade Practice | Clarifies that blanket "no refund" notices cannot override statutory rights for defective products. |
| **C11** | Defective appliance causing electrical short circuit and personal injury. | CPA 2019 Chapter VI (Product Liability) | Explains product liability claim covering both product cost and consequential property/physical damage. |
| **C12** | User seeking compensation for mental harassment and loss of time. | Consumer Commission jurisprudence | Recommends claiming reasonable compensation along with principal refund, subject to Commission discretion. |

## 4. Test Inventory: Category D — Employment & Salary Disputes (D01 – D12)

| Test ID | Scenario / Legal Issue | Key Statutory Grounding | Expected Assistant Response |
|---|---|---|---|
| **D01** | Employer withheld 2 months salary after employee gave notice. | Payment of Wages Act 1936 Sec 5, 15 | Emphasizes that salary earned cannot be withheld; specifies 7th/10th day statutory deadline; Labour Commissioner remedy. |
| **D02** | Full and Final (FnF) settlement delayed beyond 90 days. | State Shops and Establishments Act | Advises that FnF must typically be settled within 30 days of last working day; drafts formal HR demand. |
| **D03** | Employer refusing to issue Relieving and Experience Letter. | Indian Contract Act / Service Jurisprudence | Explains that withholding service certificates is unlawful; prepares legal demand notice to management. |
| **D04** | Arbitrary deductions from salary for alleged office laptop damage. | Payment of Wages Act 1936 Sec 7 | Explains permissible statutory deductions; deductions require written notice, hearing, and proof of fault. |
| **D05** | Unpaid salary in startup; founder stopped answering calls. | Payment of Wages Act / Sec 447 Companies Act | Recommends serving registered notice to company registered address and directors; Labour Commissioner complaint. |
| **D06** | Employer enforcing 3-year employment bond with ₹5 Lakh penalty. | Indian Contract Act Sec 27 | Explains that restraint of trade clauses are void under Indian law; employer can only recover actual training expenses. |
| **D07** | Sudden termination without notice pay or retrenchment compensation. | Industrial Disputes Act / Shops & Est. Act | Outlines statutory notice period pay requirements (typically 30 days or contract period). |
| **D08** | Overtime hours worked regularly without overtime compensation. | Factories Act Sec 59 / Shops & Est. Act | Identifies statutory double-rate overtime entitlement for eligible employees. |
| **D09** | Maternity leave benefits denied by private employer. | Maternity Benefit Act, 1961 | Explains mandatory 26 weeks paid maternity leave; clarifies penal consequences for non-compliance. |
| **D10** | Employer deducting Provident Fund (PF) but not depositing with EPFO. | EPF & MP Act 1952 Sec 14 | Highlights criminal breach of trust; advises lodging complaint with Regional Provident Fund Commissioner (EPFO). |
| **D11** | Unpaid sales commissions despite achieving confirmed quotas. | Indian Contract Act / Wage Definition | Confirms earned incentive commissions form part of wages; outlines recovery process. |
| **D12** | Confusion between Labour Court, civil suit, and NCLT insolvency petition. | Statutory Forum Distinction | Clearly distinguishes Labour Commissioner (salary claims) from civil court and insolvency tribunals. |
