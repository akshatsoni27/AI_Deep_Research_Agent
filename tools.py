from langchain.tools import tool
import asyncio
import time
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

REQUEST_TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 1_000_000
MAX_CONTENT_CHARS = 3_000


def _clean_html(content: bytes, charset: str | None) -> str:
    started = time.perf_counter()
    encoding = charset or "utf-8"
    try:
        decoded = content.decode(encoding, errors="replace")
    except (LookupError, UnicodeError):
        decoded = content.decode("utf-8", errors="replace")

    soup = BeautifulSoup(decoded, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    cleaned = soup.get_text(separator=" ", strip=True)[:MAX_CONTENT_CHARS]
    print(f"Content cleaning: {time.perf_counter() - started:.2f}s")
    return cleaned


async def _fetch_url(session: aiohttp.ClientSession, url: str, index: int) -> str:
    started = time.perf_counter()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return f"URL {index} failed ({url}): invalid URL"

    try:
        async with session.get(url, allow_redirects=True) as response:
            response.raise_for_status()
            content = await response.content.read(MAX_RESPONSE_BYTES)
            text = _clean_html(content, response.charset)
            print(f"URL {index}: {time.perf_counter() - started:.2f}s ({url})")
            return f"URL: {url}\nContent: {text}"
    except asyncio.TimeoutError:
        message = "request timed out"
    except (aiohttp.ClientError, UnicodeError) as exc:
        message = str(exc)

    print(f"URL {index}: {time.perf_counter() - started:.2f}s ({message})")
    return f"URL {index} failed ({url}): {message}"


async def _fetch_urls(urls: list[str]) -> list[str]:
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}
    connector = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(timeout=timeout, headers=headers, connector=connector) as session:
        return await asyncio.gather(
            *(_fetch_url(session, url, index) for index, url in enumerate(urls, 1))
        )

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on an topic. Retutns Titles, URLs and snippets"""
    results = tavily.search(query=query, max_results=5)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )

    return "\n----\n".join(out)


@tool
def scrape_urls(urls: str) -> str:
    """Fetch newline-separated URLs concurrently and return cleaned text."""
    unique_urls = list(dict.fromkeys(url.strip() for url in urls.splitlines() if url.strip()))[:5]
    if not unique_urls:
        return "No valid URLs were provided."

    started = time.perf_counter()
    results = asyncio.run(_fetch_urls(unique_urls))
    print(f"Concurrent scraping ({len(unique_urls)} URLs): {time.perf_counter() - started:.2f}s")
    return "\n\n----\n\n".join(results)


@tool
def scrape_url(url: str) -> str:
    """Scrape one URL using the same bounded, encoding-safe fetcher."""
    return scrape_urls.invoke(url)

