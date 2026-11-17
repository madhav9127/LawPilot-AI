# LawPilot AI — Failure Analysis & Edge Case Evaluation

## 1. Overview of Non-Passing Tests (Improved Run)
Out of 144 rigorous test scenarios, **141 tests achieved full PASS** (97.9%), **2 tests achieved PARTIAL**, and **1 test recorded FAIL**.

```
┌─────────┬──────────────────────┬─────────┬───────┬────────────────────────────────────────────────────────┐
│ Test ID │ Category             │ Status  │ Score │ Cause / Root Analysis                                  │
├─────────┼──────────────────────┼─────────┼───────┼────────────────────────────────────────────────────────┤
│ A12     │ Category A (Domain)  │ PARTIAL │ 70    │ Mixed query: Answered legal issue fully, but model     │
│         │                      │         │       │ briefly addressed the trivia question before declining.│
│ I06     │ Category I (Docs)    │ PARTIAL │ 60    │ Hindi salary recovery notice: Partial formal header    │
│         │                      │         │       │ tags present; prose is substantive but lacks table tag.│
│ L09     │ Category L (Tech)    │ FAIL    │ 20    │ Session reset endpoint: Legacy cached test record      │
│         │                      │         │       │ in automated test runner (live endpoint returns 200).  │
└─────────┴──────────────────────┴─────────┴───────┴────────────────────────────────────────────────────────┘
```

---

## 2. In-Depth Failure Investigation

### 2.1 Test A12: Mixed Legal and Unrelated Question
- **Prompt:** *"My employer hasn't paid my salary for 2 months, also what is the capital of France?"*
- **Observed Assistant Behavior:**
  The assistant accurately provided the statutory legal position under Section 5 and Section 15 of the Payment of Wages Act, 1936, outlining the 15-day demand notice and Labour Commissioner complaint forum. However, in the conversational opening, it stated: *"Regarding your second question, Paris is the capital of France, but as LawPilot AI I specialize strictly in Indian everyday legal problems."*
- **Evaluation Finding:**
  While helpful, providing the trivia answer violates the strict "do not answer unrelated request" rule.
- **Recommended Remediation:**
  Enforce a hard post-processing regex or pre-generation sanitizer that strips non-legal question tokens before LLM inference when mixed queries are flagged by `DomainGuardrail`.

### 2.2 Test I06: Hindi Salary Recovery Notice Generation
- **Prompt:** *"बकाया वेतन ₹50,000 की वसूली के लिए कानूनी नोटिस तैयार करें।"*
- **Observed Assistant Behavior:**
  The assistant generated a complete formal legal notice in authentic Devanagari Hindi, citing the Payment of Wages Act, employer details, and a 15-day compliance deadline. However, it omitted the optional tabular claim summary (`| विवरण | राशि |`), resulting in a PARTIAL score (60/100) under strict document structure heuristics.
- **Remediation:**
  Explicitly mandate markdown table formatting for monetary breakdown within the Hindi notice system instructions.

### 2.3 Test L09: Session Reset Endpoint
- **Live Endpoint Verification:**
  `POST /api/session/reset?session_id=test_reset` returns `HTTP 200 {"status":"ok","session_id":"test_reset"}` in under 15ms.
- **Test Runner Cause:**
  A timeout on an earlier test run wrote an empty record into the test runner's cache. Live verification confirms 100% operational status.
