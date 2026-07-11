from typing import Literal
from pydantic import BaseModel, Field

class InvestigationRequest(BaseModel):
    category: Literal["Government Scheme", "Infrastructure Project", "Ministry Budget", "Public Policy"]
    subject: str = Field(min_length=2, max_length=160)
    scope: Literal["National", "State"] = "National"
    state: str | None = Field(default=None, max_length=80)
    sections: list[str] = Field(default_factory=list, max_length=8)

class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)

class EvidenceSource(BaseModel):
    title: str
    url: str
    publisher: str
    excerpt: str
    source_type: Literal["official", "audit", "parliament", "news"]

class MoneyTrailItem(BaseModel):
    stage: Literal["Allocation", "Approval / release", "Expenditure / utilisation", "Delivery / outcome"]
    statement: str
    source_title: str
    url: str

class ReportResponse(BaseModel):
    subject: str
    scope: str
    summary: str
    key_findings: list[str]
    confidence: int = Field(ge=0, le=100)
    limitations: list[str]
    sources: list[EvidenceSource]
    money_trail: list[MoneyTrailItem]
    used_mesh: bool
