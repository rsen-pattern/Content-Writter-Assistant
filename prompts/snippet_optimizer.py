"""Featured snippet optimizer prompts."""

from prompts.seo_directive import SEO_WRITING_DIRECTIVE


def snippet_system_prompt(locale_config: dict) -> str:
    lang = locale_config.get("language_variant", "Australian English")
    spelling = locale_config.get("spelling_notes", "")
    return f"""You are a featured snippet optimization specialist.
Your job is to craft concise, direct answer targets that Google can pull into featured snippets.

LOCALISATION: Write answer targets in {lang}. {spelling}

Each answer target must:
- Be 200-320 characters (including spaces)
- Directly answer the query in the first sentence
- Be factual and authoritative
- Use natural language (not keyword-stuffed)
- Be self-contained (makes sense without surrounding context)

{SEO_WRITING_DIRECTIVE}"""


SNIPPET_USER_PROMPT_TEMPLATE = """Generate featured snippet answer targets for the following keywords.

TARGET KEYWORD: {target_keyword}

SECONDARY KEYWORDS:
{secondary_keywords}

CURRENT CONTENT EXCERPT (for context):
{content_excerpt}

For each keyword, provide:
1. The keyword
2. Snippet type (paragraph / list / table)
3. Answer target (200-320 characters)
4. Suggested placement in the article

Return the results in a clear, structured format."""


def build_snippet_prompt(
    target_keyword: str,
    secondary_keywords: list[str],
    content_excerpt: str,
    locale_config: dict,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for snippet optimization."""
    sec_kw = "\n".join(f"- {kw}" for kw in secondary_keywords) if secondary_keywords else "None provided."

    user_prompt = SNIPPET_USER_PROMPT_TEMPLATE.format(
        target_keyword=target_keyword,
        secondary_keywords=sec_kw,
        content_excerpt=content_excerpt[:3000],
    )

    return snippet_system_prompt(locale_config), user_prompt
