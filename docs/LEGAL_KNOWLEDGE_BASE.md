# LawPilot AI — Verified Indian Legal Knowledge Base Specification

## 1. Statutory Grounding Philosophy

LawPilot AI relies on a curated, verified statutory registry (`LegalKnowledgeBase.VERIFIED_STATUTES`) representing authoritative Central and State Indian legislation. Each entry is anchored directly in authentic statutory text, official government portals (India Code, e-Gazette, Department websites), and commencement dates.

Hallucination of non-existent section numbers, fake precedents, or repealed provisions is prevented by pre-retrieval grounding: the LLM is supplied with verified statutory excerpts and instructed never to fabricate provisions outside verified law.

---

## 2. Official Government & Judicial Portals Indexed

LawPilot AI connects and references 22 authoritative government, judicial, and regulatory digital portals:

| Portal Key | Authority / Body | Official URL | Primary Domain Covered |
| :--- | :--- | :--- | :--- |
| `india_code` | Ministry of Law and Justice | https://www.indiacode.nic.in/ | Central & State Acts Repository |
| `egazette` | Ministry of Housing & Urban Affairs | https://egazette.gov.in/ | Official Gazette Notifications & Amendments |
| `sci` | Supreme Court of India | https://www.sci.gov.in/ | Supreme Court Judgments & Cause Lists |
| `ecourts` | e-Courts Mission Mode Project | https://ecourts.gov.in/ | District Court & High Court Case Tracking |
| `doj` | Department of Justice | https://doj.gov.in/ | Judicial Administration & Fast Track Courts |
| `lawmin` | Ministry of Law and Justice | https://lawmin.gov.in/ | Legislative Drafting, Law Commission |
| `nalsa` | National Legal Services Authority | https://nalsa.gov.in/ | Free Legal Aid (15100), Lok Adalats |
| `consumeraffairs` | Dept. of Consumer Affairs | https://consumeraffairs.nic.in/ | Consumer Rights & Standards |
| `consumerhelpline` | National Consumer Helpline | https://consumerhelpline.gov.in/ | Pre-litigation INGRAM Portal (1915) |
| `edaakhil` | National Consumer Commission | https://edaakhil.nic.in/ | Electronic Consumer Complaint Filing |
| `labour` | Ministry of Labour & Employment | https://labour.gov.in/ | Labour Codes, Wages, Gratuity, Industrial Disputes |
| `shram_suvidha` | Shram Suvidha Portal | https://shramsuvidha.gov.in/ | Commercial & Shops Act Registration |
| `mha` | Ministry of Home Affairs | https://www.mha.gov.in/ | BNS, BNSS, BSA Codes, Police Notifications |
| `cybercrime` | National Cyber Crime Reporting | https://cybercrime.gov.in/ | 1930 Financial Fraud Reporting |
| `rbi` | Reserve Bank of India | https://www.rbi.org.in/ | Banking Regulation, Master Directions |
| `cms_rbi` | RBI Complaint Management | https://cms.rbi.org.in/ | Integrated Banking Ombudsman Scheme |
| `irdai` | Insurance Regulatory Development Authority | https://irdai.gov.in/ | Policyholder Protection & Insurance Ombudsman |
| `incometax` | Income Tax Department | https://incometaxindia.gov.in/ | Income Tax Act, Faceless Assessment |
| `gst` | Goods and Services Tax Network | https://www.gst.gov.in/ | GST Notices, ITC, Form DRC-01 |
| `meity` | Ministry of Electronics & IT | https://www.meity.gov.in/ | IT Act 2000, DPDP Act 2023 |
| `ipindia` | Controller General of Patents, Designs & TM | https://ipindia.gov.in/ | Trademark Registry, Patent Journal |
| `greentribunal` | National Green Tribunal | https://greentribunal.gov.in/ | Environmental Civil Dispute Benches |

---

## 3. Comprehensive Domain Statutory Index

