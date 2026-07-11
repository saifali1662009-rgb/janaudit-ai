"""Deterministic natural-language parsing. No LLM is used for intent detection."""
import re

from app.schemas import InvestigationRequest

REGIONS = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

def parse_query(query: str) -> InvestigationRequest:
    text = query.casefold()
    state = next((item for item in REGIONS if item.casefold() in text), None)
    category = "Government Scheme"
    if any(word in text for word in ("highway", "expressway", "metro", "bridge", "railway", "airport", "road", "project")):
        category = "Infrastructure Project"
    elif any(word in text for word in ("ministry", "department", "budget")):
        category = "Ministry Budget"
    elif any(word in text for word in ("policy", "act", "bill", "guideline")):
        category = "Public Policy"
    sections = ["Overview", "Official sources"]
    if any(word in text for word in ("latest", "news", "recent", "today")):
        sections.append("Latest updates")
    if any(word in text for word in ("budget", "fund", "spent", "utilisation", "allocation")):
        sections.append("Budget & utilisation")
    subject = re.sub(r"\b(how|what|where|when|why|is|the|in|for|about|latest|news|budget|spent|funds?|utilisation|allocation)\b", " ", query, flags=re.IGNORECASE)
    subject = re.sub(r"\s+", " ", subject).strip(" ?.,") or query
    return InvestigationRequest(category=category, subject=subject, scope="State" if state else "National", state=state, sections=sections)
