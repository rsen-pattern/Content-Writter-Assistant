"""Page scraper – full scrape (competitors) and light scrape (internal URLs)."""

from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import trafilatura


@dataclass
class PageData:
    url: str
    title: str = ""
    meta_description: str = ""
    h1: str = ""
    headings: list[dict] = field(default_factory=list)
    word_count: int = 0
    content: str = ""
    internal_links: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    faqs: list[dict] = field(default_factory=list)
    tables: list[str] = field(default_factory=list)
    error: str = ""


def _fetch_html(url: str, timeout: int = 15) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, timeout=timeout, headers=headers)
    resp.raise_for_status()
    return resp.text


def _extract_headings(soup: BeautifulSoup) -> list[dict]:
    headings = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        headings.append({"level": tag.name.upper(), "text": tag.get_text(strip=True)})
    return headings


def _extract_faqs(soup: BeautifulSoup) -> list[dict]:
    """Extract FAQ-like Q&A from structured data or common FAQ patterns."""
    faqs = []

    # JSON-LD FAQ schema
    import json

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "FAQPage":
                        data = item
                        break
            if isinstance(data, dict) and data.get("@type") == "FAQPage":
                for entity in data.get("mainEntity", []):
                    q = entity.get("name", "")
                    a = entity.get("acceptedAnswer", {}).get("text", "")
                    if q:
                        faqs.append({"question": q, "answer": a})
        except (json.JSONDecodeError, TypeError):
            continue

    # Common FAQ accordion patterns
    for details in soup.find_all("details"):
        summary = details.find("summary")
        if summary:
            q = summary.get_text(strip=True)
            a = details.get_text(strip=True).replace(q, "", 1).strip()
            faqs.append({"question": q, "answer": a})

    return faqs


def _extract_tables(soup: BeautifulSoup) -> list[str]:
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            rows.append(" | ".join(cells))
        if rows:
            tables.append("\n".join(rows))
    return tables


def full_scrape(url: str) -> PageData:
    """Full scrape for competitor pages."""
    page = PageData(url=url)
    try:
        html = _fetch_html(url)
    except Exception as e:
        page.error = str(e)
        return page

    soup = BeautifulSoup(html, "lxml")

    # Title
    title_tag = soup.find("title")
    page.title = title_tag.get_text(strip=True) if title_tag else ""

    # Meta description
    meta = soup.find("meta", attrs={"name": "description"})
    page.meta_description = meta.get("content", "") if meta else ""

    # H1
    h1 = soup.find("h1")
    page.h1 = h1.get_text(strip=True) if h1 else ""

    # Headings
    page.headings = _extract_headings(soup)

    # Main content via trafilatura
    extracted = trafilatura.extract(html, include_links=True, include_tables=True)
    page.content = extracted or ""
    page.word_count = len(page.content.split()) if page.content else 0

    # Links
    base_domain = url.split("//")[-1].split("/")[0]
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("javascript"):
            continue
        if base_domain in href or href.startswith("/"):
            page.internal_links.append(href)
        elif href.startswith("http"):
            page.external_links.append(href)

    # FAQs
    page.faqs = _extract_faqs(soup)

    # Tables
    page.tables = _extract_tables(soup)

    return page


def light_scrape(url: str) -> dict:
    """Light scrape for internal URLs – title + meta + H1 only."""
    result = {"url": url, "title": "", "meta_description": "", "h1": "", "error": ""}
    try:
        html = _fetch_html(url)
    except Exception as e:
        result["error"] = str(e)
        return result

    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.find("title")
    result["title"] = title_tag.get_text(strip=True) if title_tag else ""

    meta = soup.find("meta", attrs={"name": "description"})
    result["meta_description"] = meta.get("content", "") if meta else ""

    h1 = soup.find("h1")
    result["h1"] = h1.get_text(strip=True) if h1 else ""

    return result


def format_competitor_data(pages: list[PageData]) -> str:
    """Format scraped competitor data for LLM consumption."""
    sections = []
    for i, p in enumerate(pages, 1):
        if p.error:
            sections.append(f"--- COMPETITOR {i}: {p.url} ---\nError: {p.error}\n")
            continue

        headings_str = "\n".join(
            f"  {h['level']}: {h['text']}" for h in p.headings
        )
        faqs_str = "\n".join(
            f"  Q: {f['question']}\n  A: {f['answer']}" for f in p.faqs
        )
        tables_str = "\n---\n".join(p.tables[:3])

        sections.append(
            f"--- COMPETITOR {i}: {p.url} ---\n"
            f"Title: {p.title}\n"
            f"Meta Description: {p.meta_description}\n"
            f"H1: {p.h1}\n"
            f"Word Count: {p.word_count}\n"
            f"Heading Structure:\n{headings_str}\n"
            f"FAQs Found:\n{faqs_str}\n"
            f"Tables Found:\n{tables_str}\n"
            f"Content Excerpt:\n{p.content[:2000]}\n"
        )
    return "\n\n".join(sections)


def format_internal_data(pages: list[dict]) -> str:
    """Format light-scraped internal URLs for LLM consumption."""
    lines = []
    for p in pages:
        if p.get("error"):
            lines.append(f"- {p['url']} (error: {p['error']})")
        else:
            lines.append(f"- {p['url']} | Title: {p.get('title', '')} | H1: {p.get('h1', '')}")
    return "\n".join(lines)
