/**
 * Blog listing page for webaiautomations.com.
 * Drop this into your Bolt project and update the posts array
 * with data from your blog_engine/posts/ markdown files.
 *
 * For Bolt.new: Copy this file, import BlogCard component,
 * and add a route for /blog in your app.
 */
import BlogCard from '../components/BlogCard';

// This array gets populated from your blog_engine/posts/ files.
// In production, you'd fetch this from an API or static JSON.
const posts = [
  {
    title: "How to Build an AI Hiring System for Small Business",
    slug: "ai-hiring-system-small-business",
    meta_description: "Build an AI hiring system that screens candidates automatically. Save 15+ hours/week with Make.com, Typeform, and ClickUp automation.",
    pillar: "Hiring & Operations",
    date: "2026-04-08",
    word_count: 1820,
  },
  {
    title: "How to Create SOPs Automatically Using AI",
    slug: "automated-sop-creation-ai",
    meta_description: "Create standard operating procedures in minutes with AI. Automate SOP creation using Claude, Notion, and Make.com for your business.",
    pillar: "Hiring & Operations",
    date: "2026-04-08",
    word_count: 1700,
  },
  {
    title: "Why Every Solopreneur Needs a Virtual AI COO",
    slug: "virtual-coo-ai-solopreneurs",
    meta_description: "A virtual AI COO handles operations, hiring, and workflows so you can focus on growth. Learn how to build one for under $100/month.",
    pillar: "Hiring & Operations",
    date: "2026-04-08",
    word_count: 1750,
  },
  {
    title: "How to Automate Employee Onboarding with AI",
    slug: "ai-employee-onboarding-automation",
    meta_description: "Automate employee onboarding with AI to save 10+ hours per new hire. Step-by-step guide using Make.com, Notion, and Slack.",
    pillar: "Hiring & Operations",
    date: "2026-04-08",
    word_count: 1800,
  },
  {
    title: "Using ClickUp and AI for Operations Management",
    slug: "clickup-ai-operations-management",
    meta_description: "Transform ClickUp into an AI-powered operations hub. Automate task creation, reporting, and team management with Make.com integration.",
    pillar: "Hiring & Operations",
    date: "2026-04-08",
    word_count: 1750,
  },
];

export default function Blog() {
  return (
    <div className="blog-page">
      <header className="blog-header">
        <h1>Blog</h1>
        <p>
          AI automation insights, tutorials, and case studies for solopreneurs
          who want to scale without hiring.
        </p>
      </header>

      <div className="blog-filters">
        {["All", "AI Automation", "Lead Gen", "Hiring & Operations", "Tools", "Case Studies"].map(
          (filter) => (
            <button key={filter} className="blog-filter-btn">
              {filter}
            </button>
          )
        )}
      </div>

      <div className="blog-grid">
        {posts.map((post) => (
          <BlogCard key={post.slug} post={post} />
        ))}
      </div>

      <style>{`
        .blog-page {
          max-width: 1100px;
          margin: 0 auto;
          padding: 60px 24px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        .blog-header {
          text-align: center;
          margin-bottom: 48px;
        }
        .blog-header h1 {
          font-size: 42px;
          font-weight: 800;
          color: #111827;
          margin: 0 0 12px 0;
        }
        .blog-header p {
          font-size: 18px;
          color: #6b7280;
          max-width: 600px;
          margin: 0 auto;
        }
        .blog-filters {
          display: flex;
          gap: 8px;
          justify-content: center;
          flex-wrap: wrap;
          margin-bottom: 40px;
        }
        .blog-filter-btn {
          padding: 8px 16px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          background: #fff;
          font-size: 14px;
          color: #374151;
          cursor: pointer;
          transition: all 0.15s;
        }
        .blog-filter-btn:hover {
          border-color: #6366f1;
          color: #6366f1;
        }
        .blog-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 24px;
        }
      `}</style>
    </div>
  );
}
