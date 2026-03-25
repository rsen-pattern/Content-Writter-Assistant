"""SEO Content Writing Directive (universal) and Page Type Guides (dynamic).

The SEO_WRITING_DIRECTIVE is always injected into system prompts for brief
generation and draft writing.

PAGE_TYPE_GUIDES are dynamically selected based on the brief's page_format
field and injected only during draft-writing stages.
"""

# ---------------------------------------------------------------------------
# Section 1: Universal SEO Writing Directive
# ---------------------------------------------------------------------------

SEO_WRITING_DIRECTIVE = """
## SEO CONTENT WRITING DIRECTIVE — UNIVERSAL BEST PRACTICES

Follow these rules for every piece of content you generate. These are non-negotiable quality standards.

### 1. Write for Humans First, Search Engines Second
The content must be genuinely useful, engaging, and readable. Optimisation is a secondary layer applied on top of quality writing — never the primary driver. If a keyword insertion makes a sentence awkward, cut the keyword. Great content earns rankings; keyword-stuffed content loses readers.

### 2. Strategic Keyword Placement
Place keywords with intent, not density. The target keyword (and natural variations) should appear in:

- The H1 heading (exactly once)
- The first 100 words of the introduction
- 2-3 H2 or H3 subheadings (where it reads naturally)
- The final paragraph or conclusion
- The meta title and meta description
- The URL slug

Secondary keywords should be distributed naturally across sections. Question-format keywords should become H3 headings or FAQ entries where they match the content flow. Never force a keyword into a sentence where it disrupts readability.

Semantic keyphrases (related terms and concepts) should appear throughout to demonstrate topical depth. These signal to search engines that the content is comprehensive.

### 3. Answer the Reader's Questions Directly
Structure content around the questions readers actually have. Use "People Also Ask" data and competitor FAQ patterns to identify these questions. When a heading is phrased as a question, answer it directly in the opening sentence of that section before expanding with detail.

Good: "### How tall should a TV unit be? A TV unit should position the centre of your screen at seated eye level — roughly 100-110cm from the floor for most sofas. Here's how to calculate the ideal height for your setup..."

Bad: "### How tall should a TV unit be? There are many factors to consider when choosing furniture for your living room. Height is one of several important dimensions..."

### 4. Content Structure and Readability
- Use a single H1 for the page title
- Break content into clear sections with H2 headings for major topics and H3 headings for supporting points
- Keep paragraphs short — 2-4 sentences maximum. Dense blocks of text lose readers.
- Use bullet points and numbered lists when presenting multiple items, steps, or comparisons — but don't overuse them
- Bold key phrases to highlight important points for scanning readers (sparingly — if everything is bold, nothing is)
- Use transition sentences between sections to maintain flow
- Front-load key information in each section. Don't bury the answer after three paragraphs of preamble.

### 5. Internal Linking
Internal links are a critical SEO and UX signal. They distribute page authority, guide users through the site, and signal topical relationships to search engines.

- Use descriptive anchor text that tells the reader what they will find (e.g., "browse our modular sofa range" not "click here")
- Place internal links where they add genuine value to the reader — mid-sentence within relevant context
- Each major section should contain at least one internal link if a relevant page exists
- Link to product/category pages, related blog posts, and service pages as appropriate
- Never force a link. If it doesn't fit naturally in the section, skip it.

### 6. Meta Title and Description
Meta title:
- Under 60 characters
- Include the primary keyword as early as possible
- Add the brand name at the end, separated by a pipe: "Primary Keyword Phrase | Brand Name"
- Make it compelling — this is the first thing searchers see

Meta description:
- 150-160 characters
- Include the primary keyword in the first sentence
- Use an action verb (discover, learn, find out, explore, read)
- Clearly state what the reader will get from the page
- Never duplicate meta descriptions across pages

### 7. URL Structure
- Short, clean, lowercase
- Include the primary keyword
- Use hyphens between words, never underscores
- Remove stop words (the, a, and, of, etc.) unless they are part of the keyword
- Never include dates or numbers that will need updating
- Example: /modular-vs-sectional-sofas (not /blog/2024/01/modular-sofa-vs-sectional-sofa-guide-australia)

### 8. Image and Visual Content
- Every image must have descriptive alt text that includes the keyword where natural
- Use descriptive filenames: tv-unit-size-chart.jpg not IMG_4827.jpg
- Compress images before upload to maintain page speed
- Include relevant visuals: comparison tables, size charts, decision flowcharts, product photos, infographics
- Visual content breaks up text, aids comprehension, and can earn backlinks from other sites
- Specify custom images/charts in the brief where they would add genuine value — don't add images for the sake of it

### 9. EEAT Signals (Experience, Expertise, Authoritativeness, Trustworthiness)
Every piece of content should demonstrate:

- **Experience**: First-hand knowledge, real examples, case studies, process descriptions. "We tested this" or "In our showroom" beats generic advice.
- **Expertise**: Technical accuracy, specialised knowledge, professional credentials. Quote internal experts by name and role.
- **Authoritativeness**: Citation of reputable sources, industry data, recognised frameworks. Link out to authoritative references.
- **Trustworthiness**: Accurate claims, proper attribution, publication dates, author bios, transparent recommendations.

For YMYL (Your Money, Your Life) topics, EEAT signals are especially critical. Never fabricate statistics, quotes, or credentials — use [PLACEHOLDER] markers for anything that needs human verification.

### 10. Calls to Action
- Every piece of content should have a clear CTA aligned with the page goal and funnel stage
- TOFU (awareness) content: CTA to read related content, download a guide, subscribe
- MOFU (consideration) content: CTA to compare options, view product ranges, book a consultation
- BOFU (decision) content: CTA to buy, book, request a quote, contact
- Place the primary CTA in the conclusion, with secondary CTAs woven naturally into relevant sections
- Make CTAs specific: "Browse our entertainment unit range" beats "Learn more"

### 11. Avoid AI Writing Tells
The content must not read like it was generated by AI. Specific patterns to avoid:

- Definition lists (bold term followed by colon and explanation) — these are the most common AI writing pattern
- Starting every section with "When it comes to..."
- Overusing transitional phrases like "Furthermore," "Moreover," "Additionally"
- Repeating the same sentence structure across paragraphs
- Generic filler ("In today's fast-paced world..." / "It's important to note that...")
- Summarising what you're about to say before saying it
- Excessive hedging ("It's worth considering that perhaps...")

Write with varied sentence lengths. Mix short punchy statements with longer explanatory sentences. Use contractions where the tone allows. Be direct.

### 12. Content Freshness and Accuracy
- Include specific, verifiable data points where relevant (with sources or [PLACEHOLDER] markers)
- Avoid date-specific references that will age poorly unless the content is explicitly time-bound
- Use current terminology and conventions for the target market
- Reference products, tools, and resources that are currently available
- Flag any claims that need fact-checking with [PLACEHOLDER: Source needed]
"""

