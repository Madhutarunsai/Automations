# LinkedIn Growth + Revenue Playbook (6 Months)

**Owner:** Madhu Tarun Sai · AI Automation Specialist
**Profile:** https://www.linkedin.com/in/madhu-tarun-sai/
**Site:** https://webaiautomations.com
**Window:** May 2026 → Oct 2026
**Honest target:** 30K followers · 4K newsletter subs · $20K MRR · 10 calls/wk
**Stretch (15% probability):** 100K followers — only if 1 podcast hits + 1 viral post + paid collabs land

> This document replaces an earlier plan that overpromised 100K followers as the base case. The math didn't survive scrutiny: 99K net followers in 26 weeks requires average post impressions of ~150K (top-0.5% creator territory). Realistic ceiling without paid amp or a viral break is 15–30K. This version optimizes for revenue first, audience as a side effect, with a real pivot trigger at Month 3.

---

## 1. The Five Decisions You Make in Week 0

These block everything. None are optional.

1. **One thesis, one sentence.** Not 5 pillars. One contrarian claim every post reinforces. Candidates:
   - *"Replace one role per quarter with Claude + n8n."*
   - *"Solopreneurs should fire the VA before they hire the employee."*
   - *"AI agents are 90% prompt, 10% code."*
   Pick one. Pin it above your monitor.
2. **One ICP.** Drop "freelancer / Upwork beginner." Target **agency owners and founders at $10K–$200K MRR running manual ops**. They have budget; beginners don't. Re-aim every existing lead magnet at this audience over weeks 2–4.
3. **One win condition: $20K MRR by M6.** Followers are a side effect. 10K of the right people beats 100K strangers.
4. **Apply for LinkedIn verification + Top Voice in Week 1.** Verification is free and instant. Top Voice = 20 expert answers in collaborative articles over 30 days. Both are 360Brew trust signals.
5. **Write the M3 pivot trigger and pin it.**
   *"On July 31, if I am below 12K followers OR newsletter < 1.2K OR MRR < $3K, I drop the audience goal and run revenue-only for M4–M6."*

---

## 2. Reality Check — What the Math Actually Says

Goal: 1,000 → 100,000 = **3,800 net followers/week** for 26 weeks.

| Source | Realistic ceiling | Followers added (6mo) |
|--------|------------------|----------------------|
| Connection accepts (1st-degree auto-follow) | 100/wk × 45% accept | ~1,200 |
| Direct follows from feed (~0.5% of impressions) | needs **750K impressions/wk** to hit goal | likely <10K |
| Profile-view → follow (~10% of profile views) | needs ~38K profile views/wk | likely <5K |
| Newsletter back-flow | trivial vs goal | <500 |
| Viral comments on big posts | 14–55 viral comments × 50–200 followers | ~1K–8K |

**Honest M6 ceilings:**
- All-organic, no flagship, no paid: **12–18K**
- + paid creator collabs + LinkedIn ads: **22–32K**
- + 1 podcast hit OR 1 viral post (>500K impressions): **35–55K**
- + all of the above + 1 outlier post (>1M impressions): **60–100K** (~15% probability)

Plan for 30K. Architect for upside.

---

## 3. The 360Brew Algorithm (what we optimize for)

LinkedIn's 2026 ranker is an LLM that reads the *meaning* of your posts and comments, builds an interest graph, and routes content within that graph.

What it weights:
- **Dwell time** is the #1 signal. 61+ s dwell → 15.6% engagement; <3 s → 1.2%.
- **First 60–90 minutes** decide reach. Comments in this window are weighted 15× a like.
- **Conversation depth.** Threads with back-and-forth get 5.2× amplification vs. monologues.
- **Topic authority.** Post and comment on the same niche for 6 months → algorithm tags you as the authority and routes that audience to you.
- **5+ skills** = 27× more discoverable.

Tactical implication for every post: (a) carousel, long-text, or video — never a bare image, (b) end on a question that invites a >3-sentence reply, (c) get 5+ comments from your network in the first 30 min.

What's now penalized: engagement pods (97% detection), generic "Great post!" comments, repeat-format accounts, AI-detected em-dash dumps.

---

## 4. The Four Parallel Tracks

All four run from Week 1. Skipping any kills the plan.

### Track A — Revenue (funds everything else)

