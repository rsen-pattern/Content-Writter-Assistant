# SEO Content Engine

Multi-stage SEO content pipeline built with Streamlit. Generates high-quality, EEAT-optimised content from SERP analysis through to export-ready drafts.

## Pipeline

| Stage | Description |
|-------|-------------|
| **SERP & Setup** | Fetch top-ranking results via DataForSEO, add competitor and internal URLs |
| **Competitor Intel** | Full and light scraping of competitor pages for content analysis |
| **Content Brief** | LLM-generated brief with keyword strategy, structure, and recommendations |
| **EEAT Draft** | 3-pass drafting pipeline (initial draft, EEAT enhancement, revision) with human review gate |
| **Snippet Optimizer** | Meta title, description, and featured snippet optimisation |
| **Export** | Google Docs export with sharing, or markdown fallback |

## LLM Providers

Three provider options are available:

| Provider | Models | Notes |
|----------|--------|-------|
| **Anthropic** | Claude Sonnet 4, Opus 4, Haiku 4 | Direct Anthropic API |
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-4 Turbo | Direct OpenAI API |
| **Bifrost** | GPT-4o, Claude Sonnet 4, DeepSeek, Mistral, Llama 3.1, and more | Pattern's LLM proxy at `bifrost.pattern.com` — routes to 10+ providers through a single API key |

## Locale Support

5 built-in locale presets with spelling rules, measurement systems, and currency:

- Australia (AU English)
- United States (US English)
- United Kingdom (British English)
- Canada (Canadian English)
- New Zealand (NZ English)

## Page Type Guides

9 dynamic page type guides with tailored SEO writing directives:

- Category / Collection
- Product Detail (PDP)
- Blog / Article
- Homepage
- Landing Page
- FAQ / Help Centre
- About / Brand Story
- Comparison / Buying Guide
- Location / Store Page

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure secrets

Copy the example and fill in your keys:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Required keys:

| Key | Description |
|-----|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key (if using Anthropic provider) |
| `OPENAI_API_KEY` | OpenAI API key (if using OpenAI provider) |
| `BIFROST_API_KEY` | Bifrost virtual key `sk-bf-...` (if using Bifrost provider) |
| `DATAFORSEO_LOGIN` | DataForSEO account login |
| `DATAFORSEO_PASSWORD` | DataForSEO account password |
| `GOOGLE_DOCS_SHARE_EMAIL` | Email to share exported Google Docs with |

### 3. Run locally

```bash
streamlit run app.py
```

### Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect the repo, set `app.py` as the main file
4. Add your secrets in **App Settings > Secrets** using the format from `secrets.toml.example`

## Project Structure

```
app.py                          # Main Streamlit app (6 tabs, sidebar config)
requirements.txt                # Python dependencies
.streamlit/
  config.toml                   # Streamlit theme and settings
  secrets.toml.example          # API key template
utils/
  llm.py                        # Unified LLM interface (Anthropic, OpenAI, Bifrost)
  serp.py                       # DataForSEO SERP client
  scraper.py                    # Competitor page scraping
  sitemap.py                    # XML sitemap parser
  internal_urls.py              # Internal URL input handler
  google_docs.py                # Google Docs export + markdown fallback
prompts/
  seo_directive.py              # Universal SEO directive + 9 page type guides
  content_brief.py              # Brief generation prompts
  draft_writer.py               # 3-pass draft pipeline prompts
  snippet_optimizer.py          # Snippet optimizer prompts
```
