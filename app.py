"""SEO Content Engine – Streamlit App (v2)

Multi-stage SEO content pipeline: SERP fetch → scrape → brief → draft → snippets → export.
"""

import streamlit as st
import json

from utils.serp import fetch_serp_results
from utils.internal_urls import get_internal_urls
from utils.scraper import full_scrape, light_scrape, format_competitor_data, format_internal_data
from utils.llm import call_llm, parse_llm_json
from utils.google_docs import export_markdown_fallback
from prompts.content_brief import build_brief_prompt
from prompts.draft_writer import (
    draft_system_prompt,
    draft_user_prompt,
    eeat_user_prompt,
    revision_system_prompt,
    revision_user_prompt,
    EEAT_SYSTEM_PROMPT,
)
from prompts.snippet_optimizer import build_snippet_prompt

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="SEO Content Engine", page_icon="📝", layout="wide")
st.title("📝 SEO Content Engine")

# ---------------------------------------------------------------------------
# Locale presets
# ---------------------------------------------------------------------------
LOCALE_PRESETS = {
    "Australia": {
        "country": "Australia",
        "language_variant": "Australian English",
        "spelling_notes": (
            "Use Australian/British English spelling: colour, customise, organise, centre, metre. "
            "Use metric measurements (cm, metres) as primary with imperial in parentheses where helpful. "
            "Currency: AUD. Reference Australian lifestyle context."
        ),
        "dataforseo_location": "Sydney,New South Wales,Australia",
        "dataforseo_language": "English",
    },
    "United States": {
        "country": "United States",
        "language_variant": "American English",
        "spelling_notes": (
            "Use American English spelling: color, customize, organize, center, meter. "
            "Use imperial measurements as primary with metric in parentheses where helpful. "
            "Currency: USD. Reference American lifestyle context."
        ),
        "dataforseo_location": "United States",
        "dataforseo_language": "English",
    },
    "United Kingdom": {
        "country": "United Kingdom",
        "language_variant": "British English",
        "spelling_notes": (
            "Use British English spelling: colour, customise, organise, centre, metre. "
            "Use metric measurements as primary. Currency: GBP. Reference British lifestyle context."
        ),
        "dataforseo_location": "London,England,United Kingdom",
        "dataforseo_language": "English",
    },
    "Canada": {
        "country": "Canada",
        "language_variant": "Canadian English",
        "spelling_notes": (
            "Use Canadian English spelling: colour, customize, organize, centre, metre. "
            "Use metric measurements as primary. Currency: CAD. Reference Canadian lifestyle context."
        ),
        "dataforseo_location": "Canada",
        "dataforseo_language": "English",
    },
    "New Zealand": {
        "country": "New Zealand",
        "language_variant": "New Zealand English",
        "spelling_notes": (
            "Use New Zealand/British English spelling: colour, customise, organise, centre, metre. "
            "Use metric measurements as primary. Currency: NZD. Reference New Zealand lifestyle context."
        ),
        "dataforseo_location": "Auckland,New Zealand",
        "dataforseo_language": "English",
    },
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🔑 API Keys")
    anthropic_key = st.text_input("Anthropic API Key", type="password", value=st.session_state.get("anthropic_key", ""))
    openai_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.get("openai_key", ""))
    dataforseo_login = st.text_input("DataForSEO Login", value=st.session_state.get("dataforseo_login", ""))
    dataforseo_password = st.text_input("DataForSEO Password", type="password", value=st.session_state.get("dataforseo_password", ""))

    st.session_state["anthropic_key"] = anthropic_key
    st.session_state["openai_key"] = openai_key
    st.session_state["dataforseo_login"] = dataforseo_login
    st.session_state["dataforseo_password"] = dataforseo_password

    st.header("⚙️ LLM Settings")
    provider = st.selectbox("Provider", ["anthropic", "openai"])
    if provider == "anthropic":
        model = st.selectbox("Model", ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-haiku-4-20250514"])
    else:
        model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"])
    st.session_state["llm_provider"] = provider
    st.session_state["llm_model"] = model

    st.header("🌐 Localisation")
    country = st.selectbox("Country", list(LOCALE_PRESETS.keys()), index=0)
    preset = LOCALE_PRESETS[country]

    lang_variant = st.text_input("Language Variant", value=preset["language_variant"])
    dfs_location = st.text_input("DataForSEO Location", value=preset["dataforseo_location"])
    spelling_notes = st.text_area("Spelling Notes", value=preset["spelling_notes"], height=100, disabled=True)

    st.session_state["locale_config"] = {
        "country": country,
        "language_variant": lang_variant,
        "spelling_notes": preset["spelling_notes"],
        "dataforseo_location": dfs_location,
        "dataforseo_language": preset["dataforseo_language"],
    }

    st.header("📤 Google Docs Export")
    share_email = st.text_input("Share with email", value=st.session_state.get("share_email", ""))
    st.session_state["share_email"] = share_email


# ---------------------------------------------------------------------------
# Helper: get LLM config
# ---------------------------------------------------------------------------
def _llm_kwargs() -> dict:
    prov = st.session_state.get("llm_provider", "anthropic")
    key = st.session_state.get("anthropic_key", "") if prov == "anthropic" else st.session_state.get("openai_key", "")
    return {
        "provider": prov,
        "model": st.session_state.get("llm_model", ""),
        "api_key": key,
    }


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "0️⃣ SERP & Setup",
    "1️⃣ Competitor Intel",
    "2️⃣ Content Brief",
    "3️⃣ EEAT Draft",
    "4️⃣ Snippet Optimizer",
    "5️⃣ Export",
])