# ---------------------------------------------------------------------------
# Section 2: Page Type Guides
# ---------------------------------------------------------------------------

COMPARISON_GUIDE = """
## PAGE TYPE BEST PRACTICES: COMPARISON GUIDE

You are writing a comparison article. This format directly addresses commercial investigation intent — readers are actively deciding between options.

### Structure Pattern

1. **Hook + frame the debate**: Validate the reader's confusion. Acknowledge that the difference isn't obvious. State clearly what this guide will resolve.

2. **Define Option A**: Dedicated section explaining what it is, key characteristics, and who it's best for. Include product recommendations and internal links. Don't sell — inform.

3. **Define Option B**: Same treatment. Give both options fair, balanced coverage before the comparison.

4. **Head-to-head comparison**: Break down the comparison across 3-6 specific dimensions (e.g., flexibility, durability, price, space requirements). Use H3 subheadings for each dimension. Present both sides fairly in each subsection.

5. **Comparison table**: Include a scannable summary table. Columns: Feature | Option A | Option B. Keep descriptions punchy (5-10 words per cell). This is a high-value visual element for featured snippets.

6. **Verdict / decision guide**: "Choose A if..." and "Choose B if..." bulleted lists. Be decisive — readers want guidance, not fence-sitting. Then soften with "The good news is..." to highlight overlap products.

7. **FAQ section**: Address the specific questions people have when comparing these options.

### Key Rules for Comparison Content

- **Be balanced but decisive.** Cover both options fairly in the body, then give a clear recommendation in the verdict. Readers came here to make a decision — help them.
- **Use question-format H3s** for specific comparison dimensions: "Which is better for small spaces?" "Which is more durable?" These target long-tail queries.
- **Include a comparison table.** This is non-negotiable for comparison content. Tables have high featured snippet potential and serve scanning readers.
- **Recommend specific products** for each option where relevant. Link to product/category pages.
- **Avoid generic pros/cons.** Be specific: "Modular pieces fit through narrow apartment hallways" is better than "Easy to move."
- **Address the hybrid/overlap.** Many comparisons have a middle ground. Acknowledge products that bridge both categories.
"""

