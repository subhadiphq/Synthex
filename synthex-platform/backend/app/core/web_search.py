"""
Synthex Web Search — DuckDuckGo Integration
Free, no API key required. Used by Research and Web Search agents.
"""
import httpx
from typing import Optional


async def search_duckduckgo(query: str, max_results: int = 5) -> list[dict]:
    """
    Search DuckDuckGo Instant Answer API.
    Free, no key needed, privacy-respecting.
    """
    results = []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # DuckDuckGo Instant Answer API
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
            )
            if response.status_code == 200:
                data = response.json()
                # Abstract (main answer)
                if data.get("AbstractText"):
                    results.append({
                        "title": data.get("Heading", "Result"),
                        "snippet": data["AbstractText"],
                        "url": data.get("AbstractURL", ""),
                        "source": data.get("AbstractSource", "")
                    })
                # Related topics
                for topic in data.get("RelatedTopics", [])[:max_results]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "")[:80],
                            "snippet": topic.get("Text", ""),
                            "url": topic.get("FirstURL", ""),
                            "source": "DuckDuckGo"
                        })

    except Exception as e:
        print(f"Web search error: {e}")

    return results[:max_results]


def format_search_results(results: list[dict]) -> str:
    """Format search results as readable text for AI processing."""
    if not results:
        return "No search results found."
    
    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"[{i}] {r.get('title', 'Result')}\n"
            f"    {r.get('snippet', '')}\n"
            f"    Source: {r.get('url', 'Unknown')}"
        )
    return "\n\n".join(formatted)


class WebSearchEngine:
    """Web search engine wrapper — uses DuckDuckGo (free, no key)."""
    async def search(self, query: str, max_results: int = 5) -> list:
        return await search_duckduckgo(query, max_results)

    async def format_results(self, results: list) -> str:
        return format_results(results)

    async def search_and_format(self, query: str, max_results: int = 5) -> str:
        results = await search_duckduckgo(query, max_results)
        return format_results(results)


web_search_engine = WebSearchEngine()

# Alias for backward compatibility
format_results = format_search_results