# ===== TAB 0: SERP & Setup =====
with tab0:
    st.header("SERP & Setup")

    target_keyword = st.text_input("Target Keyword", value=st.session_state.get("target_keyword", ""))
    st.session_state["target_keyword"] = target_keyword

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Fetch SERP Results", disabled=not target_keyword):
            if not dataforseo_login or not dataforseo_password:
                st.error("Please enter DataForSEO credentials in the sidebar.")
            else:
                locale = st.session_state["locale_config"]
                with st.spinner("Fetching SERP results..."):
                    results = fetch_serp_results(
                        keyword=target_keyword,
                        location_name=locale["dataforseo_location"],
                        language_name=locale["dataforseo_language"],
                        api_login=dataforseo_login,
                        api_password=dataforseo_password,
                    )
                if results.get("error"):
                    st.error(f"DataForSEO error: {results['error']}")
                st.session_state["serp_results"] = results.get("organic", [])
                st.session_state["people_also_ask"] = results.get("people_also_ask", [])
                st.rerun()

    # Display SERP results
    serp = st.session_state.get("serp_results", [])
    if serp:
        st.subheader("SERP Results")
        selected = []
        for i, r in enumerate(serp):
            checked = st.checkbox(
                f"#{r['position']} – {r['title']} ({r['domain']})",
                value=True,
                key=f"serp_{i}",
            )
            if checked:
                selected.append(i)
            with st.expander(f"Details: {r['url']}"):
                st.write(r["description"])

        st.session_state["selected_serp_indices"] = selected

    paa = st.session_state.get("people_also_ask", [])
    if paa:
        st.subheader("People Also Ask")
        for q in paa:
            st.write(f"• {q}")

    # Manual competitor URLs
    st.subheader("Add Manual Competitor URLs")
    manual_urls = st.text_area(
        "One URL per line",
        value=st.session_state.get("manual_competitor_urls_text", ""),
        key="manual_competitor_urls_text",
    )

    # Internal URLs
    st.subheader("Internal URLs")
    internal_method = st.radio("Input method", ["Paste", "CSV", "Sitemap"], horizontal=True)

    if internal_method == "Paste":
        internal_text = st.text_area(
            "Paste internal URLs (one per line)",
            value=st.session_state.get("internal_urls_text", ""),
            key="internal_urls_text",
        )
    elif internal_method == "CSV":
        internal_text = st.text_area(
            "Paste CSV (columns: url, title)",
            value=st.session_state.get("internal_urls_csv", ""),
            key="internal_urls_csv",
        )
    else:
        internal_text = st.text_input(
            "Sitemap URL",
            value=st.session_state.get("internal_sitemap_url", ""),
            key="internal_sitemap_url",
        )
        internal_filter = st.text_input("URL filter (optional)", value="", key="sitemap_filter")

    # Brand guidelines
    st.subheader("Brand Guidelines")
    brand_guidelines = st.text_area(
        "Brand voice, tone, style notes (optional)",
        value=st.session_state.get("brand_guidelines", ""),
        key="brand_guidelines",
    )

    # Confirm & Scrape
    if st.button("✅ Confirm & Scrape"):
        # Build competitor URL list
        comp_urls = []
        serp = st.session_state.get("serp_results", [])
        selected_indices = st.session_state.get("selected_serp_indices", [])
        for idx in selected_indices:
            if idx < len(serp):
                comp_urls.append(serp[idx]["url"])

        # Add manual URLs
        for line in manual_urls.strip().splitlines():
            line = line.strip()
            if line and line.startswith("http") and line not in comp_urls:
                comp_urls.append(line)

        # Cap at 5
        comp_urls = comp_urls[:5]
        st.session_state["competitor_urls"] = comp_urls

        # Build internal URL list
        if internal_method == "Paste":
            int_urls = get_internal_urls("paste", text=internal_text)
        elif internal_method == "CSV":
            int_urls = get_internal_urls("csv", text=internal_text)
        else:
            int_urls = get_internal_urls("sitemap", sitemap_url=internal_text, url_filter=internal_filter)

        st.session_state["internal_urls"] = int_urls
        st.success(f"Ready to scrape {len(comp_urls)} competitors and {len(int_urls)} internal URLs.")