The biggest mistake of the previous plan was waiting until Month 5 to monetize. Ship in Week 2.

- **Week 1:** Productize one offer.
  - **AI Automation Starter Kit — $497**: 5 n8n templates (already in `lead_magnets/templates/`) + 1 hour of setup support. Stripe Payment Link, no website.
  - OR **Solopreneur AI Audit — $1,997**: 90-min audit + custom playbook + 30 days Slack support.
- **Week 2:** Launch with one LinkedIn post + DM to your warmest 50 connections. **Goal: 5 sales by Friday = $2,500.**
- **Week 4:** Add a $4,997 done-with-you tier as the audit-call upsell.
- **Ongoing:** Every Friday post is a case study with a *direct* CTA to the offer. Not soft. "If you want me to build this for you: [link]."

This track pays for tools, the VA, and ads. Without it, Track D is impossible.

### Track B — Content (Mon–Fri)

**4 posts/week, not 5.** Quality > volume. Thursday is comment-only.

| Day | Format | Purpose | Source |
|-----|--------|---------|--------|
| Mon | Carousel (8–10 slides) | Framework / how-to | Reformat from `blog_engine/posts/` |
| Tue | Text post (story) | Thesis reinforcement | Pull from `MASTER_CONTENT_SHEET.csv` |
| Wed | Native video (60–90 s) | Face + voice → trust | Wednesday hiring/ops pillar |
| Thu | **No post** — comment-only day | Distribution | — |
| Fri | Multi-image case study | Proof → revenue CTA | Real client work |

Sat: 1 long story post (optional). Sun: off.

Every post must:
1. Reinforce the one thesis.
2. End with a question OR a keyword-trigger CTA from `lead_magnets/lead_magnets_sheet.csv`.
3. Be drafted the day before, never at 8 AM.
4. Stay under 1,400 chars; hook in first 200 chars before the "see more" cutoff.

Format performance to plan around (2026 benchmarks): Carousels ~24% engagement · Multi-image 6.6% · Video 5.6% · Polls 4.4% · Text 4%.

**Use what you have.** 60 scripts in `MASTER_CONTENT_SHEET.csv` = 12 weeks of LinkedIn content. Reformat — don't rewrite. One blog post = 1 carousel + 1 text post + 1 newsletter section + 4 planted comments. The blog engine is the idea factory; LinkedIn is distribution.

### Track C — Distribution (the part founders skip)

**Distribution > Content. Always.** A mediocre post with 30 thoughtful first-hour comments beats a great post nobody sees. If you have 90 min today, spend 30 on the post and 60 on commenting + DMs.

- **15 thoughtful comments/day. 3-Sentence Rule:** Acknowledge a specific point, expand with your own data/story, ask a follow-up question. 10 min before your post goes live (lifts your reach ~20%), 10 min after.
- **30-creator target list** in `content_scripts/COMMENT_TARGETS.md`: 10 Tier-A (100K+, your ICP audience) · 10 Tier-B (20K–100K peers) · 10 Tier-C (1K–20K reciprocal). Bell-icon notifications on for Tier A — comment in the first 10 min.
- **10 connection invites/day, warm only** in M1–M2. Target people who liked or commented on your last 3 posts. Acceptance rate matters more than volume — drop below 30% and LinkedIn jails you.
- **No pitch in the connect note.** Under 200 chars: *"Hey {{firstName}} — saw your post about {{topic}}. Same world here. No pitch, just enjoying your content."*
- **DM your warmest 100 1st-degree connections in Week 1** — not pitching, asking what content they want more of. This is research that doubles as a re-activation signal.

### Track D — Leverage (breaks the organic ceiling)

Organic alone caps at 15–20K. These break the ceiling:

- **Pitch 30 podcasts in Weeks 2–4** (lead time is 6–10 weeks; M1 pitches = M3 episodes). Tracker: name, host, sent date, response, episode date. Use `lead_magnets/cv_tarun.html` as the pitch attachment.
- **Paid creator collabs starting M2.** Pay 2 mid-tier creators (20K–80K, adjacent niches) $500–$2K each to co-author a post or share your flagship asset. Single fastest 3K–8K-follower lever. Budget: $1K/mo from M2.
- **LinkedIn Thought Leader Ads from M3.** Boost your top 2 organic posts/month. Budget: $500–$1,500/mo. Targets: by job title, by company list, by competitor's followers. CPM is high (~$30) but follower-CAC is $2–$5 vs. $20+ for cold ads.
- **Flagship asset launched in M3.** Build *one* shareable artifact:
  - "State of Solopreneur AI 2026" report with original survey data (n≥200), OR
  - Open-source `claude-md-pack` repo on GitHub with 50+ stars target, OR
  - Free public dashboard / calculator (e.g. "What does manual ops cost your agency?").
  This is your viral lottery ticket. Without one, viral never happens — only random hot takes.
