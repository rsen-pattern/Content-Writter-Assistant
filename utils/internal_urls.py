"""Internal URL input handler – paste / CSV / sitemap → list[dict]."""

from __future__ import annotations
import csv
import io
from utils.sitemap import parse_sitemap


def parse_pasted_urls(text: str) -> list[dict]:
    """Parse newline-separated URLs."""
    urls = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line and line.startswith("http"):
            urls.append({"url": line, "title": None})
    return urls


def parse_csv_urls(csv_text: str) -> list[dict]:
    """Parse CSV with columns: url (required), title (optional)."""
    urls = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        url = row.get("url", "").strip()
        if url:
            urls.append({"url": url, "title": row.get("title", "").strip() or None})
    return urls


def parse_sitemap_urls(sitemap_url: str, url_filter: str = "", max_urls: int = 200) -> list[dict]:
    """Fetch sitemap and return URL dicts."""
    raw = parse_sitemap(sitemap_url, url_filter, max_urls)
    return [{"url": u, "title": None} for u in raw]


def get_internal_urls(method: str, **kwargs) -> list[dict]:
    """Unified entry point.

    Args:
        method: One of "paste", "csv", "sitemap".
        text: Raw text for paste/csv methods.
        sitemap_url: URL for sitemap method.
        url_filter: Optional filter for sitemap.
        max_urls: Cap for sitemap.
    """
    if method == "paste":
        return parse_pasted_urls(kwargs.get("text", ""))
    elif method == "csv":
        return parse_csv_urls(kwargs.get("text", ""))
    elif method == "sitemap":
        return parse_sitemap_urls(
            kwargs.get("sitemap_url", ""),
            kwargs.get("url_filter", ""),
            kwargs.get("max_urls", 200),
        )
    return []