# ===== TAB 1: Competitor Intel =====
with tab1:
    st.header("Competitor Intelligence")

    comp_urls = st.session_state.get("competitor_urls", [])
    int_urls = st.session_state.get("internal_urls", [])

    if not comp_urls:
        st.info("Go to Tab 0 to set up and confirm URLs first.")
    else:
        if st.button("🔄 Scrape Competitors"):
            # Full scrape competitors
            progress = st.progress(0)
            scraped = []
            total = len(comp_urls) + len(int_urls)

            for i, url in enumerate(comp_urls):
                with st.spinner(f"Scraping {url}..."):
                    page = full_scrape(url)
                    scraped.append(page)
                progress.progress((i + 1) / total)

            st.session_state["scraped_pages"] = scraped
            st.session_state["scraped_formatted"] = format_competitor_data(scraped)

            # Light scrape internal URLs
            internal_scraped = []
            for j, u in enumerate(int_urls):
                with st.spinner(f"Light scraping {u['url']}..."):
                    result = light_scrape(u["url"])
                    internal_scraped.append(result)
                progress.progress((len(comp_urls) + j + 1) / total)

            st.session_state["internal_scraped"] = internal_scraped
            st.session_state["internal_formatted"] = format_internal_data(internal_scraped)
            progress.progress(1.0)
            st.success("Scraping complete!")
            st.rerun()

    # Display scraped data
    scraped_pages = st.session_state.get("scraped_pages", [])
    if scraped_pages:
        st.subheader("Competitor Data")
        for page in scraped_pages:
            with st.expander(f"{'❌' if page.error else '✅'} {page.url}"):
                if page.error:
                    st.error(page.error)
                else:
                    st.write(f"**Title:** {page.title}")
                    st.write(f"**H1:** {page.h1}")
                    st.write(f"**Meta:** {page.meta_description}")
                    st.write(f"**Word Count:** {page.word_count}")
                    st.write("**Headings:**")
                    for h in page.headings:
                        st.write(f"  {h['level']}: {h['text']}")
                    if page.faqs:
                        st.write("**FAQs Found:**")
                        for faq in page.faqs:
                            st.write(f"  Q: {faq['question']}")
                    if page.tables:
                        st.write(f"**Tables:** {len(page.tables)} found")

    internal_scraped = st.session_state.get("internal_scraped", [])
    if internal_scraped:
        st.subheader("Internal URLs")
        for p in internal_scraped:
            icon = "❌" if p.get("error") else "✅"
            st.write(f"{icon} {p['url']} – {p.get('title', 'N/A')}")

    if scraped_pages:
        if st.button("📋 Generate Content Brief"):
            locale = st.session_state["locale_config"]
            sys_prompt, user_prompt = build_brief_prompt(
                keyword=st.session_state.get("target_keyword", ""),
                locale_config=locale,
                competitor_data=st.session_state.get("scraped_formatted", ""),
                internal_data=st.session_state.get("internal_formatted", ""),
                people_also_ask=st.session_state.get("people_also_ask", []),
            )

            with st.spinner("Generating content brief..."):
                raw = call_llm(
                    system_prompt=sys_prompt,
                    user_prompt=user_prompt,
                    response_format="json",
                    max_tokens=8192,
                    **_llm_kwargs(),
                )

            brief_json = parse_llm_json(raw)
            if brief_json:
                st.session_state["raw_brief_json"] = brief_json
                st.success("Brief generated! Go to Tab 2 to review.")
            else:
                st.warning("Failed to parse brief as JSON. Showing raw output for manual editing.")
                st.session_state["raw_brief_json"] = None
                st.session_state["raw_brief_text"] = raw