- **VA from Week 4.** $400–$800/mo on Onlinejobs.ph or GenZRevolution. They handle: inbox, magnet DMs, comment responses on old posts, scheduling. Frees ~10 h/week.

---

## 5. Profile Foundation (Week 1, 90 minutes)

- **Headline (220 chars):** thesis + ICP + proof + CTA. Example based on a Claude+n8n thesis:
  *"I help agency owners replace 1 role per quarter with Claude + n8n · 50+ automations shipped · Free 15-min audit ↓"*
- **Banner:** thesis line + DM-keyword trigger. *"Comment AUTOMATION for the n8n template pack."*
- **About:** 2,000-char arc — Pain → Realization → Method → Proof → CTA. Open with the thesis sentence.
- **Featured (6 tiles):** starter guide PDF, n8n templates, CLAUDE.md mega pack, named case study, free audit Calendly, newsletter.
- **Creator Mode ON.** Five hashtags: `#AIAutomation #AgencyOps #n8n #LeadGeneration #ClaudeCode`.
- **Skills (50 max, top 5 pinned):** AI Automation, n8n, Claude, Lead Generation, Workflow Automation. Get ≥3 endorsements per top-5 skill from past clients.
- **Verification:** apply Day 1.
- **Activity broadcast:** OFF during the rebuild day.

---

## 6. The Newsletter (start Week 2 — your moat)

Newsletter notifications are the *only* LinkedIn surface that bypasses the feed algorithm. A 4K newsletter = 4K guaranteed inbox visits/week — survives any feed change.

- **Title:** *The Solopreneur Automation Brief* (or whatever fits your thesis)
- **Cadence:** weekly, Friday 9 AM EST. Skip any week you can't ship — never miss to post junk.
- **Length:** 1,000–1,500 words. Three sections: 1 framework, 1 tool/tactic, 1 case study.
- **Subscribe surfaces:** every post CTA, profile featured, dedicated launch + every 1K-sub milestone post.
- **CTA:** every issue ends with one offer (the $497 kit OR the $1,997 audit). 2% of subs convert = 80 calls/yr from a 4K list.

---

## 7. Connection + DM Funnel

### Hard limits (LinkedIn 2026)
- Standard: 100 invites/wk · Sales Nav / high SSI: 200–250/wk · New / low-trust: 20–50/wk
- Below 30% accept rate → invite restrictions
- Profile visits: 80/day max · 1st-degree DMs: 40/day max
- Random delays 90–240 s · Active hours only · No weekends

### Daily cadence (Mon–Fri)
- 10 invites to engagers (warm) — auto-pause if 7-day acceptance < 25%
- 80 profile visits (half come back to your profile)
- 20 DM replies + 10 keyword-magnet auto-DMs
- 15 comments (Track C ritual)

### Sales Navigator Boolean (paste in Week 1)

```
Agency owners (US):
(title:("Founder" OR "Owner" OR "CEO") AND industry:("Marketing Services" OR "Advertising Services") AND companySize:"11-50" AND geography:"United States")

Solopreneur consultants:
(title:("Coach" OR "Consultant" OR "Advisor") AND keywords:("AI" OR "automation" OR "scale") AND geography:("United States" OR "United Kingdom" OR "Canada" OR "Australia"))
```

Save as Sales Nav lead lists. Refresh weekly with `Posted on LinkedIn in past 30 days`.

### The 4-step DM sequence (cold path, after accept)

Spaced Day 0 / 2 / 4 / 6. Stop on reply.