HOW_TO_GUIDE = """
## PAGE TYPE BEST PRACTICES: HOW-TO GUIDE

You are writing a how-to guide. This format addresses informational intent — readers want to accomplish something specific or understand how something works.

### Structure Pattern

1. **Hook + promise**: State what the reader will be able to do after reading. Validate that the task seems complicated but this guide makes it simple.

2. **Quick answer / summary**: Give the short answer immediately (within the first 150 words). This targets featured snippets and respects impatient readers. Then expand.

3. **Prerequisites / what you'll need** (if applicable): List tools, measurements, or information the reader should gather before starting.

4. **Step-by-step sections**: Each major step gets its own H2. Sub-steps get H3s. Number the steps if sequential order matters. Each step should be actionable — start with a verb.

5. **Visual aids**: Size charts, measurement diagrams, formula examples, reference tables. How-to content almost always benefits from visual elements that condense information.

6. **Common mistakes / things to avoid**: Dedicated section addressing what NOT to do. Frame as helpful warnings, not fear-mongering.

7. **FAQ section**: Answer the specific "but what about..." questions readers have.

8. **CTA**: Guide readers to the next action — shop the relevant product range, book a consultation, use a calculator tool.

### Key Rules for How-To Content

- **Lead with the answer, then explain.** Don't make readers wade through backstory to find the practical information. The explanation supports the answer, not the other way around.
- **Use specific numbers and measurements.** "Allow 5-10cm of clearance on each side" is better than "Leave enough space." How-to readers want precision.
- **Include reference tables and charts.** Tables mapping inputs to outputs (e.g., TV size → recommended unit width) are extremely high-value. They target featured snippets and serve as the page's "reason to bookmark."
- **Address multiple scenarios.** A how-to guide for TV unit sizing should cover 55", 65", 75", and 85" TVs separately. Each scenario is a keyword targeting opportunity (H3: "What size TV unit for a 65-inch TV?").
- **Use question-format H3s** for each scenario or sub-question. These directly target "People Also Ask" and long-tail queries.
- **Include a "rules of thumb" or "golden rules" section.** Readers love memorable heuristics they can apply without re-reading the whole guide.
- **Recommend products** at each relevant step. "For a 65-inch TV, look for units 160-180cm wide — like the [Product Name]."
"""

LISTICLE_GUIDE = """
## PAGE TYPE BEST PRACTICES: LISTICLE / LIST POST

You are writing a listicle. This format works for both informational and commercial investigation intent — readers want a curated, scannable set of options or ideas.

### Structure Pattern

1. **Hook + what to expect**: State the number of items and why this list matters. Set selection criteria — how were these chosen?

2. **List items**: Each item gets its own H2 (for major lists) or H3 (for sub-lists). Include: what it is, why it's on the list, who it's best for, and a link to more detail.

3. **Comparison element** (optional): Brief comparison table or "best for" summary near the top for scanning readers.

4. **How we chose these** (for credibility): Brief explanation of selection methodology.

5. **FAQ section**: "What about X?" questions that didn't make the main list.

### Key Rules for Listicles

- **Front-load value.** Put the strongest, most useful items first. Don't save the best for last — many readers won't get there.
- **Be specific about each item.** "Great for small spaces" is generic. "Fits rooms under 3m × 4m with its compact 140cm frame" is useful.
- **Include a "quick pick" summary** at the top or in a table: Item | Best For | Price Range. Scanning readers will thank you.
- **Odd numbers perform better in titles** (7, 9, 11) but don't pad the list to hit a number. Quality over quantity.
- **Each item should link somewhere** — product page, detailed review, category page.
"""

