# Tarun's Problem-Solving & Mindset — For Script Writing

## How He Approaches a New Client Problem

1. Ask them to walk through their current system first
2. Ask "what problem do you THINK you have?"
3. Listen — then identify the REAL problem (often different)
4. Key questions he asks:
   - "Where are you putting most of your time?"
   - "What is the value of your time / each employee's hour?"
   - "Why did you choose me instead of everyone else on Upwork?"
   - "Where is the most time going?"
   - "What is stopping you from scaling?"
5. Diagnose based on revenue level:
   - Under $50K-$200K → it's a lead gen problem
   - 25+ employees but always messy → project management / CRM / fulfilment problem
6. Frame the problem back to them: "This is the problem you're having. Because of it, this is the result you're getting. If you cut through this one thing, you'll reach X in six months. Am I right?"
7. Once they feel understood → "it's a piece of cake"

**Key insight: He works on the PROBLEM first. Never the solution. Understand before you build.**

## Shiny Object Syndrome — Real Example

A new staffing client kept asking for more features:
- "I want to hire more people"
- "I want more clients"
- "I want to optimize the system"
- "I want this feature, that feature"
- Constantly changing scope

How Tarun handled it:
1. "Yes, that's a good idea. Can I suggest something?"
2. Wait for them to say yes
3. "What is the North Star metric? What one thing solves all problems?"
4. Answer: Money. Because we're starting out.
5. "How do you get money? By getting clients first."
6. "Let's set a goal: reach out to 2,000 prospects this month"
7. "Once we have responses, THEN we automate hiring"
8. Phases: Phase 1 = leads. Phase 2 = features. Phase 3 = optimization.
9. "I'll do what you want, but I'll always give you an option of what's more important RIGHT NOW."

**His line: "If we're building systems without money coming in, it's just another toy we're creating to show off. And nobody will even see it because you won't be recognizable yet."**

## When Projects Go Wrong — Real Story

**The Lakeshore / Back Office CRM project:**
- Client: metal company in Texas (doing lead gen, then client asked for internal CRM help)
- Estimated: 2 days
- Actually took: 2 WEEKS
- Problem: Lakeshore is one of the oldest CRMs for metal/construction companies
- Zero API documentation anywhere
- Found hidden API endpoints using browser inspector (reverse engineering)
- Had 60+ nodes in the final n8n workflow
- 10 GHL sub-accounts, 14,000 leads across them
- Solution: Shifted data to Supabase, called leads one at a time by lead ID
- Created ONE workflow that handles all 10 sub-accounts instead of 10 separate ones
- Runs every second, robust error handling
- Client happy because NO other freelancer could find the API endpoints

**Key: He scoped it at 2 days, it took 2 weeks. But he didn't quit — he reverse-engineered the entire thing.**

## How He Prioritizes What to Build First

**Framework: Decrease churn FIRST, then increase lead income.**

Real example — Healthcare client:
- Running Google ads, SEO, getting referrals
- Most leads were unreachable
- Kept spending more on ads but not seeing returns
- Wanted to spend even MORE on ads

Tarun's approach:
1. "You're getting leads from your website. What about people who visit but DON'T take action?"
2. Used Instantly.ai website visitor tracking
3. When someone visits the service page but doesn't book → automatically:
   - Instantly finds their email, LinkedIn, company info
   - Amplify + Serper.ai researches them
   - AI writes personalized icebreakers
   - Email launches immediately + LinkedIn invite
4. "You were looking at our [service] page and didn't take action. Is there something I can help with?"
5. Result: Same number of clients with 30% of the original ad spend
6. Two touch points before they choose a competitor = 32-40% conversion increase

**His line: "Don't increase ad spend. Invest in one tool and my automation to capture the people who are already turning away."**

**Framework summary: Understand → reverse engineer from the end → figure out what solves 80% → automate from the BACK, not the front → always manual first, then automate**

## Hardest Project Ever