### A. Constitutional Law
- **Constitution of India, 1950 (Article 14)**: Equality before the law; protection against arbitrary state action.
- **Constitution of India, 1950 (Article 21)**: Right to life and personal liberty; dignity, privacy, and speedy trial.
- **Constitution of India, 1950 (Article 32 & 226)**: Power of Supreme Court and High Courts to issue writs of *Habeas Corpus*, *Mandamus*, *Prohibition*, *Quo Warranto*, and *Certiorari*.

### B. Modern Criminal Law (Effective 1 July 2024)
- **Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)**:
  - *Section 173*: Information in cognizable cases (Mandatory FIR, Zero FIR, e-FIR) [Historical: Sec 154 CrPC].
  - *Section 482 & 479*: Anticipatory bail before High Court / Sessions Court and undertrial bail liberalisation [Historical: Sec 438/436 CrPC].
  - *Section 107*: Police power to seize or freeze bank accounts with reporting to Magistrate [Historical: Sec 102 CrPC].
  - *Section 144*: Secular order for monthly maintenance of wives, children, and elderly parents [Historical: Sec 125 CrPC].
- **Bharatiya Nyaya Sanhita, 2023 (BNS)**:
  - *Section 318*: Cheating and dishonestly inducing delivery of property [Historical: Sec 415/420 IPC].
  - *Section 316 & 303*: Criminal breach of trust and theft [Historical: Sec 405/406 & 378/379 IPC].
  - *Section 351*: Criminal intimidation [Historical: Sec 503/506 IPC].
- **Bharatiya Sakshya Adhiniyam, 2023 (BSA)**:
  - *Section 61 & 63*: Admissibility of electronic records and certificate requirement [Historical: Sec 65B IEA].

### C. Civil Law & Procedure
- **Code of Civil Procedure, 1908 (CPC)**:
  - *Order XXXVII (Order 37)*: Summary suits on negotiable instruments and liquidated debts.
  - *Order XXXIX (Order 39)*: Temporary injunctions (stay orders) and interlocutory orders.
- **The Limitation Act, 1963**:
  - *Section 3 & Schedule*: 3-year general limitation period for recovery of money or breach of contract.
- **The Specific Relief Act, 1963**:
  - *Section 6*: Summary recovery of immovable property if dispossessed without consent.

### D. Family Law
- **Protection of Women from Domestic Violence Act, 2005 (PWDVA)**:
  - *Sections 12, 18, 19, 20*: Protection orders, residence in shared household, monetary maintenance.
- **The Hindu Marriage Act, 1955**:
  - *Section 13 & 13B*: Fault divorce grounds and divorce by mutual consent.
  - *Section 24*: Maintenance pendente lite and litigation expenses.
- **The Special Marriage Act, 1954**:
  - *Section 27 & 28*: Civil marriage dissolution and mutual consent divorce.

### E. Property & Real Estate
- **Real Estate (Regulation and Development) Act, 2016 (RERA)**:
  - *Section 18 & 31*: Builder delay compensation (SBI MCLR + 2%) and refund orders.
- **The Transfer of Property Act, 1882**:
  - *Section 106*: Month-to-month lease termination notice (15 days).
  - *Section 108(m)*: Restoration of leased premises subject only to reasonable wear and tear.
- **Model Tenancy Act, 2021**:
  - *Section 11 & 13*: Cap on residential security deposits (2 months) and succession of tenancy.
- **The Registration Act, 1908**:
  - *Section 17 & 49*: Mandatory registration of leases exceeding 11 months.

### F. Consumer Protection
- **The Consumer Protection Act, 2019 (CPA 2019)**:
  - *Section 2(7)*: Definition of consumer including offline and e-commerce transactions.
  - *Section 2(47)*: Unfair trade practices (refusal to refund or take back defective items).
  - *Section 35 & 38*: Filing complaints before District Commission and e-Daakhil.
