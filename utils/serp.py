"""DataForSEO SERP client – fetches top organic results + People Also Ask."""

import requests

FILTERED_DOMAINS = {
    "youtube.com", "reddit.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "linkedin.com", "pinterest.com", "tiktok.com",
    "amazon.com", "ebay.com", "quora.com",
}

API_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"


def _is_filtered(domain: str) -> bool:
    domain = domain.lower().strip()
    for fd in FILTERED_DOMAINS:
        if domain == fd or domain.endswith("." + fd):
            return True
    return False


def fetch_serp_results(
    keyword: str,
    location_name: str,
    language_name: str,
    device: str = "desktop",
    api_login: str = "",
    api_password: str = "",
) -> dict:
    """Return {"organic": [...], "people_also_ask": [...]}."""
    payload = [
        {
            "keyword": keyword,
            "location_name": location_name,
            "language_name": language_name,
            "device": device,
            "os": "windows",
            "depth": 10,
        }
    ]

    try:
        resp = requests.post(
            API_URL,
            json=payload,
            auth=(api_login, api_password),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        return {"error": str(exc), "organic": [], "people_also_ask": []}

    organic = []
    people_also_ask = []

    tasks = data.get("tasks", [])
    if not tasks:
        return {"error": "No tasks returned", "organic": [], "people_also_ask": []}

    result = tasks[0].get("result")
    if not result:
        return {"error": "No result in task", "organic": [], "people_also_ask": []}

    items = result[0].get("items", []) if result else []

    for item in items:
        item_type = item.get("type", "")

        if item_type == "organic":
            domain = item.get("domain", "")
            if _is_filtered(domain):
                continue
            organic.append(
                {
                    "position": item.get("rank_absolute", 0),
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "domain": domain,
                }
            )

        elif item_type == "people_also_ask":
            paa_items = item.get("items", [])
            if isinstance(paa_items, list):
                for paa in paa_items:
                    q = paa.get("title", "") or paa.get("question", "")
                    if q:
                        people_also_ask.append(q)

    return {"organic": organic[:10], "people_also_ask": people_also_ask}