# ===== TAB 2: Content Brief (Review Gate) =====
with tab2:
    st.header("Content Brief Review")

    brief = st.session_state.get("raw_brief_json")

    if not brief and st.session_state.get("raw_brief_text"):
        st.warning("Brief couldn't be parsed as JSON. Edit the raw text below.")
        edited = st.text_area("Raw Brief", value=st.session_state["raw_brief_text"], height=600)
        if st.button("Try Parse Again"):
            parsed = parse_llm_json(edited)
            if parsed:
                st.session_state["raw_brief_json"] = parsed
                st.success("Parsed successfully!")
                st.rerun()
            else:
                st.error("Still invalid JSON.")

    elif not brief:
        st.info("Generate a content brief in Tab 1 first.")
    else:
        # ---- METADATA SECTION ----
        st.subheader("📊 Metadata")
        meta = brief.get("metadata", {})

        content_types = ["Blog", "Landing Page", "Product Page", "Guide", "How-To", "Listicle", "Comparison", "Other"]
        current_type = meta.get("content_type", "Blog")
        type_idx = content_types.index(current_type) if current_type in content_types else len(content_types) - 1
        meta_content_type = st.selectbox("Content Type", content_types, index=type_idx, key="meta_content_type")

        meta_url = st.text_input("URL", value=meta.get("url", ""), key="meta_url")

        meta_title = st.text_input("Meta Title", value=meta.get("meta_title", ""), key="meta_title")
        st.caption(f"Characters: {len(meta_title)}/60")

        meta_desc = st.text_area("Meta Description", value=meta.get("meta_description", ""), height=68, key="meta_desc")
        st.caption(f"Characters: {len(meta_desc)}/155")

        meta_word_count = st.text_input("Expected Word Count", value=meta.get("expected_word_count", ""), key="meta_wc")
        meta_intent = st.text_input("Search Intent", value=meta.get("search_intent", ""), key="meta_intent")
        meta_format = st.text_input("Page Format", value=meta.get("page_format", ""), key="meta_format")
        meta_audience = st.text_area("Target Audience", value=meta.get("target_audience", ""), height=80, key="meta_audience")

        # Primary keywords
        st.markdown("**Primary Keywords** (one per line: keyword | volume | notes)")
        pk_default = "\n".join(
            f"{kw.get('keyword', '')} | {kw.get('search_volume', '')} | {kw.get('notes', '')}"
            for kw in meta.get("primary_keywords", [])
        )
        meta_pk = st.text_area("Primary Keywords", value=pk_default, height=100, key="meta_pk")

        # Secondary keywords
        st.markdown("**Secondary Keywords** (one per line)")
        sk_default = "\n".join(
            kw.get("keyword", "") + (f" | {kw.get('notes', '')}" if kw.get("notes") else "")
            for kw in meta.get("secondary_keywords", [])
        )
        meta_sk = st.text_area("Secondary Keywords", value=sk_default, height=120, key="meta_sk")

        # Internal links
        st.markdown("**Internal Links**")
        il_list = meta.get("internal_links", [])
        if "brief_internal_links" not in st.session_state:
            st.session_state["brief_internal_links"] = il_list.copy() if il_list else []

        links = st.session_state["brief_internal_links"]
        links_to_remove = []
        for li, link in enumerate(links):
            cols = st.columns([3, 2, 3, 1])
            with cols[0]:
                links[li]["url"] = st.text_input("URL", value=link.get("url", ""), key=f"il_url_{li}")
            with cols[1]:
                links[li]["anchor_text"] = st.text_input("Anchor", value=link.get("anchor_text", ""), key=f"il_anchor_{li}")
            with cols[2]:
                links[li]["placement_note"] = st.text_input("Placement", value=link.get("placement_note", ""), key=f"il_place_{li}")
            with cols[3]:
                if st.button("🗑️", key=f"il_rm_{li}"):
                    links_to_remove.append(li)

        for idx in sorted(links_to_remove, reverse=True):
            links.pop(idx)
        if links_to_remove:
            st.rerun()

        if st.button("➕ Add Internal Link"):
            links.append({"url": "", "anchor_text": "", "placement_note": ""})
            st.rerun()

        # ---- CONTENT OUTLINE SECTION ----
        st.subheader("📝 Content Outline")
        outline = brief.get("content_outline", [])
        if "brief_outline" not in st.session_state:
            st.session_state["brief_outline"] = [h.copy() for h in outline]

        ol = st.session_state["brief_outline"]
        outline_changed = False

        for hi, heading in enumerate(ol):
            st.markdown(f"---")
            cols = st.columns([1, 4, 1])
            with cols[0]:
                levels = ["H1", "H2", "H3", "H4"]
                lvl_idx = levels.index(heading.get("level", "H2")) if heading.get("level", "H2") in levels else 1
                ol[hi]["level"] = st.selectbox("Level", levels, index=lvl_idx, key=f"ol_lvl_{hi}")
            with cols[1]:
                ol[hi]["text"] = st.text_input("Heading", value=heading.get("text", ""), key=f"ol_txt_{hi}")
            with cols[2]:
                st.write("")  # spacer
                btn_cols = st.columns(3)
                with btn_cols[0]:
                    if hi > 0 and st.button("⬆️", key=f"ol_up_{hi}"):
                        ol[hi], ol[hi - 1] = ol[hi - 1], ol[hi]
                        outline_changed = True
                with btn_cols[1]:
                    if hi < len(ol) - 1 and st.button("⬇️", key=f"ol_dn_{hi}"):
                        ol[hi], ol[hi + 1] = ol[hi + 1], ol[hi]
                        outline_changed = True
                with btn_cols[2]:
                    if st.button("🗑️", key=f"ol_rm_{hi}"):
                        ol.pop(hi)
                        outline_changed = True

            if not outline_changed:
                ol[hi]["instructions"] = st.text_area(
                    "Writing Instructions",
                    value=heading.get("instructions", ""),
                    height=100,
                    key=f"ol_inst_{hi}",
                )

                if st.button(f"➕ Add Heading Below", key=f"ol_add_{hi}"):
                    ol.insert(hi + 1, {"level": "H2", "text": "", "instructions": ""})
                    outline_changed = True

        if outline_changed:
            st.rerun()

        if st.button("➕ Add New Heading"):
            ol.append({"level": "H2", "text": "", "instructions": ""})
            st.rerun()

        # ---- FAQ SECTION ----
        st.subheader("❓ FAQs")
        faqs = brief.get("faqs", [])
        if "brief_faqs" not in st.session_state:
            st.session_state["brief_faqs"] = [f.copy() for f in faqs]

        faq_list = st.session_state["brief_faqs"]
        faq_changed = False
        for fi, faq in enumerate(faq_list):
            cols = st.columns([5, 1])
            with cols[0]:
                faq_list[fi]["question"] = st.text_input("Question", value=faq.get("question", ""), key=f"faq_q_{fi}")
                faq_list[fi]["answer_direction"] = st.text_area(
                    "Answer Direction", value=faq.get("answer_direction", ""), height=80, key=f"faq_a_{fi}"
                )
            with cols[1]:
                st.write("")
                if st.button("🗑️", key=f"faq_rm_{fi}"):
                    faq_list.pop(fi)
                    faq_changed = True

        if faq_changed:
            st.rerun()

        if st.button("➕ Add FAQ"):
            faq_list.append({"question": "", "answer_direction": ""})
            st.rerun()

        # ---- CHART/TABLE IDEAS ----
        st.subheader("📊 Chart & Table Ideas")
        chart_default = "\n\n".join(
            f"{c.get('type', '')}: {c.get('description', '')}"
            for c in brief.get("chart_table_ideas", [])
        )
        chart_ideas = st.text_area("Chart/Table Ideas", value=chart_default, height=150, key="chart_ideas")

        # ---- EEAT IDEAS ----
        st.subheader("🏆 EEAT Ideas")
        eeat_default = "\n".join(f"• {e}" for e in brief.get("eeat_ideas", []))
        eeat_ideas = st.text_area("EEAT Ideas", value=eeat_default, height=120, key="eeat_ideas")

        # ---- ADDITIONAL NOTES ----
        st.subheader("📌 Additional Notes")
        add_notes = st.text_area("Notes", value=brief.get("additional_notes", ""), height=100, key="add_notes")

        # ---- APPROVE BUTTON ----
        st.markdown("---")
        if st.button("✅ Approve Brief & Generate Draft", type="primary"):
            # Reassemble brief
            # Parse primary keywords
            pk_parsed = []
            for line in meta_pk.strip().splitlines():
                parts = [p.strip() for p in line.split("|")]
                kw = {"keyword": parts[0]} if parts else {"keyword": ""}
                if len(parts) > 1:
                    kw["search_volume"] = parts[1]
                if len(parts) > 2:
                    kw["notes"] = parts[2]
                pk_parsed.append(kw)

            # Parse secondary keywords
            sk_parsed = []
            for line in meta_sk.strip().splitlines():
                parts = [p.strip() for p in line.split("|")]
                kw = {"keyword": parts[0]} if parts else {"keyword": ""}
                if len(parts) > 1:
                    kw["notes"] = parts[1]
                sk_parsed.append(kw)

            approved_json = {
                "metadata": {
                    "content_type": meta_content_type,
                    "url": meta_url,
                    "meta_title": meta_title,
                    "meta_description": meta_desc,
                    "expected_word_count": meta_word_count,
                    "search_intent": meta_intent,
                    "page_format": meta_format,
                    "target_audience": meta_audience,
                    "primary_keywords": pk_parsed,
                    "secondary_keywords": sk_parsed,
                    "internal_links": st.session_state["brief_internal_links"],
                },
                "content_outline": st.session_state["brief_outline"],
                "faqs": st.session_state["brief_faqs"],
                "chart_table_ideas": chart_ideas,
                "eeat_ideas": eeat_ideas,
                "additional_notes": add_notes,
            }
            st.session_state["approved_brief_json"] = approved_json

            # Build markdown brief for draft writer
            md = _brief_json_to_markdown(approved_json)
            st.session_state["approved_brief"] = md
            st.success("Brief approved! Go to Tab 3 to generate the draft.")


