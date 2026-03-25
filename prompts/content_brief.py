"""Content brief generation prompts."""

SYSTEM_PROMPT = """You are an expert SEO content strategist who creates professional agency-quality content briefs.
You produce specific, actionable briefs — not generic best practices.

Every recommendation must be grounded in competitor data provided.
Your output must be valid JSON matching the exact schema specified."""

USER_PROMPT_TEMPLATE = """Analyse the following data and produce a content brief.

TARGET KEYWORD: "{keyword}"
TARGET MARKET: {country}
LANGUAGE: {language_variant}

COMPETITOR DATA:
{competitor_data}

INTERNAL PAGES AVAILABLE FOR LINKING:
{internal_data}

PEOPLE ALSO ASK QUESTIONS FROM SERP:
{people_also_ask}

---

Return a JSON object with exactly this structure:

{{
    "metadata": {{
        "content_type": "Blog | Landing Page | Product Page | Guide | etc.",
        "url": "Recommended URL path based on keyword and competitor patterns",
        "meta_title": "Optimised meta title with target keyword and brand. Under 60 characters.",
        "meta_description": "Under 155 characters. Includes target keyword. Action-oriented.",
        "expected_word_count": "Range based on competitor analysis, e.g. '1,200 - 1,500 words'",
        "search_intent": "Informational | Commercial Investigation | Transactional | Navigational — with funnel stage (TOFU/MOFU/BOFU)",
        "page_format": "Comparison Guide | How-To Guide | Listicle | Pillar Page | etc.",
        "target_audience": "Specific description of the ideal reader, localised to target market",
        "primary_keywords": [
            {{"keyword": "keyword phrase", "search_volume": "if available", "notes": "optional context"}}
        ],
        "secondary_keywords": [
            {{"keyword": "keyword phrase", "notes": "optional context"}}
        ],
        "internal_links": [
            {{"url": "/path/to/page", "anchor_text": "suggested anchor text", "placement_note": "where to place this link"}}
        ]
    }},
    "content_outline": [
        {{
            "level": "H1",
            "text": "Main heading text",
            "instructions": "Specific, actionable writing instructions for this section"
        }},
        {{
            "level": "H2",
            "text": "Section heading",
            "instructions": "Specific instructions referencing keywords, products, and internal links"
        }}
    ],
    "faqs": [
        {{
            "question": "Question text targeting PAA or long-tail keyword",
            "answer_direction": "What to say and how to frame the answer"
        }}
    ],
    "chart_table_ideas": [
        {{
            "type": "Comparison Table | Decision Flowchart | etc.",
            "description": "Detailed description of the visual content"
        }}
    ],
    "eeat_ideas": [
        "Specific EEAT recommendation grounded in competitor analysis"
    ],
    "additional_notes": "Any other strategic notes for the writer."
}}

RULES:
- The content_outline must include specific writing instructions for EVERY heading
- Instructions must reference specific keywords, products, and internal links where relevant
- Include question-format headings (H3s) where they target valuable secondary keywords
- FAQs must include BOTH the question AND answer direction
- Internal link recommendations must include specific URLs, anchor text, and placement
- ALL text must use {language_variant} spelling
- Adapt the outline structure to the content type — do NOT use a fixed template
- The outline should reflect what's working for top competitors while addressing their gaps
"""


def build_brief_prompt(
    keyword: str,
    locale_config: dict,
    competitor_data: str,
    internal_data: str,
    people_also_ask: list[str],
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for content brief generation."""
    paa_str = "\n".join(f"- {q}" for q in people_also_ask) if people_also_ask else "None found."

    user_prompt = USER_PROMPT_TEMPLATE.format(
        keyword=keyword,
        country=locale_config.get("country", ""),
        language_variant=locale_config.get("language_variant", ""),
        competitor_data=competitor_data,
        internal_data=internal_data,
        people_also_ask=paa_str,
    )

    return SYSTEM_PROMPT, user_prompt