GHL to Lakeshore sync:
- Track messages sent, messages received, calls, call themes, call results
- Lakeshore API returns 10,000 leads in one call (can't call individually)
- 10 GHL sub-accounts, 14,000 leads
- Solution: Shifted to Supabase → call one lead at a time by ID
- One master workflow instead of 10
- 60+ n8n nodes
- Runs every second with error handling

## The SOP Philosophy

"If you automate everything without understanding the manual procedure first, you'll project-creep everything."

Process:
1. Learn their SOP first
2. Learn their manual procedure
3. Spend time understanding how it works
4. Create an entity diagram (step 1, step 2...)
5. Build automation from the BACK (not front)
6. "What one thing solves 80% of the work?"
7. Then iterate forward

## When He Doesn't Know Something

Honest approach:
- "I haven't explored this yet, but I've done similar work with [X tool]"
- Explains his experience on the similar thing
- "It should be similar work and won't take extra time"
- Clients value the honesty + willingness to learn

Research process:
1. Claude Code
2. Perplexity
3. Google
4. ChatGPT Deep Research mode
5. Ask it to summarize and "teach me like an eighth grader"
6. Then: "How is this related to what I already know?"
   - e.g., "What's the difference between ClickUp and Monday.com?"
7. Explore the tool, look at the API, test it
8. "We won't know everything at the start. We learn by doing."

## What Makes Him Different From YouTube Course Graduates

**Reverse engineering methodology.**

His analogy: "It's like drawing art. You can copy a portrait by looking at it. But when you need to draw a completely different species, how will you do it? You need experience drawing a horse first. Then you understand how it works, how it looks. Then with your imagination, you can draw a donkey."

- YouTube people learn tools → think they can solve any problem → fail
- Tarun understands the problem first → then picks the tool → builds the solution
- He also makes clients understand problems they don't see yet

**His analogy about parents:** "Your parents have knee pain at 50. They think it's not a big deal. They keep walking on it. You know it's damaging their knees long-term. So you explain what happens if they keep going. THEN you show them the shoes. If you show the shoes first without explaining the problem, they'll say 'don't waste your money.' Same thing in business."

## Hidden API Reverse Engineering Process

Used on: DocuSign, Controlio time tracker, Lakeshore CRM

Process:
1. Open browser Inspector (developer tools)
2. Click manually on the thing you'd normally do
3. Watch the Network tab — see the payload
4. Identify: Where is the API being called? What URL?
5. Identify the method: POST (create), PUT/PATCH (update), GET (read)
6. Copy the payload structure
7. Recreate it in JSON inside n8n or Make.com
8. Call it programmatically — same result as clicking manually
9. Test rate limits (100 calls/second will break it)
10. Add error handling: sleep/wait nodes, retry on failure
11. "Understand the whole process, do it one by one, then make it solid and unbreakable"

**Key insight: He started with the time tracker (Controlio) BEFORE DocuSign, because "if you don't have tracking, all the other things become features that don't work."**
**He also researches APIs BEFORE starting the project to know if it's feasible.**

## At 2 AM When Nothing Works

"I can't sleep. Even if I try, the problem appears in my mind. I'll wake up and start working."

Process when stuck:
1. Use Claude Code to build test variations
2. Understand the problem better through testing
3. Keep iterating until solution found
4. OR: Hire an expert for a consultation on that specific problem

**His advice on spending money: "Pay for expert consultations on specific problems. You'll learn faster than 99% of people who buy courses. Don't pay $500 for a course. Pay $100 for 30 minutes with someone who already solved your exact problem."**

## Lead Gen Is the Only Problem (Under $10K/month)

"Until you have 5-10 clients, you don't need a CRM. Use a Google Sheet. Once you cross $10K/month, THEN you need fulfilment systems."

The trap: People build fancy systems before making money.
"You're trying to be busy but not productive."

Correct order:
1. Reach out to people
2. Ask what their problem is (don't assume)
3. Build the solution for the problem that EXISTS
4. Make money first
5. THEN build systems to scale

## The Hidden Skill: Art & Music

- Draws in 8 mediums: graphite, charcoal, oil painting, acrylic, watercolor, color pencil, mixed media, and his own style
- Plays guitar and piano
- Learned from childhood

**How it connects:** "These things gave me the patience I need to learn new things. Everything won't be a piece of cake. You become good only by becoming bad first. If you fear mistakes and don't have patience, you can't go ahead. Call it stubbornness — I call it patience and a never-give-up attitude. Indecisiveness kills your growth."

## One Piece of Advice to Past Self

**"Just don't stop. Do what you're doing right now."**

## What Makes Him Angry

**When people stop asking "how."**

"90% of people I've met have the capability to do what I did. Many could do it 10x better. But they have low estimation of themselves. They don't ask 'how.'"

"In the world of AI, knowledge is not exclusive anymore. Anyone can learn anything. The only question you need to ask is 'how to do X.' If you don't know something, ask again. If you don't know that, ask again."

"Asking is one skill that will never let you down."

"You were failing 99 times but you only need to be successful once. All 99 times you learned how NOT to do it. That's what life is."

**"Don't hesitate to invest in yourself. Don't think 'I'm gonna waste money.' The learning is what helps you earn more."**