def _brief_json_to_markdown(brief: dict) -> str:
    """Convert approved brief JSON to a formatted markdown string for the draft writer."""
    lines = ["# Content Brief\n"]

    meta = brief.get("metadata", {})
    lines.append("## Metadata")
    for key, val in meta.items():
        if key in ("primary_keywords", "secondary_keywords", "internal_links"):
            continue
        lines.append(f"- **{key.replace('_', ' ').title()}**: {val}")

    lines.append("\n### Primary Keywords")
    for kw in meta.get("primary_keywords", []):
        lines.append(f"- {kw.get('keyword', '')} (vol: {kw.get('search_volume', 'N/A')})")

    lines.append("\n### Secondary Keywords")
    for kw in meta.get("secondary_keywords", []):
        lines.append(f"- {kw.get('keyword', '')}")

    lines.append("\n### Internal Links")
    for link in meta.get("internal_links", []):
        lines.append(f"- [{link.get('anchor_text', '')}]({link.get('url', '')}) — {link.get('placement_note', '')}")

    lines.append("\n## Content Outline")
    for h in brief.get("content_outline", []):
        prefix = "#" * (int(h.get("level", "H2")[1]) if h.get("level", "H2")[1:].isdigit() else 2)
        lines.append(f"\n{prefix} {h.get('text', '')}")
        lines.append(f"*Instructions: {h.get('instructions', '')}*")

    faqs = brief.get("faqs", [])
    if faqs:
        lines.append("\n## FAQs")
        for faq in faqs:
            lines.append(f"\n**Q: {faq.get('question', '')}**")
            lines.append(f"Answer direction: {faq.get('answer_direction', '')}")

    chart = brief.get("chart_table_ideas", "")
    if chart:
        lines.append(f"\n## Chart & Table Ideas\n{chart}")

    eeat = brief.get("eeat_ideas", "")
    if eeat:
        lines.append(f"\n## EEAT Ideas\n{eeat}")

    notes = brief.get("additional_notes", "")
    if notes:
        lines.append(f"\n## Additional Notes\n{notes}")

    return "\n".join(lines)


