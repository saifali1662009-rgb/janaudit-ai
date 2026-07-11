"""Verified official entry points used only when ordinary retrieval misses them.

The short fallback excerpts preserve exact facts from the cited public pages. They let the
app remain useful when a government server blocks automated fetching, while the original
official URL remains visible and clickable for verification.
"""
from app.services.sources import RetrievedSource, extract_page, classify

Route = tuple[str, str, str]

OFFICIAL_ROUTES: list[tuple[tuple[str, ...], list[Route]]] = [
    (
        ("indiaai", "india ai mission"),
        [
            (
                "Cabinet Approves IndiaAI Mission",
                "https://www.pmindia.gov.in/en/news_updates/cabinet-approves-ambitious-indiaai-mission-to-strengthen-the-ai-innovation-ecosystem/",
                "The Cabinet approved the comprehensive national-level IndiaAI Mission with a budget outlay of Rs. 10,371.92 crore.",
            ),
            (
                "PIB: IndiaAI Mission",
                "https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=2012375&lang=2&reg=48",
                "The Government of India approved over Rs. 10,300 crore for the IndiaAI Mission to expand compute infrastructure and support AI startups.",
            ),
        ],
    ),
    (
        ("ladli behna", "ladli bahna", "ladli behna yojana", "ladli bahna yojana"),
        [
            (
                "Mukhyamantri Ladli Bahna Yojna, Madhya Pradesh",
                "https://services.india.gov.in/service/detail/mukymantri-ladli-bahana-yojna-madhya-pradesh",
                "Under the Madhya Pradesh Mukhyamantri Ladli Bahna Scheme, beneficiary women receive financial assistance of Rs. 1,250 per month.",
            ),
            (
                "Mukhyamantri Ladli Bahna Yojana portal",
                "https://cmladlibahna.mp.gov.in/index.html",
                "The official Madhya Pradesh portal provides scheme information and application services for Mukhyamantri Ladli Bahna Yojana.",
            ),
        ],
    ),
    (
        ("delhi mumbai expressway", "delhi mumbai highway", "delhi-mumbai expressway"),
        [
            (
                "PIB: Delhi-Mumbai Expressway",
                "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2039504&lang=2&reg=48",
                "The Ministry reported 53 packages over 1,386 km; as of June 2024, 26 packages were complete, physical progress was 82%, and 1,136 km had been constructed.",
            ),
            (
                "Rajya Sabha reply: Delhi-Mumbai Expressway",
                "https://sansad.in/getFile/annex/265/AU1054_o7lyP6.pdf?source=pqars",
                "A written Rajya Sabha reply reported 82% physical progress as of June 2024 and a revised scheduled completion date of October 2025.",
            ),
        ],
    ),
]

async def registry_sources(query: str, client) -> list[RetrievedSource]:
    normalized = query.casefold().replace("–", "-")
    routes = next((sources for aliases, sources in OFFICIAL_ROUTES if any(alias in normalized for alias in aliases)), [])
    evidence: list[RetrievedSource] = []
    for title, url, fallback_excerpt in routes:
        source_info = classify(url) or ("Government of India", "official")
        fetched_excerpt = await extract_page(client, url)
        publisher, source_type = source_info
        # Keep the verified fallback fact even when a portal returns only navigation text.
        excerpt = f"{fetched_excerpt}\n{fallback_excerpt}" if fetched_excerpt else fallback_excerpt
        evidence.append(RetrievedSource(title=title, url=url, publisher=publisher, excerpt=excerpt, source_type=source_type))
    return evidence
