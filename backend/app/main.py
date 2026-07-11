from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.schemas import EvidenceSource, InvestigationRequest, ReportResponse, SearchRequest
from app.services.finance import money_trail
from app.services.mesh import rank_sources
from app.services.sources import retrieve_evidence
from app.services.intent import parse_query

@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()
    yield

app = FastAPI(title="Janaudit AI API", version="0.1.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mesh": "configured" if settings.mesh_api_key else "not configured"}

@app.post("/api/investigations", response_model=ReportResponse)
async def investigate(request: InvestigationRequest) -> ReportResponse:
    place = request.state if request.scope == "State" and request.state else request.scope
    sources = await retrieve_evidence(f"{request.subject} {place}")
    if not sources and request.scope == "State":
        sources = await retrieve_evidence(request.subject)
    if not sources:
        sources = await retrieve_evidence(f"{request.subject} Government of India")
    if not sources:
        return ReportResponse(
            subject=request.subject,
            scope=place,
            summary=f"Janaudit could not retrieve an accessible official source for {request.subject} during this search.",
            key_findings=["No financial or implementation claim has been made because no accessible source was retrieved."],
            confidence=0,
            limitations=["Government websites can block automated access or have no indexed page for a specific query.", "Try the official scheme or project name, a state, or return later for a fresh search."],
            sources=[],
            money_trail=[],
            used_mesh=False,
        )
    used_mesh = await rank_sources(f"{request.subject} {place} {' '.join(request.sections)}", sources)
    official_sources = sum(source.source_type in {"official", "audit", "parliament"} for source in sources)
    confidence = min(96, 42 + len(sources) * 10 + official_sources * 4)
    findings = [f"{source.publisher}: {source.title}" for source in sources[:3]]
    summary = f"Janaudit retrieved {len(sources)} accessible public source{'s' if len(sources) != 1 else ''} for {request.subject}. Open the evidence below to inspect the original wording, figures and publication dates."
    limitations = ["This report only covers pages that were accessible during this search.", "A source may describe an allocation, release or status update; those terms are not interchangeable.", "Janaudit does not infer corruption, success or failure from incomplete public records."]
    return ReportResponse(subject=request.subject, scope=place, summary=summary, key_findings=findings, confidence=confidence, limitations=limitations, sources=[EvidenceSource(**source.__dict__) for source in sources], money_trail=money_trail(sources), used_mesh=used_mesh)

@app.post("/api/search", response_model=ReportResponse)
async def search(request: SearchRequest) -> ReportResponse:
    """Natural search is parsed deterministically; it never calls an LLM for intent."""
    return await investigate(parse_query(request.query))