# ===== TAB 3: EEAT Draft =====
with tab3:
    st.header("EEAT-Aware Draft Generation")

    approved = st.session_state.get("approved_brief")
    if not approved:
        st.info("Approve a content brief in Tab 2 first.")
    else:
        if st.button("🚀 Generate Draft (3-Pass Pipeline)"):
            locale = st.session_state["locale_config"]
            llm = _llm_kwargs()

            # Pass 1: First draft
            st.subheader("Pass 1: Writing First Draft")
            with st.spinner("Writing first draft..."):
                first_draft = call_llm(
                    system_prompt=draft_system_prompt(locale),
                    user_prompt=draft_user_prompt(approved),
                    max_tokens=8192,
                    **llm,
                )
            st.session_state["first_draft"] = first_draft
            st.success("First draft complete!")

            # Pass 2: EEAT analysis
            st.subheader("Pass 2: EEAT Analysis")
            with st.spinner("Analysing EEAT signals..."):
                eeat = call_llm(
                    system_prompt=EEAT_SYSTEM_PROMPT,
                    user_prompt=eeat_user_prompt(
                        first_draft,
                        st.session_state.get("scraped_formatted", "No competitor data available."),
                    ),
                    max_tokens=4096,
                    **llm,
                )
            st.session_state["eeat_analysis"] = eeat
            st.success("EEAT analysis complete!")

            # Pass 3: Revision
            st.subheader("Pass 3: Final Revision")
            with st.spinner("Revising draft with EEAT improvements..."):
                final = call_llm(
                    system_prompt=revision_system_prompt(locale),
                    user_prompt=revision_user_prompt(first_draft, eeat),
                    max_tokens=8192,
                    **llm,
                )
            st.session_state["final_draft"] = final
            st.success("Final draft complete!")
            st.rerun()

        # Display results in sub-tabs
        if st.session_state.get("first_draft"):
            dtab1, dtab2, dtab3 = st.tabs(["First Draft", "EEAT Analysis", "Final Draft"])

            with dtab1:
                st.markdown(st.session_state.get("first_draft", ""))

            with dtab2:
                st.markdown(st.session_state.get("eeat_analysis", ""))

            with dtab3:
                st.markdown(st.session_state.get("final_draft", ""))

