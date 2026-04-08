/**
 * Blog post card component for the blog listing page.
 * Drop this into your Bolt project's components/ folder.
 */
export default function BlogCard({ post }) {
  return (
    <a href={`/blog/${post.slug}`} className="blog-card">
      <div className="blog-card-content">
        <span className="blog-card-pillar">{post.pillar}</span>
        <h3 className="blog-card-title">{post.title}</h3>
        <p className="blog-card-description">{post.meta_description}</p>
        <div className="blog-card-meta">
          <span className="blog-card-date">{post.date}</span>
          <span className="blog-card-read-time">
            {Math.ceil(post.word_count / 250)} min read
          </span>
        </div>
      </div>

      <style>{`
        .blog-card {
          display: block;
          text-decoration: none;
          color: inherit;
          background: #fff;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 24px;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        .blog-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        .blog-card-pillar {
          display: inline-block;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #6366f1;
          background: #eef2ff;
          padding: 4px 10px;
          border-radius: 6px;
          margin-bottom: 12px;
        }
        .blog-card-title {
          font-size: 20px;
          font-weight: 700;
          line-height: 1.3;
          margin: 0 0 8px 0;
          color: #111827;
        }
        .blog-card-description {
          font-size: 14px;
          color: #6b7280;
          line-height: 1.5;
          margin: 0 0 16px 0;
        }
        .blog-card-meta {
          display: flex;
          gap: 16px;
          font-size: 13px;
          color: #9ca3af;
        }
      `}</style>
    </a>
  );
}