1. **D0:** *"Thanks for connecting, {{firstName}}. Curious — is {{specific pain}} something you're tackling now or already solved?"*
2. **D2 (voice note, 30 s):** Reference one thing from their LinkedIn. (Voice DMs +28% reply vs. text in 2026.)
3. **D4 (free resource, no ask):** *"Saw you posted about X. This made me think of you — [magnet link]. No reply needed."*
4. **D6 (last touch):** *"Last note from me — if {{pain}} is on the table this quarter, happy to spend 15 min mapping the bottleneck. No pitch unless we both think there's fit. [Calendly]"*

After D6 → 6-month dormant list. Re-engage on hyper-relevant content only.

### The warm DM path (engagers — your highest converter)

Comment-keyword on your post → auto-DM the matching magnet within 5 min → 24h human follow-up → 72h problem question → audit offer if they describe a real problem. ~10% of magnet-grabbers book a call.

### Never send
- Calendly link in the first DM
- A pitch deck before they asked for it
- "Just checking in" / "circle back" / "synergies"
- Walls of text

---

## 8. Tool Stack ($235/mo) — Pick One Per Job

Stack risk is real: more tools = higher detection. **One tool per job.**

| Tool | Use | Cost |
|------|-----|------|
| Sales Navigator Core | ICP filtering + Boolean + 200 invite cap | $99/mo |
| HeyReach | Connection invites + DM sequencing (cloud, dedicated proxy) | $79/mo |
| Authoredup | Post formatting + dwell-time analytics | $19/mo |
| Shield Analytics | Per-post data, follow-source attribution | $29/mo |
| Calendly | 15-min audit booking | already have |
| n8n (self-host) | Glue: keyword → DM → CRM | already have |

**Avoid:** Phantombuster, Dux-Soup, LinkedHelper. Browser-extension fingerprints are the #1 ban vector in 2026.

**Account safety:** one tool per session, residential IP, no concurrent Chrome extensions, no automation overnight or weekends. If 7-day accept rate <25%, auto-pause invites for 48 h — recover in days, not weeks.

---

## 9. The First Four Weeks (in detail — this is what determines whether the rest works)

### Week 1
- D1: Make the 5 decisions (§1). Write thesis sentence. Pin it.
- D2: Profile rebuild (§5). Apply for LinkedIn verification.
- D3: Build productized offer page. Stripe Payment Link.
- D4: DM 50 warmest connections asking what they want more of.
- D5: Schedule 4 posts for Week 2. Draft newsletter issue 1.
- Weekend: Pitch 10 podcasts. Subscribe to 30-creator notifications. Set up Sales Nav with 2 saved searches.

### Week 2
- Mon: Launch the productized offer with a "behind the scenes" post. **Target: 5 sales by Friday = $2,500.**
- Daily: 4 posts/wk + 15 comments + 10 connection invites + Track A DMs.
- Fri: Newsletter issue 1 ships. Promote in 1 post + 1 DM-batch + 1 comment-thread.
- Weekend: 10 more podcast pitches. Post VA job ad on Onlinejobs.ph.

### Week 3
- Daily rhythm locked. No new tactics — just execution.
- Apply for LinkedIn Top Voice (5 collaborative-article answers/week, all on-thesis).
- Email 5 past clients asking for case-study permission. Document 2 with real numbers.

### Week 4
- VA starts. Train on: comment-keyword → DM-magnet flow, inbox triage, scheduling.
- Reach out to 2 mid-tier creators for M2 paid collabs. Negotiate $500–$1,500.
- **Month 1 review (90 min):** posts published, impressions, followers added, calls booked, MRR. What worked, what didn't.
- Decision: if Track A revenue < $1,500 in M1, simplify the offer to one-line copy and $297 price.

**Month 1 KPIs:** 2.5K followers · 200 newsletter subs · 1–3 inbound calls · 5 product sales · 1 podcast booked for M3.

---

## 10. Months 2–6 (the rhythm)

| Month | Followers | News subs | Calls/wk | MRR | Key moves |
|------:|----------:|----------:|---------:|----:|-----------|
| 2 | 5K | 600 | 3 | $4K | First paid creator collab. Top Voice badge. Add $4,997 tier. |
| 3 | 9K | 1.2K | 5 | $7K | Flagship asset launch. First podcast episode airs. **PIVOT CHECK.** |
| 4 | 14K | 2K | 7 | $11K | Second flagship promotion wave. LinkedIn ads on. Hot-take post weekly. |
| 5 | 20K | 3K | 9 | $16K | Host one LinkedIn Live with 4 guests. Productize a $4,997 group cohort. |
| 6 | 28K | 4K | 11 | $22K | Year-in-review flagship carousel. Press push. Stretch shot at the 100K window. |

