"""
Lightweight Title Generator for LawPilot AI
Generates short (2-5 words), professional, meaningful conversation titles
based on the legal topic of the first user message without making additional LLM calls.
"""

import re
from typing import Optional
from app.models.schemas import CaseCategoryEnum


def generate_conversation_title(message: str, category: Optional[CaseCategoryEnum] = None) -> str:
    """
    Analyzes the initial user message and produces a concise, professional title.
    Supports English, Hindi, Hinglish, and Malayalam.
    Returns a 2-5 word title.
    """
    if not message or not message.strip():
        return "New Consultation"

    lower = message.lower().strip()

    # 1. Greetings & casual intro
    if re.match(r"^(hi|hello|hey|namaste|pranam|good\s*(morning|afternoon|evening))\b", lower) and len(lower.split()) <= 4:
        return "General Consultation"
    if any(q in lower for q in ["what is your name", "who are you", "what can you help me with", "help"]):
        return "LawPilot AI Overview"

    # 2. Tenancy & Landlord Disputes
    if any(k in lower for k in ["evict", "eviction", "threat to evict", "nikal raha hai", "khali karne"]):
        return "Eviction Dispute"
    
    if any(k in lower for k in ["deposit", "security deposit", "25,000", "25000", "advance", "dharohar", "डिपॉज़िट"]):
        if any(d in lower for d in ["deduct", "painting", "maintenance", "damage", "katoti", "kaat"]):
            return "Deposit Deduction Dispute"
        return "Security Deposit Dispute"

    if any(k in lower for k in ["rent agreement", "rental agreement", "agreement", "lease", "kirayanama", "किराया"]):
        if any(h in lower for h in ["hike", "increase", "badha"]):
            return "Rent Increase Dispute"
        return "Rental Agreement Issue"

    if any(k in lower for k in ["landlord", "tenant", "makan malik", "kirayedar", "flat", "pg", "room"]):
        if any(r in lower for r in ["repair", "damage", "seepage", "water", "electricity"]):
            return "Tenancy Property Issue"
        return "Tenant Landlord Dispute"

    # 3. Employment & Wage Disputes
    if any(k in lower for k in ["salary", "unpaid", "wages", "pay", "vetan", "tankhwah", "tankha", "वेतन", "ശമ്പളം"]):
        if any(d in lower for d in ["deduct", "cut", "katoti"]):
            return "Salary Deduction Dispute"
        return "Unpaid Salary Issue"

    if any(k in lower for k in ["relieving", "experience letter", "relieving letter", "service certificate"]):
        return "Relieving Letter Request"

    if any(k in lower for k in ["fnf", "full and final", "f&f", "settlement", "resignation"]):
        return "Employment Settlement Dispute"

    if any(k in lower for k in ["terminate", "termination", "fired", "layoff", "laid off", "job loss", "resign"]):
        return "Employment Termination Issue"

    if any(k in lower for k in ["employer", "company", "boss", "hr", "workplace"]):
        return "Employment Dispute"

    # 4. Consumer Protection & E-Commerce
    if any(k in lower for k in ["defective", "damaged", "broken", "faulty", "kharab", "soap bar"]):
        if any(r in lower for r in ["phone", "mobile", "laptop", "product", "item", "device"]):
            return "Defective Product Refund"
        return "Defective Goods Complaint"

    if any(k in lower for k in ["refund", "money back", "return", "wapas", "paise wapas", "റീഫണ്ട്"]):
        return "Consumer Refund Issue"

    if any(k in lower for k in ["amazon", "flipkart", "meesho", "myntra", "courier", "e-commerce", "online order"]):
        return "E-Commerce Consumer Dispute"

    if any(k in lower for k in ["unfair charge", "hidden charge", "overcharge", "billed", "bill"]):
        return "Unfair Billing Dispute"

    if any(k in lower for k in ["warranty", "guarantee", "service center", "repair refusal"]):
        return "Consumer Warranty Grievance"

    # 5. Legal Notices & Documents
    if any(k in lower for k in ["legal notice", "court notice", "notice received", "got a notice", "vakil ka notice"]):
        return "Legal Notice Assistance"

    # 6. Category-based fallback if detected
    if category == CaseCategoryEnum.TENANT:
        return "Tenant Rights Issue"
    elif category == CaseCategoryEnum.EMPLOYMENT:
        return "Employment Rights Issue"
    elif category == CaseCategoryEnum.CONSUMER:
        return "Consumer Rights Issue"

    # 7. Intelligent generic fallback: extract key content words (2-4 words)
    # Remove common filler words
    stop_words = {
        "i", "me", "my", "myself", "we", "our", "you", "your", "he", "she", "it", "they",
        "am", "is", "are", "was", "were", "be", "have", "has", "had", "do", "does", "did",
        "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of",
        "at", "by", "for", "with", "about", "against", "between", "into", "through", "during",
        "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on",
        "off", "over", "under", "again", "further", "then", "once", "here", "there", "when",
        "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        "s", "t", "can", "will", "just", "don", "should", "now", "please", "help", "want",
        "need", "tell", "what", "which", "who", "whom", "this", "that", "these", "those"
    }
    
    # Strip punctuation
    clean_words = re.findall(r'\b[A-Za-z0-9\u0900-\u097F\u0D00-\u0D7F]+\b', message)
    content_words = [w.capitalize() for w in clean_words if w.lower() not in stop_words]

    if len(content_words) >= 2:
        return " ".join(content_words[:4])
    elif len(content_words) == 1:
        return f"{content_words[0]} Legal Inquiry"

    # Default fallback
    return "Legal Consultation"
