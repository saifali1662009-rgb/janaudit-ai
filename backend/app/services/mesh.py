import math
import httpx
from app.config import get_settings
from app.services.sources import RetrievedSource

def cosine_similarity(left: list[float], right: list[float]) -> float:
    denominator = math.sqrt(sum(value * value for value in left)) * math.sqrt(sum(value * value for value in right))
    return sum(a * b for a, b in zip(left, right)) / denominator if denominator else 0.0

async def rank_sources(query: str, sources: list[RetrievedSource]) -> bool:
    """Rank evidence through Mesh embeddings; no text-generation model is used."""
    settings = get_settings()
    if not settings.mesh_api_key or not sources:
        return False
    payload = {"model": settings.mesh_embedding_model, "input": [query] + [f"{source.title}\n{source.excerpt}" for source in sources]}
    headers = {"Authorization": f"Bearer {settings.mesh_api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post("https://api.meshapi.ai/v1/embeddings", headers=headers, json=payload)
            response.raise_for_status()
        vectors = [item["embedding"] for item in response.json()["data"]]
        query_vector = vectors[0]
        scored = [(cosine_similarity(query_vector, vectors[index + 1]), source) for index, source in enumerate(sources)]
        sources[:] = [source for _, source in sorted(scored, key=lambda item: item[0], reverse=True)]
        return True
    except (httpx.HTTPError, KeyError, IndexError, TypeError):
        return False