The above is the **honest base case (50% probability of hitting these numbers)**. The 100K stretch lives in M5–M6 if and only if (a) one podcast goes long-tail viral, (b) one paid collab compounds, (c) the flagship asset gets shared by a >250K creator. Plan for the base case; architect optionality for the stretch.

---

## 11. The M3 Pivot (the most important section)

End of Month 3, look at four numbers:

| Metric | M3 target | If under… |
|--------|-----------|-----------|
| Followers | 9K | Thesis or post quality is broken — post-mortem the bottom 10 posts |
| Newsletter | 1.2K | CTAs are weak — every post needs an explicit subscribe ask for 2 weeks |
| MRR | $5K (cumulative $10K) | Audience isn't your buyer — pivot ICP or simplify offer |
| Calls/wk | 5 | DM funnel is broken — A/B test the warm DM script |

**Decision matrix:**

- **Followers + MRR both on track →** continue plan, push Track D harder.
- **Followers behind, MRR on track →** keep going. The goal is achieved. Followers are vanity; revenue is the win.
- **MRR behind, followers on track →** **kill the audience goal.** M4–M6 = pure outbound + product. 50 cold DMs/day to qualified ICPs + LinkedIn ads + closed-list outreach. Posting drops to 2/wk.
- **Both behind →** stop. Take a week off. Re-pick the thesis and ICP. The plan was wrong, not your effort.

---

## 12. Repo Integration (how the existing assets plug in)

You already own most of the infrastructure. Build these three modules to wire it to LinkedIn:

### 12.1 `linkedin_engine/keyword_dm.py` (n8n + Python)
- Listens for comments on your posts via LinkedIn webhook
- Matches comment text against `lead_magnets/lead_magnets_sheet.csv` keyword column
- Looks up matching `pdf_links.json` URL
- Sends DM via HeyReach API: *"Hey {{firstName}}, here you go — {{magnet}}: {{link}}."*
- Logs to `linkedin_engine/conversions.csv`
- Triggers 24h human follow-up reminder in CRM

### 12.2 `blog_engine/to_carousel.py`
- Input: a markdown post from `blog_engine/posts/`
- Output: 8–10 slide carousel JSON (title + bullets per slide)
- Renders via Canva API. Uses existing AEO `direct_answer_within_words` block as opening slide.

### 12.3 `content-engine linkedin schedule --weeks 4`
- Reads `content_scripts/MASTER_CONTENT_SHEET.csv`
- Filters Status=Written, groups by week + pillar
- Reformats each script: hook + body + CTA + keyword
- Pushes to LinkedIn scheduler via API
- Tags each post in `content_engine/calendar.py`

### 12.4 New tracking files
- `content_scripts/COMMENT_TARGETS.md` — 30-creator list (handle, followers, tier, last-touched, reciprocity rate)
- `content_scripts/HOOK_BANK.md` — 200-row hook DB (formula, niche, last-used) — never reuse a hook in 14 days

---

## 13. Daily / Weekly / Monthly Rhythm

### Daily (90 min, Mon–Fri)
- 08:30 — 15 min: comment on 5 Tier-A posts before publishing
- 09:00 — Publish today's post (drafted yesterday)
- 09:00–10:00 — Reply to every comment within 60 min, trigger keyword DMs
- 12:30 — 15 min: comments round 2 (Tier B + C)
- 15:00 — 15 min: HeyReach review, warm DM follow-ups
- 17:00 — 15 min: draft tomorrow's hook + CTA

### Weekly (Sunday, 3 hrs)
- Review 7-day metrics dashboard
- Write 4 hooks for next week
- Repurpose 1 blog post → 1 carousel
- Newsletter draft → schedule for Friday
- Refresh Sales Nav with last-7-day-active filter
- Update `COMMENT_TARGETS.md` with last-touched dates

### Monthly
- Post-mortem top 3 and bottom 3 posts. Pattern-match.
- Pitch 1 podcast guest spot.
- Add 1 lead magnet + bundle differently.
- Review accept and reply rates; tighten DMs that dropped.

---