PILLAR_PAGE_GUIDE = """
## PAGE TYPE BEST PRACTICES: PILLAR PAGE / COMPREHENSIVE GUIDE

You are writing a pillar page — a comprehensive, authoritative guide on a broad topic. This is the centrepiece of a topic cluster strategy.

### Structure Pattern

1. **Executive summary**: What this guide covers and who it's for. Include a table of contents with anchor links.

2. **Foundational sections**: Define key terms, establish context. This is where beginners start.

3. **Deep-dive sections**: Each major subtopic gets its own H2 with H3 sub-sections. These are thorough but should link out to dedicated "spoke" articles for exhaustive detail.

4. **Practical application sections**: How-to elements, case studies, examples.

5. **Advanced considerations**: Expert-level insights for readers who already know the basics.

6. **FAQ section**: Comprehensive — 6-10 questions covering the full range from beginner to advanced.

7. **Next steps / CTA**: Where to go from here based on the reader's situation.

### Key Rules for Pillar Pages

- **This page should be the single best resource on the topic.** If a reader could only read one page, this should give them everything they need.
- **Link extensively to related content** (both internal and external). A pillar page is a hub — it should connect readers to deeper resources on every subtopic.
- **Use a table of contents** with anchor links. Long-form content needs navigation.
- **Target the broadest keyword** in the topic cluster for the H1 and meta title.
- **Include multiple content formats**: text, tables, charts, embedded calculators, examples.
- **Word count is typically 2,500-5,000+** depending on topic complexity. Don't pad — but do be thorough.
- **Update regularly.** Pillar pages are living documents. Flag sections that will need refreshing.
"""

PRODUCT_ROUNDUP_GUIDE = """
## PAGE TYPE BEST PRACTICES: PRODUCT ROUNDUP / REVIEW

You are writing product-focused content. This format serves commercial investigation and transactional intent.

### Structure Pattern

1. **Hook + selection criteria**: What problem do these products solve? How were they selected?

2. **Quick comparison table**: Product | Key Feature | Best For | Price Range. Appears before the detailed reviews.

3. **Individual product sections**: Each product gets its own H2 or H3 with: overview, key features, who it's best for, any limitations, and a link to the product page.

4. **How to choose**: Buying guide section explaining what factors to consider.

5. **FAQ section**: Common purchasing questions.

6. **CTA**: Direct links to shop or enquire.

### Key Rules for Product Content

- **Be specific about features.** Dimensions, materials, weight capacity, available finishes — readers making purchase decisions need specifics.
- **Include real-world context.** "The 200cm width accommodates TVs up to 75 inches" is more useful than "extra wide."
- **Link every product mention** to its product page. Multiple times if it appears in multiple sections.
- **Be honest about limitations.** Acknowledging trade-offs builds trust: "At 45cm depth, the feet of some wider-stance TVs may overhang slightly."
- **Use "best for" framing** to help readers self-select: "Best for open-plan living rooms" / "Best for apartment-sized spaces."
"""

FAQ_PAGE_GUIDE = """
## PAGE TYPE BEST PRACTICES: FAQ PAGE

You are writing a dedicated FAQ page or a content piece structured primarily as Q&A.

### Structure Pattern

1. **Brief introduction**: What topic these FAQs cover and who they're for.

2. **Q&A pairs**: Each question is an H2 or H3. Answer immediately and directly in the first sentence, then expand with detail.

3. **Group by theme**: If there are 8+ questions, group them under thematic H2 headings.

4. **CTA**: Direct readers to relevant product/service pages or "still have questions? Contact us."

### Key Rules for FAQ Content

- **Answer in the first sentence.** The question is the heading; the answer starts immediately. No preamble, no "Great question!" — just the answer.
- **Keep answers concise but complete.** 50-150 words per answer. If an answer needs more, it should probably be its own article (link to it instead).
- **Use the exact question phrasing people search for.** Check "People Also Ask" data. Match the natural language.
- **Don't start answers with "Yes" or "No".** Start with a standalone statement: "A TV unit should always be wider than the TV it supports" not "Yes, your TV unit should be wider."
- **Implement FAQ schema markup** on the page for rich result eligibility.
- **Each answer should contain at least one internal link** where relevant.
"""

LANDING_PAGE_GUIDE = """
## PAGE TYPE BEST PRACTICES: LANDING PAGE

You are writing a service or product landing page. This format serves transactional intent — readers are close to a decision.

### Structure Pattern

1. **Hero section**: Clear value proposition in the H1. What do you offer, who is it for, what's the key benefit?

2. **Social proof**: Trust signals early — reviews, client logos, awards, guarantees.

3. **Features/benefits**: What the reader gets. Focus on outcomes, not features.

4. **How it works**: Simple 3-5 step process if applicable.

5. **Detailed information**: Supporting sections with specifics, FAQs, case studies.

6. **CTA (repeated)**: Primary CTA appears at least twice — after the hero and at the end. Use specific action language.

### Key Rules for Landing Pages

- **One page, one goal.** Every element should support a single conversion action.
- **Lead with benefits, support with features.** "Sleep better tonight" then "Memory foam, 25cm depth, 10-year warranty."
- **Minimise exit paths.** Internal links should be strategic, not exploratory. Don't send readers away from the conversion path.
- **Use specific, action-oriented CTAs**: "Shop entertainment units" not "Learn more."
- **Include trust signals**: guarantees, reviews, credentials, delivery information.
"""

