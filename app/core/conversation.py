import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class ConversationCaseMemory:
    """
    Maintains structured multi-turn conversation memory and case facts.
    Distinguishes:
      1. Facts explicitly provided by user
      2. Inferred information
      3. Information that is still unknown
    Handles real-time factual corrections (e.g. 'Correction, deposit was ₹35,000, not ₹30,000').
    """

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.turns: List[Dict[str, str]] = []
        self.reset_facts()

    def reset_facts(self):
        """Resets all tracked case facts."""
        self.explicit_facts = {
            "dispute_type": None,
            "category": None,
            "city": None,
            "state": None,
            "amount": None,
            "amount_raw": None,
            "vacate_date": None,
            "move_in_date": None,
            "incident_date": None,
            "user_role": None,
            "counterparty_name": None,
            "counterparty_role": None,
            "agreement_type": None,
            "available_evidence": [],
            "actions_taken": [],
            "desired_outcome": None
        }
        self.inferred_facts = {}
        self.unknown_facts = [
            "Exact financial amount in dispute",
            "Location (City / State)",
            "Key dates",
            "Written agreement status",
            "Available documentary evidence"
        ]

    def update_from_message(self, text: str):
        """Extracts and updates facts from a user turn, respecting corrections."""
        lower = text.lower().strip()

        # Ignore smalltalk / greetings / math from corrupting case memory
        if any(re.match(p, lower) for p in [
            r"^(hi|hello|hey|namaste|pranam|good\s*(morning|afternoon|evening))\b",
            r"^(what\s+is\s+|tell\s+me\s+a\s+joke|who\s+are\s+you|how\s+are\s+you)\b",
            r"^\d+\s*[\+\-\*\/]\s*\d+"
        ]):
            return

        # 1. Check for Corrections
        correction_match = re.search(
            r"correction[,:]?\s*(?:the\s+)?(?:deposit|amount|salary|rent)?\s*(?:was|is)?\s*[₹rs\.]*\s*([0-9,]+)",
            lower
        )
        if correction_match:
            new_val = int(correction_match.group(1).replace(",", ""))
            self.explicit_facts["amount"] = new_val
            self.explicit_facts["amount_raw"] = f"₹{new_val:,}"
            if "Exact financial amount in dispute" in self.unknown_facts:
                self.unknown_facts.remove("Exact financial amount in dispute")
            return

        # 2. Extract Category (with domain switch detection)
        detected_category = None
        if any(w in lower for w in [
            "landlord", "tenant", "deposit", "rent", "flat", "evict", "painting", "makandari", "kiraya", "makaan malik", "legal notice", "court notice", "notice received",
            "સિક્યોરિટી", "ડિપોઝિટ", "મકાનમાલિક", "ભાડું", "કાનૂની નોટિસ", "લીગલ નોટિસ", "किराया", "डिपॉज़िट", "मकान मालिक", "कानूनी नोटिस",
            "घरमालक", "घरमालकाकडून", "घरमालकाने", "भाडेकरू", "भाडे", "कायदेशीर नोटीस", "लीगल नोटीस",
            "വാടക", "ഡെപ്പോസിറ്റ്", "വാടകക്കാരൻ", "വീട്ടുടമസ്ഥൻ", "നോട്ടീസ്",
            "வாடகை", "வைப்புத்தொகை", "வீட்டு உரிமையாளர்", "நோட்டீஸ்",
            "అద్దె", "డిపాజిట్", "ఇంటి యజమాని", "నోటీసు",
            "ভাড়া", "আমানত", "বাড়িওয়ালা", "আইনি নোটিশ"
        ]):
            detected_category = "tenant"
        elif any(w in lower for w in [
            "phone", "laptop", "product", "defective", "order", "seller", "refund", "flipkart", "amazon", "e-commerce", "interior design", "service",
            "ખામીયુક્ત", "રિફંડ", "વેચનાર", "ખરીદ્યો", "ફોન", "दोषपूर्ण", "विक्रेता", "റീഫണ്ട്", "குறைபாடு", "ரீபண்ட்", "లోపం", "రీఫండ్", "ত্রুটি", "ফেরত"
        ]):
            detected_category = "consumer"
        elif any(w in lower for w in [
            "salary", "employer", "company", "boss", "wages", "resigned", "relieving", "fnf", "settlement",
            "પગાર", "નિયોક્તા", "કંપની", "वेतन", "नियोक्ता", "तनख्वाह", "തൊഴിലുടമ", "ശമ്പളം", "சம்பளம்", "நிறுவனம்", "జీతం", "యజమాని", "বেতন", "নিয়োগকর্তা"
        ]):
            detected_category = "employment"

        # If user switches domain mid-conversation, clear prior domain facts
        if detected_category and self.explicit_facts["category"] and detected_category != self.explicit_facts["category"]:
            self.reset_facts()

        if detected_category == "tenant":
            self.explicit_facts["category"] = "tenant"
            self.explicit_facts["user_role"] = "Tenant"
            self.explicit_facts["counterparty_role"] = "Landlord"
            if "deposit" in lower:
                self.explicit_facts["dispute_type"] = "Security deposit withholding"
            elif "painting" in lower:
                self.explicit_facts["dispute_type"] = "Arbitrary painting/repair deduction"
            elif "evict" in lower or "leave tomorrow" in lower:
                self.explicit_facts["dispute_type"] = "Unlawful eviction threat"
            elif "repair" in lower or "leak" in lower:
                self.explicit_facts["dispute_type"] = "Property repair & damages dispute"
            else:
                self.explicit_facts["dispute_type"] = "Tenancy dispute"

        elif detected_category == "consumer":
            self.explicit_facts["category"] = "consumer"
            self.explicit_facts["user_role"] = "Consumer / Buyer"
            self.explicit_facts["counterparty_role"] = "Seller / Service Provider"
            if "defective" in lower or "stopped working" in lower or "broken" in lower:
                self.explicit_facts["dispute_type"] = "Defective product"
            elif "refund" in lower:
                self.explicit_facts["dispute_type"] = "Refund delay or denial"
            elif "wrong" in lower or "different model" in lower:
                self.explicit_facts["dispute_type"] = "Wrong product delivered"
            elif "service" in lower:
                self.explicit_facts["dispute_type"] = "Deficiency in service"
            else:
                self.explicit_facts["dispute_type"] = "Consumer dispute"

        elif detected_category == "employment":
            self.explicit_facts["category"] = "employment"
            self.explicit_facts["user_role"] = "Employee"
            self.explicit_facts["counterparty_role"] = "Employer / Management"
            if "unpaid" in lower or "not paid" in lower or "delayed" in lower:
                self.explicit_facts["dispute_type"] = "Unpaid or delayed salary"
            elif "deduct" in lower:
                self.explicit_facts["dispute_type"] = "Unexplained salary deduction"
            elif "relieving" in lower or "settlement" in lower:
                self.explicit_facts["dispute_type"] = "Withheld final settlement & relieving letter"
            else:
                self.explicit_facts["dispute_type"] = "Employment and wage dispute"

        # 3. Extract Financial Amounts (if not already extracted via correction)
        if not self.explicit_facts["amount"]:
            # Check currency patterns: ₹25,000, Rs. 25000, 25k, 25,000
            amt_match = re.search(r"(?:₹|rs\.?|inr)\s*([0-9,]+)", lower)
            if not amt_match:
                amt_match = re.search(r"([0-9,]+)\s*(?:rs\.?|rupees|inr|k\b|thousand|hazar)", lower)
            if not amt_match:
                # Bare numbers
                amt_match = re.search(r"\b(\d{4,7})\b", lower)

            if amt_match:
                try:
                    num_str = amt_match.group(1).replace(",", "")
                    val = int(num_str)
                    if "k" in amt_match.group(0):
                        val *= 1000
                    self.explicit_facts["amount"] = val
                    self.explicit_facts["amount_raw"] = f"₹{val:,}"
                    if "Exact financial amount in dispute" in self.unknown_facts:
                        self.unknown_facts.remove("Exact financial amount in dispute")
                except ValueError:
                    pass

        # 4. Extract Location (City / State)
        cities = ["jaipur", "bangalore", "bengaluru", "delhi", "mumbai", "pune", "hyderabad", "chennai", "kolkata", "noida", "gurgaon", "lucknow", "ahmedabad"]
        for c in cities:
            if c in lower:
                self.explicit_facts["city"] = c.title()
                if "Location (City / State)" in self.unknown_facts:
                    self.unknown_facts.remove("Location (City / State)")
                break

        # 5. Extract Dates
        date_matches = re.findall(r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|[a-z]{3})\s*(?:20\d\d)?)\b", lower)
        if date_matches:
            self.explicit_facts["incident_date"] = date_matches[0]
            if "Key dates" in self.unknown_facts:
                self.unknown_facts.remove("Key dates")

        # 6. Extract Agreement Status
        if "no written" in lower or "bina agreement" in lower or "no agreement" in lower:
            self.explicit_facts["agreement_type"] = "Oral agreement / No formal written agreement"
            if "Written agreement status" in self.unknown_facts:
                self.unknown_facts.remove("Written agreement status")
        elif "rental agreement" in lower or "lease" in lower or "contract" in lower or "appointment letter" in lower:
            self.explicit_facts["agreement_type"] = "Written agreement exists"
            if "Written agreement status" in self.unknown_facts:
                self.unknown_facts.remove("Written agreement status")

        # 7. Extract Evidence Mentioned
        ev_items = self.explicit_facts["available_evidence"]
        if any(w in lower for w in ["upi", "bank transfer", "bank statement", "receipt"]):
            if "Bank / UPI transaction records" not in ev_items:
                ev_items.append("Bank / UPI transaction records")
        if any(w in lower for w in ["whatsapp", "chat", "messages"]):
            if "WhatsApp / SMS communications" not in ev_items:
                ev_items.append("WhatsApp / SMS communications")
        if any(w in lower for w in ["photo", "video", "unboxing"]):
            if "Photos / Video evidence" not in ev_items:
                ev_items.append("Photos / Video evidence")
        if any(w in lower for w in ["invoice", "bill", "payslip", "salary slip"]):
            if "Invoice / Payslips" not in ev_items:
                ev_items.append("Invoice / Payslips")
        if ev_items and "Available documentary evidence" in self.unknown_facts:
            self.unknown_facts.remove("Available documentary evidence")

    def format_case_summary(self) -> str:
        """Formats the structured 3-part Case Summary."""
        ef = self.explicit_facts
        
        # Explicit facts lines
        explicit_lines = []
        if ef["dispute_type"]: explicit_lines.append(f"- **Dispute Type:** {ef['dispute_type']}")
        if ef["user_role"] and ef["counterparty_role"]: explicit_lines.append(f"- **Parties Involved:** {ef['user_role']} vs {ef['counterparty_role']}")
        if ef["amount_raw"]: explicit_lines.append(f"- **Disputed Amount:** {ef['amount_raw']}")
        if ef["city"]: explicit_lines.append(f"- **Location:** {ef['city']}")
        if ef["incident_date"]: explicit_lines.append(f"- **Incident / Vacate Date:** {ef['incident_date']}")
        if ef["agreement_type"]: explicit_lines.append(f"- **Agreement Status:** {ef['agreement_type']}")
        if ef["available_evidence"]: explicit_lines.append(f"- **Available Evidence:** {', '.join(ef['available_evidence'])}")

        if not explicit_lines:
            explicit_lines.append("- Primary details are being gathered from your conversation.")

        # Inferred facts lines
        inferred_lines = []
        if ef["category"] == "tenant":
            inferred_lines.append("- Tenancy relationship governed by general civil/tenancy law (Transfer of Property Act, 1882).")
        elif ef["category"] == "consumer":
            inferred_lines.append("- Consumer transaction falls under the Consumer Protection Act, 2019.")
        elif ef["category"] == "employment":
            inferred_lines.append("- Wage recovery governed by Payment of Wages Act, 1936 or state commercial establishments rules.")
        else:
            inferred_lines.append("- Standard civil legal principles apply.")

        # Unknown facts lines
        unknown_lines = [f"- {u}" for u in self.unknown_facts] if self.unknown_facts else ["- All primary case parameters have been recorded."]

        summary_md = (
            "### 📋 Your Case Summary\n\n"
            "**1. Facts Explicitly Provided by You:**\n" +
            "\n".join(explicit_lines) + "\n\n"
            "**2. Inferred Legal Context:**\n" +
            "\n".join(inferred_lines) + "\n\n"
            "**3. Information Still Needed:**\n" +
            "\n".join(unknown_lines)
        )
        return summary_md

    def get_natural_follow_up(self, language_code: str = "en") -> Optional[str]:
        """Returns at most 1 or 2 targeted, natural follow-up questions."""
        ef = self.explicit_facts

        # Priority 1: Missing Amount
        if not ef["amount"]:
            if ef["category"] == "employment":
                if language_code == "hi":
                    return "आपकी मासिक सैलरी कितनी तय थी और कुल कितना वेतन बकाया है?"
                elif language_code == "gu":
                    return "તમારો માસિક પગાર કેટલો નક્કી થયેલ હતો અને કુલ કેટલું વેતન બાકી છે?"
                elif language_code == "hinglish":
                    return "Aapki monthly salary kitni thi aur total kitna salary amount pending hai?"
                else:
                    return "What was your agreed monthly salary and the total unpaid salary amount?"
            elif ef["category"] == "consumer":
                if language_code == "hi":
                    return "आपने उस उत्पाद के लिए कुल कितनी राशि का भुगतान किया था?"
                elif language_code == "gu":
                    return "તમે તે ખામીયુક્ત ઉત્પાદન માટે કુલ કેટલી રકમ ચૂકવી હતી?"
                elif language_code == "hinglish":
                    return "Aapne defective product ke liye total kitna payment kiya tha?"
                else:
                    return "What was the total purchase price paid for the defective product?"
            else:
                if language_code == "hi":
                    return "कृपया बताएं कि कुल कितनी सुरक्षा राशि (रुपयों में) विवादित है?"
                elif language_code == "gu":
                    return "કૃપા કરીને જણાવો કે કુલ કેટલી સિક્યોરિટી ડિપોઝિટ (રૂપિયામાં) બાકી છે?"
                elif language_code == "hinglish":
                    return "Dispute me total kitna deposit amount (₹ me) involved hai?"
                else:
                    return "What is the exact amount of money (in ₹) involved in this dispute?"

        # Priority 2: Missing Location
        if not ef["city"] and not ef["state"]:
            if language_code == "hi":
                return "यह संपत्ति या घटना किस शहर या राज्य से संबंधित है?"
            elif language_code == "gu":
                return "આ મિલકત અથવા કંપની કયા શહેર કે રાજ્યમાં આવેલી છે?"
            elif language_code == "hinglish":
                return "Ye rented flat ya company kis city/state me located hai?"
            else:
                return "Which city or state is the property or company located in? (Tenancy and shops laws vary by state)."

        # Priority 3: Evidence Check
        if not ef["available_evidence"]:
            if language_code == "hi":
                return "क्या आपके पास कोई रेंट एग्रीमेंट, बैंक ट्रांसफर रसीद, या ईमेल/व्हाट्सएप चैट रिकॉर्ड है?"
            elif language_code == "gu":
                return "શું તમારી પાસે ભાડા કરાર, બેંક ટ્રાન્સફર રસીદ અથવા ઇમેઇલ/ચેટ રેકોર્ડ ઉપલબ્ધ છે?"
            elif language_code == "hinglish":
                return "Kya aapke paas written agreement, bank transfer proof ya chat record available hai?"
            else:
                return "Do you possess written evidence such as agreements, payment receipts, or chat logs?"

        return None
        if not ef["available_evidence"]:
            if language_code == "hi":
                return "क्या आपके पास इस संबंध में कोई लिखित प्रमाण जैसे बैंक ट्रांसफर रसीद, ईमेल या व्हाट्सऐप चैट मौजूद है?"
            elif language_code == "hinglish":
                return "Kya aapke paas bank transaction, UPI receipt ya WhatsApp chats ka koi proof available hai?"
            else:
                return "Do you have transaction records (like bank/UPI receipts) or communication logs (like WhatsApp or email)?"

        return None