## 14. The Single Rule

**Distribution > Content. Always.**

Most founders fail on LinkedIn because they spend 80% of time *making* posts and 20% *distributing*. Reverse it. The 10 minutes before publishing — comments planted on big creators' posts — are more valuable than the 60 you spent writing. If you have 90 min today, spend 30 on the post and 60 on commenting + DMing.

---

## 15. What Tomorrow Morning Looks Like

1. Make the 5 decisions in §1. Write thesis sentence. Pin it.
2. Profile rebuild (§5) — 90 min.
3. Apply for LinkedIn verification.
4. Build the productized offer page on Stripe.
5. DM 50 warmest connections asking what they want more.
6. Pitch 5 podcasts before bed.
7. Book a 90-min Sunday recurring block on your calendar.
8. Open Sales Nav trial + HeyReach trial. Configure 5/day invite warm-up.
9. Draft newsletter issue 1.

That's the launch sequence. Compounding starts the day after.

---

## Sources

- [LinkedIn Algorithm 2026 — 360Brew breakdown — ALM Corp](https://almcorp.com/blog/linkedin-feed-algorithm-update-llm-2026/)
- [LinkedIn Algorithm 2026: Why Your First 60 Min Decide Everything — Growleads](https://growleads.io/blog/linkedin-algorithm-2026-text-vs-video-reach/)
- [LinkedIn Algorithm 2026: What Works Now — DataSlayer](https://www.dataslayer.ai/blog/linkedin-algorithm-february-2026-whats-working-now)
- [Richard van der Blom — Algorithm Insights 2025/26](https://www.linkedin.com/posts/richardvanderblom_want-more-reach-more-engagement-and-more-activity-7323960700844838912-ymze)
- [LinkedIn Content Formats: Performance Stats 2026 — Meet-LEA](https://meet-lea.com/en/blog/linkedin-content-formats-performance)
- [LinkedIn Carousels vs Text vs Video — CarouselMaker](https://carouselmaker.co/en/blog/linkedin-carousels-vs-text-posts-vs-videos)
- [LinkedIn Weekly Connection Limit 2026 — Konnector](https://konnector.ai/linkedin-weekly-connection-request-limit-2026/)
- [LinkedIn Automation Safe Limits — PhantomBuster](https://phantombuster.com/blog/linkedin-automation/linkedin-automation-safe-limits-2026/)
- [Best LinkedIn Automation Tools 2026 — Postiv](https://postiv.ai/blog/best-linkedin-automation-tools)
- [LinkedIn Engagement Pods Crackdown 2026 — ConnectSafely](https://connectsafely.ai/articles/linkedin-engagement-pods-crackdown-2026)
- [LinkedIn Hooks That Actually Work in 2026 — Viral Boris](https://medium.com/@viralboris/linkedin-hooks-that-actually-work-in-2026-50-examples-bbe7976cde67)
- [Top Frameworks for Viral LinkedIn Hooks — UseVisuals](https://usevisuals.com/blog/top-frameworks-for-viral-linkedin-hooks)
- [Mastering LinkedIn in 2026: B2B Lead Generation — The Strategy Story](https://thestrategystory.com/blog/mastering-linkedin-in-2026-a-comprehensive-strategy-for-high-quality-b2b-lead-generation/)
- [LinkedIn Newsletter Strategy Guide 2026 — InfluenceFlow](https://influenceflow.io/resources/linkedin-newsletter-strategy-complete-guide-to-building-an-engaged-subscriber-base-in-2026/)
- [LinkedIn Strategy for SaaS Founders — LinkBoost](https://blog.linkboost.co/linkedin-strategy-for-saas-founders-2026/)
- [Sales Navigator Filters Guide 2026 — Sbl.so](https://sbl.so/linkedin/sales-navigator-filters-guide/)
- [How to Use Sales Navigator Boolean Search — GrackerAI](https://gracker.ai/blog/linkedin-sales-navigator-boolean-search)
- [How I added 100K Followers in 6 months — Steve Blakeman (outlier case)](https://www.linkedin.com/pulse/how-i-added-100000-followers-linkedin-just-6-months-steve-blakeman)
- [From 49 to 10K followers in 17 days — Ruben Hassid (outlier case)](https://ruben.substack.com/p/from-49-to-10000-followers-in-17)
