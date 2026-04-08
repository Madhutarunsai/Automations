# Bolt Blog Template for webaiautomations.com

## Quick Setup (in Bolt.new)

1. Open your project in Bolt.new
2. Tell Bolt:

```
Add a blog page to my website. Here are the components:
- A BlogCard component (paste BlogCard.jsx)
- A Blog page (paste Blog.jsx)  
- Add a /blog route
- Style it to match my existing site design
```

3. Bolt will integrate it with your existing site

## Adding New Blog Posts

Every day, the blog engine generates 5 posts in `blog_engine/posts/`.
To add them to your Bolt site:

1. Copy the frontmatter data (title, slug, meta_description, etc.)
2. Add it to the `posts` array in Blog.jsx
3. Create a new page for each post's full content

## Automating with Make.com (recommended)

For fully automated daily publishing:

1. Create a Make.com scenario triggered by a webhook
2. The blog engine sends new post data to the webhook
3. Make.com pushes the content to your Bolt/deployed site
4. Zero manual work — 5 posts appear daily

## File Structure

```
bolt_template/
├── components/
│   └── BlogCard.jsx      ← Post preview card
├── pages/
│   └── Blog.jsx          ← Blog listing page
└── README.md             ← This file
```
