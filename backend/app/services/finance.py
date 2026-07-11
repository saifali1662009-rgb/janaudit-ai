"""Extract explicit financial evidence. It never manufactures a number or spending stage."""
import re

from app.schemas import MoneyTrailItem
from app.services.sources import RetrievedSource

MONEY_PATTERN = re.compile(r"(?:₹|Rs\.?|INR)\s?[\d,]+(?:\.\d+)?\s*(?:crore|cr|lakh|million|billion)?|[\d,]+(?:\.\d+)?\s*(?:crore|cr|lakh)", re.IGNORECASE)
STAGES = [
    ("Allocation", ("allocation", "allocated", "budget estimate", "budget outlay", "outlay")),
    ("Approval / release", ("released", "sanctioned", "approved", "disbursed", "funding")),
    ("Expenditure / utilisation", ("spent", "expenditure", "utilised", "utilized", "utilisation", "utilization")),
    ("Delivery / outcome", ("completed", "beneficiaries", "delivered", "implemented", "progress", "financial assistance", "monthly assistance", "benefit")),
]

def money_trail(sources: list[RetrievedSource]) -> list[MoneyTrailItem]:
    findings: list[MoneyTrailItem] = []
    seen: set[tuple[str, str]] = set()
    for source in sources:
        # Do not treat the period in "Rs." as the end of a sentence.
        sentences = re.split(r"(?<=[.!?])\s+", source.excerpt.replace("Rs.", "Rs"))
        for sentence in sentences:
            compact = " ".join(sentence.split())
            lowered = compact.casefold()
            for stage, terms in STAGES:
                has_money = bool(MONEY_PATTERN.search(compact))
                if any(term in lowered for term in terms) and (has_money or stage == "Delivery / outcome"):
                    key = (stage, compact[:180])
                    if key not in seen:
                        seen.add(key)
                        findings.append(MoneyTrailItem(stage=stage, statement=compact[:500], source_title=source.title, url=source.url))
                    break
            if len(findings) >= 8:
                return findings
    return findings
