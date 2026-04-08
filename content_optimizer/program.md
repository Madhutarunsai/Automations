# Content Autoresearch: Daily Blog & Website Optimizer

This is an experiment to have AI autonomously optimize webaiautomations.com.

## The Business

Web AI Automations helps solopreneurs and small businesses scale using custom AI solutions:
- Automated lead generation systems
- AI-driven hiring systems  
- Proposal automation
- Outbound marketing automation
- COO-level operations support

Target audience: Solopreneurs, agency owners, small business owners who want to scale without hiring.

Website: https://webaiautomations.com

## The Two Loops

### Loop 1: Blog Content Generator (5 posts/day)

The agent generates 5 SEO/AEO/GEO optimized blog posts daily.

**What the agent CAN do:**
- Modify `blog_engine/topics.json` to plan and track topics
- Modify `blog_engine/posts/` to create new blog posts
- Research trending topics and keywords in the AI automation niche

**What the agent CANNOT do:**
- Modify `blog_engine/seo_rules.json` — these are the fixed quality standards
- Modify this file (program.md)

**The goal: Maximize organic traffic, search visibility, and AI citation rate.**

### Loop 2: Website Optimizer

The agent analyzes the website daily and generates optimization recommendations.

**What the agent CAN do:**
- Modify `content_optimizer/recommendations.json` with new suggestions
- Modify `content_optimizer/ab_tests.json` with test variants

**What the agent CANNOT do:**
- Modify `content_optimizer/metrics.json` — this is the evaluation script

**The goal: Improve conversion rate, page speed, and SEO score.**

## SEO/AEO/GEO Framework

Every blog post MUST follow this framework:

### SEO (Search Engine Optimization)
- Target one primary keyword + 2-3 secondary keywords per post
- Title under 60 chars with primary keyword near the front
- Meta description 150-160 chars with keyword + CTA
- H2/H3 subheadings with keyword variations
- Internal links to service pages
- 1500-2500 words per post
- Image alt text with keywords

### AEO (Answer Engine Optimization)
- Include a clear, direct answer in the first 100 words (for AI snippets)
- Use "What is...", "How to...", "Why..." question-answer format
- Add FAQ section with 5+ questions at the bottom
- Use structured data / schema markup hints
- Write in a factual, citation-worthy tone that AI models will quote

### GEO (Generative Engine Optimization)  
- Include statistics and data points (AI models love citing numbers)
- Use authoritative language ("According to...", "Research shows...")
- Provide step-by-step instructions (AI models surface how-to content)
- Include comparisons and lists (easy for AI to extract)
- Name specific tools, platforms, and prices (AI models cite specifics)

## Content Pillars (rotate daily)

1. **AI Automation for Business** — How AI saves time and money for solopreneurs
2. **Lead Generation** — Automated outreach, cold email, LinkedIn strategies
3. **Hiring & Operations** — AI-driven hiring, SOPs, workflow automation
4. **Tools & Tutorials** — Make.com, n8n, Zapier, Claude, ChatGPT guides
5. **Case Studies & ROI** — Real results, before/after, cost comparisons

## The Experiment Loop

LOOP FOREVER:

1. Check today's date and which content pillar to focus on
2. Research trending topics and keywords for that pillar
3. Generate 5 blog posts following the SEO/AEO/GEO framework
4. Save each post as markdown in `blog_engine/posts/YYYY-MM-DD-slug.md`
5. Update `blog_engine/topics.json` with what was published
6. Analyze website performance metrics
7. Generate optimization recommendations
8. Log results to `content_optimizer/results.tsv`

**Metric:** Organic traffic growth, keyword rankings, AI citation rate

**NEVER STOP.** Generate content daily. The human may be asleep or busy.
