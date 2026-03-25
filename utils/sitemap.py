"""Sitemap parser – handles sitemap indexes and regular sitemaps."""

import requests
from lxml import etree

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def fetch_sitemap(url: str, timeout: int = 15) -> str:
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "SEOContentBot/1.0"})
    resp.raise_for_status()
    return resp.text


def parse_sitemap(
    sitemap_url: str,
    url_filter: str = "",
    max_urls: int = 500,
) -> list[str]:
    """Parse a sitemap (or sitemap index) and return a list of URLs.

    Args:
        sitemap_url: URL of the sitemap XML.
        url_filter: Optional substring filter – only URLs containing this string are kept.
        max_urls: Cap on total URLs returned.
    """
    try:
        xml_text = fetch_sitemap(sitemap_url)
    except Exception:
        return []

    root = etree.fromstring(xml_text.encode())
    tag = etree.QName(root.tag).localname

    urls: list[str] = []

    if tag == "sitemapindex":
        sitemap_locs = root.findall(".//sm:sitemap/sm:loc", SITEMAP_NS)
        for loc in sitemap_locs:
            if loc.text:
                urls.extend(parse_sitemap(loc.text.strip(), url_filter, max_urls - len(urls)))
                if len(urls) >= max_urls:
                    break
    else:
        url_locs = root.findall(".//sm:url/sm:loc", SITEMAP_NS)
        for loc in url_locs:
            if loc.text:
                u = loc.text.strip()
                if not url_filter or url_filter in u:
                    urls.append(u)
                    if len(urls) >= max_urls:
                        break

    return urls[:max_urls]
