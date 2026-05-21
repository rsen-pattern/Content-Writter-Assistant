"""SEMrush keyword research – target metrics + related keywords.

SEMrush legacy API returns semicolon-separated values, one header line then data lines.
Docs: https://www.semrush.com/api-documentation/
"""

from __future__ import annotations
import requests


SEMRUSH_BASE_URL = "https://api.semrush.com/"
DEFAULT_DATABASE = "us"
TARGET_COLUMNS = "Ph,Nq,Cp,Co,Nr,Td"
RELATED_COLUMNS = "Ph,Nq,Cp,Co,Nr,Td,Rr"

# Map SEMrush column codes to friendly names
_COLUMN_MAP = {
    "Ph": "keyword",
    "Nq": "volume",
    "Cp": "cpc",
    "Co": "competition",
    "Nr": "results",
    "Td": "trend",
    "Rr": "relatedness",
    "Kd": "difficulty",
}


def _semrush_request(params: dict) -> list[dict]:
    """Call SEMrush and parse the CSV-like response into a list of dicts."""
    resp = requests.get(SEMRUSH_BASE_URL, params=params, timeout=20)
    resp.raise_for_status()
    text = resp.text.strip()

    # SEMrush returns "ERROR ##" on failure
    if text.startswith("ERROR"):
        raise RuntimeError(f"SEMrush API: {text}")
    if not text:
        return []

    lines = text.splitlines()
    headers = [_COLUMN_MAP.get(h, h.lower()) for h in lines[0].split(";")]
    rows = []
    for line in lines[1:]:
        values = line.split(";")
        if len(values) != len(headers):
            continue
        rows.append(dict(zip(headers, values)))
    return rows


def _cast(row: dict) -> dict:
    """Cast numeric fields in a SEMrush row to int/float."""
    cast_int = ("volume", "results")
    cast_float = ("cpc", "competition", "relatedness", "difficulty")
    out = dict(row)
    for k in cast_int:
        if k in out:
            try:
                out[k] = int(out[k])
            except (ValueError, TypeError):
                out[k] = 0
    for k in cast_float:
        if k in out:
            try:
                out[k] = float(out[k])
            except (ValueError, TypeError):
                out[k] = 0.0
    return out


def fetch_keyword_data(
    keyword: str,
    api_key: str,
    database: str = DEFAULT_DATABASE,
    related_limit: int = 25,
) -> dict:
    """Fetch volume, CPC, competition for the target keyword plus related keywords.

    Returns:
        {
            "target": {"keyword": ..., "volume": int, "cpc": float, "competition": float,
                       "results": int, "trend": str} or None,
            "related": [{"keyword": ..., "volume": int, ...}, ...]
        }
    """
    if not api_key:
        raise ValueError("Missing SEMrush API key.")
    if not keyword:
        raise ValueError("Missing keyword.")

    target_rows = _semrush_request({
        "type": "phrase_this",
        "key": api_key,
        "phrase": keyword,
        "database": database,
        "export_columns": TARGET_COLUMNS,
    })
    target = _cast(target_rows[0]) if target_rows else None

    related_rows = _semrush_request({
        "type": "phrase_related",
        "key": api_key,
        "phrase": keyword,
        "database": database,
        "export_columns": RELATED_COLUMNS,
        "display_limit": related_limit,
    })
    related = [_cast(r) for r in related_rows]

    return {"target": target, "related": related}


def format_keyword_data_for_llm(data: dict) -> str:
    """Render keyword data as a short markdown block to inject into LLM prompts."""
    if not data:
        return ""
    lines = ["## Keyword Research (SEMrush)"]
    t = data.get("target")
    if t:
        lines.append(
            f"- Target: **{t.get('keyword', '')}** | Volume: {t.get('volume', 0):,} "
            f"| CPC: ${t.get('cpc', 0.0):.2f} | Competition: {t.get('competition', 0.0):.2f}"
        )
    related = data.get("related", [])
    if related:
        lines.append(f"\n### Related Keywords (top {len(related)})")
        for r in related:
            lines.append(
                f"- {r.get('keyword', '')} | Vol: {r.get('volume', 0):,} "
                f"| CPC: ${r.get('cpc', 0.0):.2f}"
            )
    return "\n".join(lines)
