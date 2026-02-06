# Homepage And Content Update Instructions

This file is for coding agents making future updates to this GitHub Pages site.

## Current Behavior (Important)
- Homepage featured sections in `index.html` are manual.
- Homepage highlight counters are data-driven from `data/homepage_highlights.json`.
- Counters update only after running `scripts/build_homepage.py`.
- Blog index cards update only after running `scripts/build_blogs_html.py`.

## Files To Know
- Homepage: `index.html`
- Shared styles: `styles.css`
- Blog listing page: `blogs.html`
- Publications page: `publications.html`
- Homepage counters data: `data/homepage_highlights.json`
- Homepage counters builder: `scripts/build_homepage.py`
- Blog cards builder: `scripts/build_blogs_html.py`
- Crawl/index files: `robots.txt`, `sitemap.xml`

## Navigation Consistency Rules
Use this exact nav set and order on all main pages:
1. `About` -> `index.html`
2. `Research` -> `research.html`
3. `Publications` -> `publications.html`
4. `Awards` -> `awards.html`
5. `Blog` -> `blogs.html`
6. `My Works` -> `projects.html`
7. `Resources` -> `resources.html`
8. `Contact` -> `contact.html`

Do not add `Paper Reviews` in nav unless explicitly requested.

## When Adding A New Blog Post
1. Add/update markdown file in `posts/` with valid front matter (`title`, `date`, etc.).
2. Run:
   - `python3 scripts/build_blogs_html.py`
3. If the new post should be featured on homepage, update the "Latest Blog Posts" links in `index.html`.
4. If counters should change, update `data/homepage_highlights.json` and run:
   - `python3 scripts/build_homepage.py`

## When Adding A New Publication
1. Add publication entry to `publications.html`.
2. If it should be featured, update "Selected Publications" in `index.html`.
3. If counters should change, update `data/homepage_highlights.json` and run:
   - `python3 scripts/build_homepage.py`

## SEO/Metadata Guardrails For Homepage
Ensure `index.html` keeps:
- `meta description`
- canonical URL
- Open Graph tags
- Twitter card tags
- JSON-LD Person block

## Analytics Guardrails For Homepage
For homepage CTAs and featured links, keep `data-analytics-event` and `data-analytics-label` attributes so GA4 tracking continues.

## Validation Commands Before Commit
Run these checks:
1. `python3 scripts/build_homepage.py`
2. `python3 scripts/build_blogs_html.py`
3. `rg -n 'paperreviews\.html' *.html` (should usually return no matches)
4. `for f in index.html research.html publications.html awards.html blogs.html projects.html resources.html contact.html; do echo "--- $f"; sed -n '/<nav>/,/<\/nav>/p' "$f"; done`

## Release Workflow
1. Work in feature branch (preferred prefix: `codex/`).
2. Open PR into `main`.
3. Use squash merge for release unless user requests otherwise.
