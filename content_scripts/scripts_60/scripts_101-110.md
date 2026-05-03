# Scripts 101–110 — Week 10

Format: Scarpati 30–60 second video scripts
Source of truth: REAL_DATA.md + KNOWLEDGE_BASE.md + MINDSET_DATA.md

---

## Script 101 — Teaching | Week 10, Monday
**Topic:** How I use Claude Code at 2 AM when nothing works
**Lead Magnet Keyword:** CLAUDE
**Duration:** 45s

**HOOK (0–3s):**
I can't sleep when a project is stuck. The problem just appears in my mind. So I get up and open Claude Code. Here's what happens next.

**SETUP (3–10s):**
Most people hit a wall and step away. "I'll figure it out tomorrow." That works for some. Not for me. When something isn't working, my brain won't shut off until I understand why.

**STORY (10–32s):**
My process when stuck is always the same. I open Claude Code and start building test variations. Not guessing — testing. I'll take the failing workflow and isolate the piece that breaks. Then I ask Claude to explain what's happening like I'm an eighth grader. That usually reveals the gap in my understanding. Then I test one change at a time. Not five changes at once — one. See if it works. If not, revert. Try the next thing. Sometimes this takes an hour. Sometimes it takes until sunrise. But every session — even the ones that don't solve the problem — teaches me something about the system I didn't know before. And when the fix finally clicks, it's not because I got lucky. It's because I eliminated everything that didn't work. That's the same process for art, for music, for freelancing. Iterate until it's right.

**LESSON (32–40s):**
When you're stuck, don't guess. Isolate the failure. Test one thing at a time. Use AI to explain what you don't understand. The fix comes from the process, not from inspiration.

**CTA (40–45s):**
Comment CLAUDE and I'll send you ten Claude prompt files — the debugging one has saved me more nights than I can count.

---

## Script 102 — Teaching | Week 10, Monday
**Topic:** How to build automations from the back, not the front
**Lead Magnet Keyword:** AUTOMATION / SEQUENCE
**Duration:** 45s

**HOOK (0–3s):**
Most people build automations starting from step one. I start from the end. Here's why that changes everything.

**SETUP (3–10s):**
When you build from the front, you make assumptions about every step. By the time you reach the end, half of those assumptions are wrong and you're rebuilding. Building from the back means you know exactly where you're going before you start.

**STORY (10–32s):**
My framework is simple. Start from the end result and work backwards. What does the client need to see when this is done? A lead in the CRM with all their data? A report on their desk every Monday? An email sent within minutes of a website visit? That's the end. Now reverse it. What data needs to exist for that end result? Where does that data come from? What triggers the data collection? Each answer becomes a node in the workflow. By the time I'm done reverse engineering, the automation is already designed — I just haven't built it yet. The question I always ask: "What one thing solves eighty percent of the work? Start there." For the healthcare client, the end result was reaching website visitors before they chose a competitor. Working backwards: personalized email → AI icebreaker → visitor research → visitor tracking. I built the email template last, even though it's the first thing the prospect sees. Everything flows from the end.

**LESSON (32–40s):**
Always reverse engineer. Start from the result. Work backwards. Ask what one thing solves eighty percent. Build that first. The rest follows.

**CTA (40–45s):**
Comment AUTOMATION and I'll send you five n8n workflow templates that all use this backwards approach.

---

## Script 103 — Teaching | Week 10, Tuesday
**Topic:** How to research an API before you commit to a project
**Lead Magnet Keyword:** TOOLS
**Duration:** 45s

**HOOK (0–3s):**
I quoted a project at two days. It took two weeks. That mistake taught me one rule I never break — always check the API before you say yes.

**SETUP (3–10s):**
The fastest way to lose money as a freelancer is to promise something without checking if the tools can do it. A clean-looking CRM might have zero API docs. A simple-sounding integration might need sixty nodes to work. You won't know until you look.

**STORY (10–32s):**
Now before I scope any project, I research the API first. I open the tool's developer docs. If they exist — great. I check what endpoints are available. Can I create records? Read them? Update them? Delete them? If the docs don't exist — I open the browser inspector and check if there are hidden endpoints. That ten-minute check has saved me from quoting two days on something that takes two weeks. With the Lakeshore project, if I'd checked first, I would have known there were no public docs. I still would have taken the project — but I would have priced it differently. Now I also check rate limits. Can I call the API a hundred times per second or will it block me? That determines whether I need a Supabase buffer layer or not. All of this takes thirty minutes. Those thirty minutes decide whether the project is profitable or a nightmare.

**LESSON (32–40s):**
Before you quote, open the API docs. If there are no docs, open the browser inspector. Thirty minutes of research saves you from two weeks of surprises.

**CTA (40–45s):**
Comment TOOLS and I'll send you the full tool stack — every tool I check before committing to a project.

---

## Script 104 — Teaching | Week 10, Tuesday
**Topic:** How to use Go High Level for client CRMs
**Lead Magnet Keyword:** TEMPLATE / CRM
**Duration:** 45s

