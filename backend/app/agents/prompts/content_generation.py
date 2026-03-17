CONTENT_GENERATION_SYSTEM = """You are BACE (Bito-Aware Content Engine), a content generation agent for Bito.

Bito is an AI-powered code review and developer productivity platform. You create high-quality, engaging content that:
- Speaks authentically to software engineers and engineering leaders
- Shares genuine insights, not generic advice
- Uses a conversational, knowledgeable tone — not corporate speak
- Incorporates real data points, stories, and examples
- Drives engagement through relatable developer experiences

{writing_style_guide}

IMPORTANT RULES:
- Never use buzzwords without substance
- Lead with the insight, not the product
- Make it feel like it came from a thoughtful engineering leader, not a marketing team
- Each piece should teach something or challenge a common assumption"""

LINKEDIN_GENERATION_USER = """Generate {count} LinkedIn posts for Bito this week.

**Weekly Context Brief:**
{context_brief}

**This Week's Top Insights:**
{insights}

**Past Top Performers (for style reference):**
{top_performers}

For each post, provide:
1. category: The content category (thought-leadership, product-update, industry-trend, customer-story, engineering-culture, how-to)
2. body: The full post body (800-1500 characters for LinkedIn). Do NOT include the hook in the body.
3. hooks: Exactly 8 hook options (the opening line), ranked by predicted engagement. Each hook should be a different angle/approach.
4. suggested_post_time: Best day and time to post (e.g., "Tuesday 9am EST")

Respond as JSON array:
[
  {{
    "category": "...",
    "body": "...",
    "hooks": ["hook1", "hook2", ...],
    "suggested_post_time": "..."
  }}
]"""

TWITTER_GENERATION_USER = """Generate {count} Twitter/X posts for Bito this week.

**Weekly Context Brief:**
{context_brief}

**This Week's Top Insights:**
{insights}

For each post, provide:
1. category: The content category
2. body: The tweet (max 280 chars) or thread (array of tweets, each max 280 chars)
3. hooks: 8 opening line variations
4. suggested_post_time: Best time to post

Respond as JSON array:
[
  {{
    "category": "...",
    "body": "...",
    "hooks": ["hook1", "hook2", ...],
    "suggested_post_time": "..."
  }}
]"""

BLOG_GENERATION_USER = """Generate {count} blog post outlines for Bito this week.

**Weekly Context Brief:**
{context_brief}

**This Week's Top Insights:**
{insights}

For each blog post, provide:
1. category: The content category
2. body: A detailed outline with sections, key points, and suggested data/examples to include
3. hooks: 8 title/headline options
4. suggested_post_time: Best day to publish

Respond as JSON array."""

EMAIL_GENERATION_USER = """Generate a weekly email newsletter draft for Bito.

**Weekly Context Brief:**
{context_brief}

**This Week's Top Insights:**
{insights}

Provide:
1. category: "newsletter"
2. body: The full newsletter body in markdown. Include: intro, 2-3 key sections, product update, CTA
3. hooks: 8 subject line options
4. suggested_post_time: Best send time

Respond as JSON array with one item."""
