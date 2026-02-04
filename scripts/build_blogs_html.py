#!/usr/bin/env python3
"""
Rebuild the <div class="post-grid"> ... </div> section in blogs.html from posts/*.md.

Keeps the rest of blogs.html (including GA snippet and page styling) intact.
"""

from __future__ import annotations

import glob
import html
import os
import re
from dataclasses import dataclass
from datetime import date


def parse_front_matter(md: str) -> tuple[dict[str, str] | None, str]:
    md = md.lstrip("\ufeff")
    if not md.startswith("---\n"):
        return None, md
    end = md.find("\n---\n", 4)
    if end == -1:
        return None, md
    block = md[4:end]
    body = md[end + len("\n---\n") :]
    data: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        data[k] = v
    return data, body


def format_iso_date(iso: str) -> str:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", iso or "")
    if not m:
        return iso or ""
    y, mo, d = map(int, m.groups())
    try:
        dt = date(y, mo, d)
    except ValueError:
        return iso
    # Match the rest of the site: "Jan 24, 2026"
    return dt.strftime("%b %d, %Y").replace(" 0", " ")


def strip_html_tags(s: str) -> str:
    s = re.sub(r"<script\b[^>]*>.*?</script>", " ", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"<style\b[^>]*>.*?</style>", " ", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def strip_markdown(s: str) -> str:
    # Remove fenced code blocks.
    s = re.sub(r"```.*?```", " ", s, flags=re.DOTALL)
    # Remove headings.
    s = re.sub(r"^#{1,6}\s+", "", s, flags=re.MULTILINE)
    # Replace links [text](url) -> text.
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", s)
    # Replace emphasis markers.
    s = s.replace("*", " ").replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def excerpt_from_body(body: str, limit: int = 200) -> str:
    # Prefer stripping HTML if it looks like HTML content.
    text = strip_html_tags(body) if "<" in body and ">" in body else strip_markdown(body)
    # Drop the Medium canonical footer from excerpts.
    text = re.split(r"Originally published on Medium:", text, maxsplit=1)[0].strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


@dataclass
class Post:
    slug: str
    title: str
    date_iso: str
    tag: str
    excerpt: str
    canonical: str
    medium_id: str


def load_posts(posts_dir: str) -> list[Post]:
    candidates: list[Post] = []
    for path in glob.glob(os.path.join(posts_dir, "*.md")):
        slug = os.path.splitext(os.path.basename(path))[0]
        if slug == "template":
            continue
        raw = open(path, "r", encoding="utf-8").read()
        fm, body = parse_front_matter(raw)
        if fm:
            title = fm.get("title", slug)
            date_iso = fm.get("date", "")
            canonical = fm.get("canonical", "")
            source = fm.get("source", "")
            medium_id = fm.get("mediumId", "")
        else:
            title = slug
            date_iso = ""
            canonical = ""
            source = ""
            medium_id = ""
        source_l = source.lower()
        if source_l == "medium" or "medium" in canonical.lower():
            tag = "Medium"
        elif source_l == "wordpress" or "wordpress.com" in canonical.lower():
            tag = "WordPress"
        else:
            tag = "Blog"
        candidates.append(
            Post(
                slug=slug,
                title=title,
                date_iso=date_iso,
                tag=tag,
                excerpt=excerpt_from_body(body),
                canonical=canonical,
                medium_id=medium_id,
            )
        )

    # Deduplicate by canonical URL when present (Medium export can create duplicates if a post
    # was imported earlier under a different slug).
    by_key: dict[str, Post] = {}
    for p in candidates:
        key = p.canonical or p.slug
        current = by_key.get(key)
        if not current:
            by_key[key] = p
            continue

        def score(post: Post) -> tuple[int, int, int]:
            # Higher is better.
            # 1) Prefer posts with a mediumId (more reliable mapping)
            # 2) Prefer "Medium" tag when tied
            # 3) Prefer shorter slugs (nicer URLs)
            return (
                1 if post.medium_id else 0,
                1 if post.tag == "Medium" else 0,
                -len(post.slug),
            )

        if score(p) > score(current):
            by_key[key] = p

    out = list(by_key.values())

    def sort_key(p: Post):
        return p.date_iso or "0000-00-00"

    out.sort(key=sort_key, reverse=True)
    return out


def render_cards(posts: list[Post]) -> str:
    chunks: list[str] = []
    for p in posts:
        date_label = format_iso_date(p.date_iso)
        title = html.escape(p.title)
        excerpt = html.escape(p.excerpt)
        tag = html.escape(p.tag)
        href = f"post.html?post={html.escape(p.slug)}"
        tag_html = f'<span class="post-tag">{tag}</span>'
        if p.canonical and p.tag in {"Medium", "WordPress"}:
            tag_href = html.escape(p.canonical)
            tag_html = (
                f'<a class="post-tag post-tag-link" href="{tag_href}" target="_blank" '
                f'rel="noopener noreferrer">{tag}</a>'
            )
        chunks.append(
            "\n".join(
                [
                    '    <article class="post-card">',
                    f'      <div class="post-date">{html.escape(date_label)}</div>' if date_label else '      <div class="post-date"></div>',
                    '      <h2 class="post-title">',
                    f'        <a href="{href}">{title}</a>',
                    "      </h2>",
                    f'      <p class="post-excerpt">{excerpt}</p>',
                    '      <div class="post-tags">',
                    f"        {tag_html}",
                    "      </div>",
                    f'      <a class="post-link" href="{href}">Read</a>',
                    "    </article>",
                ]
            )
        )
    return "\n".join(chunks) + "\n"


def main() -> int:
    posts = load_posts("posts")
    cards = render_cards(posts)

    blogs_path = "blogs.html"
    raw = open(blogs_path, "r", encoding="utf-8").read()
    start_marker = '<div class="post-grid">'
    start = raw.find(start_marker)
    if start == -1:
        raise SystemExit("blogs.html: could not find post-grid start marker")
    start_end = raw.find(">", start) + 1
    end_marker = "    </div>\n  </main>"
    end = raw.find(end_marker, start_end)
    if end == -1:
        raise SystemExit("blogs.html: could not find post-grid end marker")

    updated = raw[:start_end] + "\n" + cards + raw[end:]
    with open(blogs_path, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"Updated {blogs_path} with {len(posts)} posts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
