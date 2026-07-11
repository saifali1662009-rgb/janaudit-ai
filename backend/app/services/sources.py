from dataclasses import dataclass
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
import httpx
from bs4 import BeautifulSoup
from app.config import get_settings

TRUSTED_DOMAINS = {
    "cag.gov.in": ("CAG", "audit"),
    "pib.gov.in": ("Press Information Bureau", "official"),
    "indiabudget.gov.in": ("Union Budget", "official"),
    "sansad.in": ("Parliament", "parliament"),
    "gov.in": ("Government of India", "official"),
}

@dataclass
class RetrievedSource:
    title: str
    url: str
    publisher: str
    excerpt: str
    source_type: str

def classify(url: str) -> tuple[str, str] | None:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    for domain, value in TRUSTED_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return value
    return None

def result_url(url: str) -> str:
    """Unwrap DuckDuckGo's redirect before checking whether a result is official."""
    parsed = urlparse(url)
    if "duckduckgo.com" in parsed.netloc:
        return unquote(parse_qs(parsed.query).get("uddg", [url])[0])
    return url

async def extract_page(client: httpx.AsyncClient, url: str) -> str:
    try:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        if "text/html" not in response.headers.get("content-type", ""):
            return ""
        page = BeautifulSoup(response.text, "html.parser")
        for tag in page(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return " ".join(page.stripped_strings)[:3000]
    except httpx.HTTPError:
        return ""

async def retrieve_evidence(query: str, limit: int = 5) -> list[RetrievedSource]:
    """Retrieve accessible authoritative sources and discard everything else."""
    settings = get_settings()
    encoded = quote_plus(f"{query} (site:gov.in OR site:cag.gov.in OR site:pib.gov.in OR site:sansad.in)")
    headers = {"User-Agent": "JanauditAI/0.1 (public-finance-research)"}
    async with httpx.AsyncClient(headers=headers, timeout=settings.request_timeout_seconds) as client:
        from app.services.official_registry import registry_sources
        official = await registry_sources(query, client)
        try:
            result = await client.get(f"https://html.duckduckgo.com/html/?q={encoded}")
            result.raise_for_status()
        except httpx.HTTPError:
            return official
        results = BeautifulSoup(result.text, "html.parser")
        candidates: list[tuple[str, str]] = []
        for link in results.select("a.result__a"):
            url = result_url(link.get("href", ""))
            if classify(url) and url not in [item[1] for item in candidates]:
                candidates.append((link.get_text(" ", strip=True), url))
            if len(candidates) == limit:
                break
        evidence: list[RetrievedSource] = []
        for title, url in candidates:
            source_info = classify(url)
            excerpt = await extract_page(client, url)
            if source_info and excerpt:
                publisher, source_type = source_info
                evidence.append(RetrievedSource(title=title[:200], url=url, publisher=publisher, excerpt=excerpt, source_type=source_type))
        combined = official + [source for source in evidence if source.url not in {item.url for item in official}]
        return combined[:limit]