- **Consumer Protection (E-Commerce) Rules, 2020**:
  - *Rule 4 & 6*: Mandatory Grievance Officer, 48-hour acknowledgment, 1-month resolution.

### G. Employment & Labour Law
- **The Payment of Wages Act, 1936**:
  - *Section 5 & 15*: Payment within 7–10 days of wage period; claims with 10x compensation.
  - *Section 7*: Strict enumeration of permissible deductions.
- **The Sexual Harassment of Women at Workplace (POSH) Act, 2013**:
  - *Section 4 & 9*: Internal Committee (IC) constitution and 90-day inquiry timeframe.
- **The Payment of Gratuity Act, 1972**:
  - *Section 4 & 7*: Gratuity after 5 years continuous service; 30-day payment mandate.
- **The Industrial Disputes Act, 1947**:
  - *Section 33C(2)*: Labour Court recovery of dues for workmen.

### H. Cyber Law & Digital Personal Data
- **The Information Technology Act, 2000**:
  - *Section 66C & 66D*: Identity theft and online cheating by personation.
  - *Section 43A*: Corporate compensation for failure to protect sensitive data.
- **Digital Personal Data Protection Act, 2023 (DPDP)**:
  - *Section 6, 8, 11*: Consent requirements, fiduciary obligations, Data Protection Board.

### I. Banking & Financial Law
- **The Negotiable Instruments Act, 1881**:
  - *Section 138*: Dishonour of cheque (15-day notice, 2 years imprisonment, 2x fine).
- **Reserve Bank - Integrated Ombudsman Scheme, 2021**:
  - *Clause 8 & 10*: Free grievance redressal for bank deficiency and recovery agent harassment.

### J. Taxation Law
- **The Income-tax Act, 1961**:
  - *Section 148 & 148A*: Escaped income reassessment notice and mandatory preliminary inquiry.
- **The Central Goods and Services Tax Act, 2017 (CGST)**:
  - *Section 73 & 74*: Determination of unpaid tax, DRC-01 show cause notices, ITC mismatch.

### K. Intellectual Property Law (IPR)
- **The Copyright Act, 1957 (Section 51 & 55)**: Injunctions, damages, and profits for infringement.
- **The Trade Marks Act, 1999 (Section 29 & 134)**: Infringement, passing off, commercial court suit.

### L. Motor Vehicle & Accident Law
- **The Motor Vehicles Act, 1988/2019**:
  - *Section 166*: MACT compensation claim within 6 months.
  - *Section 161*: Enhanced hit-and-run compensation (₹2 Lakhs for death, ₹50,000 for grievous hurt).

### M. Insurance Law
- **Insurance Ombudsman Rules, 2017 (Rule 13 & 14)**:
  - Cost-free resolution of claim repudiation up to ₹30 Lakhs.

### N. Environmental Law
- **The National Green Tribunal Act, 2010 (Section 14 & 15)**:
  - Civil environmental dispute adjudication, restitution within 6 months.

### O. Administrative & RTI Law
- **The Right to Information Act, 2005 (Section 6, 7 & 19)**:
  - ₹10 application fee, 30-day disposal, First and Second Appeals to Information Commission.

### P. Immigration & Citizenship Law
- **The Passports Act, 1967 (Section 6 & 10)**:
  - Refusal grounds; Section 6(2)(f) court NOC requirement for citizens facing minor pending criminal cases.

### Q. Alternative Dispute Resolution (ADR)
- **The Arbitration and Conciliation Act, 1996 (Section 8, 9 & 11)**:
  - Mandatory reference to arbitration, interim measures by court.
- **The Mediation Act, 2023 (Section 5, 19 & 27)**:
  - Mediated settlement agreements given equivalent legal enforceability as court decrees.
- **The Legal Services Authorities Act, 1987 (Section 12 & 19)**:
  - Free legal aid (NALSA Helpline 15100) and finality of Lok Adalat awards.