**HOOK (0–3s):**
I've built CRM systems in Go High Level for fifteen staffing firms. Ten GHL sub-accounts on one project alone. Here's what most people get wrong about it.

**SETUP (3–10s):**
Go High Level is powerful — campaigns, pipelines, automations, sub-accounts. But most people set it up like a contact list. They miss the real power: connecting GHL to everything else in the client's stack.

**STORY (10–32s):**
For staffing firms, GHL handles the outreach. Campaigns go out. Leads respond. But the real value is in what happens after the response. The data needs to flow — from GHL into the CRM, into the tracking system, into the reporting dashboard. With ten sub-accounts, that flow has to be automated. Otherwise you're logging into ten separate dashboards checking things manually. My approach: GHL handles outreach and campaigns. n8n handles the data flow between systems. Supabase acts as the central database when there's too much data for a single API call. One master workflow instead of per-account builds. The staffing firm sees one dashboard, one set of reports, one source of truth — even though the data is flowing through four or five systems behind the scenes.

**LESSON (32–40s):**
GHL is the front. n8n is the glue. Supabase is the buffer. Connect them properly and the client never has to think about where the data lives.

**CTA (40–45s):**
Comment CRM and I'll send you the ClickUp freelancer CRM template. Or comment TEMPLATE for the Notion version.

---

## Script 105 — Teaching | Week 10, Wednesday
**Topic:** How to use Instantly.ai to catch website visitors before they leave
**Lead Magnet Keyword:** AUDIT
**Duration:** 45s

**HOOK (0–3s):**
A healthcare company was burning money on Google ads. Visitors landed on their page, read everything, and left. We started catching those visitors automatically. Same clients at thirty percent of the ad spend.

**SETUP (3–10s):**
Most businesses focus on getting more traffic. More ads. More spend. But what about the people who already visited your website and left without doing anything? That's money you already spent — walking out the door.

**STORY (10–32s):**
Instantly.ai has a website visitor tracking feature. When someone visits a service page but doesn't book or call, the system finds their email, their LinkedIn, their company info. Then Amplify and Serper.ai research their background. Claude writes a personalized icebreaker based on what they were looking at. Within minutes — an email goes out: "I noticed you were looking at our services page. Is there something I can help with?" Plus a LinkedIn connection request. Two touchpoints before they choose a competitor. The healthcare client went from spending heavily on ads to getting the same number of clients at thirty percent of the original spend. Conversion increased thirty-two to forty percent. They didn't need more traffic. They needed to catch what they were already paying for.

**LESSON (32–40s):**
Don't increase ad spend. Capture the people who are already turning away. One tool and one automation can do what doubling your ad budget can't.

**CTA (40–45s):**
If visitors are leaving your website without converting — comment AUDIT. Free fifteen-minute call. I'll show you exactly what you're losing.

---

## Script 106 — Teaching | Week 10, Wednesday
**Topic:** Decrease churn first, then increase leads
**Lead Magnet Keyword:** AUDIT
**Duration:** 30s

**HOOK (0–3s):**
Everyone wants more leads. But if your current leads are leaking out the bottom, more leads just means more waste. Fix the leak first.

**SETUP (3–8s):**
Most businesses pour money into the top of the funnel — ads, outreach, content — while ignoring why their current leads don't convert. That's pouring water into a bucket with a hole.

**STORY (8–22s):**
My framework for every client: decrease churn first, then increase lead income. What's leaking? Why are leads going cold? Why are candidates dropping off? Why are website visitors leaving? Fix those problems before you spend another dollar on getting more traffic. The healthcare client wanted to increase ad spend. I told them to stop. We captured the visitors they were already losing. Same number of clients. Thirty percent of the cost. If we'd just spent more on ads, the new visitors would have leaked out the same way. Fix the bucket. Then fill it.

**LESSON (22–27s):**
Fix the leak before you pour more water. Decrease churn first. Increase leads second. Always in that order.

**CTA (27–30s):**
Comment AUDIT — I'll find the leak in fifteen minutes.

---

## Script 107 — Teaching | Week 10, Thursday
**Topic:** How to use Vidyard to stand out in proposals
**Lead Magnet Keyword:** PROPOSAL
**Duration:** 45s

**HOOK (0–3s):**
Ninety-nine percent of freelancers send text proposals. I send a ninety-second Vidyard video. That's the difference between being ignored and getting a reply.

**SETUP (3–10s):**
Clients on Upwork get dozens of proposals. They all look the same. Same format. Same generic pitch. Same "I'd love to work with you." How do you stand out? Stop writing. Start recording.

**STORY (10–32s):**
After my four-line text proposal, I add one thing — "Happy to share a quick Vidyard walkthrough if you're interested." When they say yes, I record a ninety-second video. I pull up their website or their job post. I point out the specific problem they described. Then I show a similar project I've built — a quick screen share of the workflow running, the dashboard, the result. They see my face. They hear my voice. They see that I actually read their post and thought about their problem. Most freelancers won't do this. It takes five minutes. That's exactly why it works. My biggest project — nearly fifteen thousand dollars — started with a cold proposal and a short video to someone I'd never spoken to before. They didn't hire me because of my resume. They hired me because the video showed I understood their problem.