# ===== TAB 4: Snippet Optimizer =====
with tab4:
    st.header("Featured Snippet Optimizer")

    snippet_keyword = st.text_input(
        "Target Keyword",
        value=st.session_state.get("target_keyword", ""),
        key="snippet_keyword",
    )

    # Parse secondary keywords from approved brief
    sec_kws = []
    approved_json = st.session_state.get("approved_brief_json", {})
    if approved_json:
        for kw in approved_json.get("metadata", {}).get("secondary_keywords", []):
            if kw.get("keyword"):
                sec_kws.append(kw["keyword"])

    sec_kw_text = st.text_area(
        "Secondary Keywords (one per line)",
        value="\n".join(sec_kws),
        height=100,
        key="snippet_sec_kws",
    )

    if st.button("⚡ Generate Snippet Targets"):
        locale = st.session_state["locale_config"]
        content = st.session_state.get("final_draft", st.session_state.get("first_draft", ""))

        sec_list = [k.strip() for k in sec_kw_text.strip().splitlines() if k.strip()]

        sys_p, user_p = build_snippet_prompt(
            target_keyword=snippet_keyword,
            secondary_keywords=sec_list,
            content_excerpt=content,
            locale_config=locale,
        )

        with st.spinner("Generating snippet targets..."):
            result = call_llm(
                system_prompt=sys_p,
                user_prompt=user_p,
                max_tokens=4096,
                **_llm_kwargs(),
            )
        st.session_state["snippet_results"] = result
        st.rerun()

    if st.session_state.get("snippet_results"):
        st.markdown(st.session_state["snippet_results"])

