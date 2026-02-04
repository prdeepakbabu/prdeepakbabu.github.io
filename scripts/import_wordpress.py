#!/usr/bin/env python3
"""
Import posts from a WordPress RSS feed into the site's `posts/*.md` format.

Goals:
- Preserve links and images (we store body as HTML from <content:encoded>).
- Use original WordPress publish date.
- Avoid importing posts that already exist from Medium (by title match and/or canonical URL).

Default source feed: https://prdeepakbabu.wordpress.com/feed/?paged=N
"""

from __future__ import annotations

import argparse
import glob
import html
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


WP_FEED_BASE = "https://prdeepakbabu.wordpress.com/feed/"


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "post"


def yaml_quote(s: str) -> str:
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f"\"{s}\""


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


def normalize_title(title: str) -> str:
    title = html.unescape(title or "").lower()
    title = re.sub(r"\s+", " ", title).strip()
    title = re.sub(r"[^a-z0-9 ]+", "", title)
    return title


def load_existing_medium_titles(posts_dir: str) -> set[str]:
    titles: set[str] = set()
    for path in glob.glob(os.path.join(posts_dir, "*.md")):
        slug = Path(path).stem
        if slug == "template":
            continue
        raw = Path(path).read_text(encoding="utf-8")
        fm, _ = parse_front_matter(raw)
        if not fm:
            continue
        if fm.get("source") != "medium":
            continue
        titles.add(normalize_title(fm.get("title", "")))
    return titles


def load_existing_canonicals(posts_dir: str) -> set[str]:
    out: set[str] = set()
    for path in glob.glob(os.path.join(posts_dir, "*.md")):
        slug = Path(path).stem
        if slug == "template":
            continue
        raw = Path(path).read_text(encoding="utf-8")
        fm, _ = parse_front_matter(raw)
        if not fm:
            continue
        canonical = (fm.get("canonical") or "").strip()
        if canonical:
            out.add(canonical)
    return out


def fetch_url(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; prdeepakbabu.github.io importer)",
            "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


@dataclass
class WpItem:
    title: str
    link: str
    date_iso: str
    content_html: str


def parse_wp_feed(xml_bytes: bytes) -> list[WpItem]:
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        return []

    ns = {
        "content": "http://purl.org/rss/1.0/modules/content/",
    }

    items: list[WpItem] = []
    for it in channel.findall("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        dt = parsedate_to_datetime(pub) if pub else datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        date_iso = dt.astimezone(timezone.utc).strftime("%Y-%m-%d")

        content_el = it.find("content:encoded", ns)
        content_html = (content_el.text or "").strip() if content_el is not None else ""
        items.append(WpItem(title=title, link=link, date_iso=date_iso, content_html=content_html))
    return items


def strip_wp_footer(html_body: str) -> str:
    # WordPress often appends:
    # <p>The post <a ...>Title</a> appeared first on <a ...>Site</a>.</p>
    html_body = re.sub(
        r"<p>\\s*The post\\s+.*?appeared first on\\s+.*?</p>\\s*$",
        "",
        html_body,
        flags=re.IGNORECASE | re.DOTALL,
    ).strip()
    return html_body


def slug_from_wp_link(link: str) -> str:
    # Prefer the last path segment (WordPress usually has /YYYY/MM/DD/slug/).
    try:
        path = urllib.request.urlparse(link).path
    except Exception:
        path = ""
    parts = [p for p in path.split("/") if p]
    if parts:
        last = parts[-1]
        # Sometimes the last part is numeric; fallback to title slug later.
        if re.fullmatch(r"\d+", last):
            return ""
        return slugify(last)
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts-dir", default="posts")
    ap.add_argument("--max-pages", type=int, default=50)
    args = ap.parse_args()

    posts_dir = args.posts_dir
    os.makedirs(posts_dir, exist_ok=True)

    medium_titles = load_existing_medium_titles(posts_dir)
    existing_canonicals = load_existing_canonicals(posts_dir)

    imported = 0
    skipped_duplicates = 0

    for page in range(1, args.max_pages + 1):
        url = WP_FEED_BASE if page == 1 else f"{WP_FEED_BASE}?paged={page}"
        try:
            xml_bytes = fetch_url(url)
        except Exception:
            break

        items = parse_wp_feed(xml_bytes)
        if not items:
            break

        for item in items:
            if not item.link or not item.title:
                continue

            # Skip if WordPress link already imported.
            if item.link in existing_canonicals:
                skipped_duplicates += 1
                continue

            # Skip if Medium already has this title (cross-posted).
            if normalize_title(item.title) in medium_titles:
                skipped_duplicates += 1
                continue

            slug = slug_from_wp_link(item.link) or slugify(item.title)
            out_slug = slug
            out_path = os.path.join(posts_dir, f"{out_slug}.md")
            if os.path.exists(out_path):
                out_slug = f"{slug}-wp"
                out_path = os.path.join(posts_dir, f"{out_slug}.md")

            body = strip_wp_footer(item.content_html)
            fm_lines = [
                "---",
                f"title: {yaml_quote(item.title)}",
                f"date: {yaml_quote(item.date_iso)}",
                f"canonical: {yaml_quote(item.link)}",
                'source: "wordpress"',
                "---",
                "",
            ]
            md = "\n".join(fm_lines) + body

            Path(out_path).write_text(md, encoding="utf-8")
            imported += 1
            existing_canonicals.add(item.link)

        # If we got fewer than 10 items, likely the last page.
        if len(items) < 10:
            break

    print(f"Imported WordPress posts: {imported}")
    print(f"Skipped (duplicates/cross-posted): {skipped_duplicates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