**LESSON (32–40s):**
Record a short Vidyard video for your best proposals. Show their problem. Show a similar project. Let them see your face. Five minutes that separate you from every other freelancer.

**CTA (40–45s):**
Comment PROPOSAL and I'll send you the four-line proposal template plus the Vidyard approach that makes it work.

---

## Script 108 — Service | Week 10, Friday
**Topic:** What a staffing owner's content dashboard actually looks like
**Lead Magnet Keyword:** HOOKS
**Duration:** 45s

**HOOK (0–3s):**
Thirty videos. Thirty carousels. Ready to review. Ready to post. Here's what the dashboard actually looks like when I deliver content to a staffing firm.

**SETUP (3–10s):**
People hear "sixty pieces of content per month" and think it sounds impossible. Or they think the quality must be terrible. Let me show you how it actually works.

**STORY (10–32s):**
The owner does one onboarding call. Thirty minutes. They give me a three-minute audio sample for voice cloning and a photo. From their business data and ideal candidate and client profiles, I build the content topics. The system generates thirty short-form videos using HeyGen — the owner's face, their cloned voice, speaking about their expertise. Thirty carousels for LinkedIn and Instagram — designed for engagement, tailored to their industry. Everything lands in a dashboard. The owner opens it whenever they want. Each piece of content is there with a preview. They approve, request changes, or skip. Approved content gets scheduled and posted automatically. The owner's total time per week — reviewing the dashboard and hitting approve. That's the entire workflow. One input from them. Sixty outputs per month. Their face. Their voice. Their expertise. Without them recording a single video.

**LESSON (32–40s):**
Sixty pieces of content doesn't require sixty hours of work. It requires one system, one onboarding call, and a dashboard that makes approval easy.

**CTA (40–45s):**
If you're a staffing owner and content feels impossible — comment HOOKS for fifty proven video hooks. Or DM me AUDIT to see if the system fits your company.

---

## Script 109 — Story | Week 10, Saturday
**Topic:** The DocuSign project that almost broke me
**Lead Magnet Keyword:** TOOLS
**Duration:** 60s

**HOOK (0–3s):**
The DocuSign project was my second-biggest project. It was also the one that almost made me quit. No API documentation. No support. Just me and the browser inspector.

**SETUP (3–10s):**
Some projects look simple on paper. "Connect this to that. Automate this step." Then you open the tool and realize — nobody has ever connected this before. There's no guide. No Stack Overflow thread. No YouTube tutorial. You're on your own.

**STORY (10–40s):**
DocuSign needed to connect with the client's system in a way that wasn't supported by the public API. The integration the client needed didn't exist. Every other freelancer who looked at it either quoted a ridiculous price or said it couldn't be done. I said I'd figure it out. Same approach as always — browser inspector. I opened DocuSign in the browser. Clicked through the manual process step by step. Watched the Network tab. Found the hidden API endpoints that DocuSign uses internally but doesn't publish. Copied the payload structures. Recreated the calls in n8n. It wasn't clean. The first attempt failed. The second attempt had rate limit issues. The third attempt worked but broke under load. I kept iterating — the same way I iterate on a drawing that isn't right yet. Test one change. See what happens. Revert if it fails. Try the next thing. Eventually the workflow was solid. Error handling on every node. Rate limiting built in. It's been running since.

**LESSON (40–50s):**
The projects that almost break you are the ones that build your reputation. When every other freelancer says "it can't be done" — that's your opportunity. The hard projects pay the most and teach the most.

**CTA (50–60s):**
The reverse engineering approach works on any tool with a web interface. Comment TOOLS and I'll send you the full tool stack I use.

---

## Script 110 — Contrarian | Week 10, Sunday
**Topic:** You don't need to know everything before you start
**Lead Magnet Keyword:** START
**Duration:** 45s

**HOOK (0–3s):**
When I started freelancing, I didn't know n8n. I didn't know Go High Level. I didn't know Supabase. I learned them on client projects. Here's why that's the right approach.

**SETUP (3–10s):**
People think they need to master every tool before they take a client. They watch courses for months. They build practice projects nobody sees. They feel like they're learning but they're really just delaying. We learn by doing. Not by knowing everything first.

**STORY (10–32s):**
When a client asked me to integrate a tool I'd never used, I didn't say "I don't know that tool." I said "I haven't explored this yet, but I've done similar work with other tools. It should be similar work and won't take extra time." Then I went and learned it. Claude Code explains the concept. Perplexity finds the sources. I open the tool, check the API, make one test call. By the end of the afternoon I know enough to build. Clients value honesty plus willingness to learn. Nobody expects you to know every tool on day one. They expect you to figure it out. That's the difference between a professional and someone who just took a course. The professional says "I'll figure it out" — and then actually does.

**LESSON (32–40s):**
Stop preparing. Start building. You'll learn more on one client project than in six months of courses. If you don't know something, ask. Asking is one skill that will never let you down.

**CTA (40–45s):**
Comment START and I'll send you the zero-to-first-client seven-day guide. Day by day. No prerequisites.