# ===== TAB 5: Export =====
with tab5:
    st.header("Export")

    sections = {}
    if st.session_state.get("approved_brief"):
        sections["Content Brief"] = st.session_state["approved_brief"]
    if st.session_state.get("final_draft"):
        sections["Final Draft"] = st.session_state["final_draft"]
    elif st.session_state.get("first_draft"):
        sections["Draft"] = st.session_state["first_draft"]
    if st.session_state.get("eeat_analysis"):
        sections["EEAT Analysis"] = st.session_state["eeat_analysis"]
    if st.session_state.get("snippet_results"):
        sections["Snippet Targets"] = st.session_state["snippet_results"]

    if not sections:
        st.info("Nothing to export yet. Complete the pipeline first.")
    else:
        selected_sections = st.multiselect("Sections to export", list(sections.keys()), default=list(sections.keys()))

        export_sections = {k: v for k, v in sections.items() if k in selected_sections}

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 Google Docs Export")
            st.info(
                "Google Docs export requires OAuth credentials. "
                "Set up a Google Cloud project with Docs API enabled and provide credentials."
            )
            if st.button("Export to Google Docs"):
                st.warning("Google Docs OAuth flow not yet configured. Use Markdown export below.")

        with col2:
            st.subheader("📋 Markdown Export")
            md = export_markdown_fallback(export_sections)
            st.download_button(
                label="⬇️ Download Markdown",
                data=md,
                file_name=f"seo-content-{st.session_state.get('target_keyword', 'export').replace(' ', '-')}.md",
                mime="text/markdown",
            )

        # Preview
        st.subheader("Preview")
        for title in selected_sections:
            with st.expander(title):
                st.markdown(sections[title])