CASE_STUDY_GUIDE = """
## PAGE TYPE BEST PRACTICES: CASE STUDY

You are writing a case study. This format builds trust through real-world proof.

### Structure Pattern

1. **The challenge**: What problem did the client/customer face?
2. **The approach**: What solution was implemented?
3. **The results**: Specific, measurable outcomes.
4. **Key takeaways**: What can the reader learn from this?
5. **CTA**: "Want similar results? Let's talk."

### Key Rules for Case Studies

- **Lead with results.** Put the headline metric in the introduction or even the H1: "How [Client] increased organic traffic by 340% in 6 months."
- **Be specific.** Numbers, timelines, before/after comparisons.
- **Include direct quotes** from the client (or [PLACEHOLDER] markers for them).
- **Make it scannable.** Use callout boxes for key metrics, before/after comparisons, and pull quotes.
"""

BLOG_POST_GUIDE = """
## PAGE TYPE BEST PRACTICES: BLOG POST

You are writing a blog post. This is a versatile format that can address informational, educational, or thought leadership goals.

### Structure Pattern

1. **Hook**: Open with a relatable problem, surprising fact, or direct statement of what the reader will learn.

2. **Body sections**: Each H2 covers a major point. H3s provide supporting detail. Logical flow from problem → understanding → solution → action.

3. **Practical elements**: Include at least one actionable takeaway, example, or framework the reader can apply.

4. **Conclusion + CTA**: Summarise the key takeaway (one sentence) and direct the reader to a next step.

### Key Rules for Blog Posts

- **Have a clear angle.** A blog post should have a specific point of view or argument — not just "everything about X."
- **Make it scannable.** Subheadings should tell the story even if the reader only reads the headings.
- **Include at least one visual element**: table, chart, image, embedded content.
- **Link to related blog posts and relevant product/service pages.**
- **End with a specific CTA** tied to the content topic, not a generic "contact us."
"""

NEWS_GUIDE = """
## PAGE TYPE BEST PRACTICES: NEWS / ANNOUNCEMENT

You are writing a news article or announcement. This format prioritises timeliness and factual clarity.

### Structure Pattern

1. **Lead**: The most important information in the first paragraph — who, what, when, where, why.
2. **Supporting detail**: Expand on the lead with quotes, data, and context.
3. **Background**: Broader context for readers unfamiliar with the topic.
4. **Next steps / implications**: What happens next, what it means for the reader.

### Key Rules for News Content

- **Inverted pyramid structure.** Most important information first. Each paragraph adds decreasing levels of detail.
- **Be factual and precise.** Dates, names, figures — get them right or use [PLACEHOLDER].
- **Include quotes** from relevant stakeholders.
- **Keep it concise.** News is not the format for exhaustive coverage.
"""

# ---------------------------------------------------------------------------
# Page type guide lookup
# ---------------------------------------------------------------------------

PAGE_TYPE_GUIDES: dict[str, str] = {
    "comparison": COMPARISON_GUIDE,
    "how-to": HOW_TO_GUIDE,
    "how to": HOW_TO_GUIDE,
    "listicle": LISTICLE_GUIDE,
    "list": LISTICLE_GUIDE,
    "pillar": PILLAR_PAGE_GUIDE,
    "comprehensive": PILLAR_PAGE_GUIDE,
    "product": PRODUCT_ROUNDUP_GUIDE,
    "roundup": PRODUCT_ROUNDUP_GUIDE,
    "review": PRODUCT_ROUNDUP_GUIDE,
    "faq": FAQ_PAGE_GUIDE,
    "landing": LANDING_PAGE_GUIDE,
    "case study": CASE_STUDY_GUIDE,
    "news": NEWS_GUIDE,
    "blog": BLOG_POST_GUIDE,
    "generic": BLOG_POST_GUIDE,
}


def get_page_type_guide(page_format: str) -> str:
    """Match a page_format string to the closest page type guide.

    Uses simple keyword matching — e.g., if "comparison" is in the format,
    return the comparison guide. Falls back to generic guide if no match.
    """
    format_lower = page_format.lower()
    for key, guide in PAGE_TYPE_GUIDES.items():
        if key in format_lower:
            return guide
    return PAGE_TYPE_GUIDES.get("generic", "")
