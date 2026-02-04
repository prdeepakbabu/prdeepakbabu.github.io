#!/usr/bin/env python3
"""
Import Medium export ZIP posts into the site's `posts/*.md` format.

- Skips draft posts (filenames starting with `draft_`).
- Uses Medium publish date from dt-published.
- Extracts featured image (data-is-featured="true") as coverImage and removes it from body.
- Keeps the rest of the post body as HTML (works with marked.js passthrough).
- Adds a small canonical footer.
- Updates/overwrites existing posts by matching Medium post id (12-hex) from canonical or filename.
"""

from __future__ import annotations

import argparse
import glob
import html
import os
import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime


RE_POST_ID = re.compile(r"([0-9a-f]{11,12})(?:\\b|$)", re.IGNORECASE)

# Notes / short responses that we don't want to show as blog posts on the site.
# (They appear in Medium exports as posts, but read like comment replies.)
SKIP_MEDIUM_IDS = {
    "92e1a7ff8451",  # "interesting content."
    "64159929259d",  # "Amit, good point."
    "4f9eb273e8e2",  # "interesting read !"
    "1f61ecb0870d",  # "Hoh is really beautiful"
    "78a14d432e4d",  # "I see your viewpoint"
}


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "post"


def yaml_quote(s: str) -> str:
    # Always emit as a double-quoted YAML scalar.
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
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        data[k] = v
    return data, body


def extract_medium_id_from_url(url: str) -> str | None:
    if not url:
        return None
    m = RE_POST_ID.search(url)
    return m.group(1).lower() if m else None


def find_existing_by_medium_id(posts_dir: str) -> dict[str, str]:
    # medium_id -> slug (filename without .md)
    mapping: dict[str, str] = {}
    for path in glob.glob(os.path.join(posts_dir, "*.md")):
        if os.path.basename(path) == "template.md":
            continue
        try:
            raw = open(path, "r", encoding="utf-8").read()
        except OSError:
            continue
        fm, _ = parse_front_matter(raw)
        if not fm:
            continue
        mid = (fm.get("mediumId") or "").strip().lower() or extract_medium_id_from_url(fm.get("canonical", ""))
        if not mid:
            # fall back to filename suffix
            mid = extract_medium_id_from_url(os.path.splitext(os.path.basename(path))[0] or "")
        if mid:
            mapping[mid] = os.path.splitext(os.path.basename(path))[0]
    return mapping


@dataclass
class MediumExportPost:
    title: str
    date_iso: str
    canonical: str
    cover_image: str | None
    medium_id: str | None
    body_html: str


def parse_export_post(html_doc: str, filename: str) -> MediumExportPost:
    # Title
    title = ""
    m = re.search(r"<title>(.*?)</title>", html_doc, flags=re.IGNORECASE | re.DOTALL)
    if m:
        title = html.unescape(re.sub(r"\s+", " ", m.group(1)).strip())

    # Canonical URL (export footer has <a class="p-canonical">Canonical link</a>)
    canonical = ""
    m = re.search(r'<a[^>]*class="p-canonical"[^>]*href="([^"]+)"', html_doc, flags=re.IGNORECASE)
    if m:
        canonical = html.unescape(m.group(1).strip())
    else:
        # Export uses both `href="..." class="p-canonical"` and the reverse ordering.
        m = re.search(r'<a[^>]*href="([^"]+)"[^>]*class="p-canonical"', html_doc, flags=re.IGNORECASE)
        if m:
            canonical = html.unescape(m.group(1).strip())

    # Published datetime
    date_iso = ""
    m = re.search(r'<time[^>]+class="dt-published"[^>]+datetime="([^"]+)"', html_doc, flags=re.IGNORECASE)
    if m:
        dt = m.group(1).strip()
        date_iso = dt[:10]
    else:
        # Fallback to filename prefix (YYYY-MM-DD_)
        m2 = re.match(r"^(\d{4}-\d{2}-\d{2})_", os.path.basename(filename))
        if m2:
            date_iso = m2.group(1)
    if not date_iso:
        date_iso = datetime.utcnow().strftime("%Y-%m-%d")

    # Extract body section HTML
    start = html_doc.find('<section data-field="body"')
    if start == -1:
        # Some exports may differ; fallback to e-content.
        start = html_doc.find('class="e-content"')
        start = html_doc.rfind("<section", 0, start) if start != -1 else -1
    if start == -1:
        raise ValueError(f"Could not find body section in {filename}")
    start_end = html_doc.find(">", start)
    if start_end == -1:
        raise ValueError(f"Malformed body section tag in {filename}")
    start_end += 1

    footer = html_doc.find("<footer", start_end)
    if footer == -1:
        footer = len(html_doc)
    end = html_doc.rfind("</section>", start_end, footer)
    if end == -1:
        raise ValueError(f"Could not find closing body section in {filename}")
    body_html = html_doc[start_end:end]

    # Featured image as cover
    cover_image = None
    m = re.search(r'<img[^>]+data-is-featured="true"[^>]+src="([^"]+)"', body_html, flags=re.IGNORECASE)
    if m:
        cover_image = html.unescape(m.group(1).strip())
        # Prefer a slightly larger size than export default.
        cover_image = cover_image.replace("/max/800/", "/max/1024/")

        # Remove the figure containing the featured image to avoid duplicate with cover.
        body_html = re.sub(
            r'<figure[^>]*>\s*<img[^>]*data-is-featured="true"[^>]*>.*?</figure>',
            "",
            body_html,
            flags=re.IGNORECASE | re.DOTALL,
            count=1,
        )

    # Remove the leading title header inside Medium body (usually graf--title).
    body_html = re.sub(
        r'<h[1-6][^>]*\bgraf--title\b[^>]*>.*?</h[1-6]>',
        "",
        body_html,
        flags=re.IGNORECASE | re.DOTALL,
        count=1,
    )
    # Some exports use a strong-in-h3 title without graf--title class; remove first h3 if it matches title.
    if title:
        body_html = re.sub(
            rf'<h3[^>]*>\s*(?:<strong[^>]*>)?\s*{re.escape(title)}\s*(?:</strong>)?\s*</h3>',
            "",
            body_html,
            flags=re.IGNORECASE,
            count=1,
        )

    # Remove Medium tracking pixels.
    body_html = re.sub(
        r'<img[^>]+src="https?://medium\\.com/_/stat[^"]*"[^>]*>',
        "",
        body_html,
        flags=re.IGNORECASE,
    )

    # Normalize remaining Medium CDN images to a sane max width.
    body_html = re.sub(r"https://cdn-images-1\\.medium\\.com/max/800/", "https://cdn-images-1.medium.com/max/1024/", body_html)

    medium_id = extract_medium_id_from_url(canonical) or extract_medium_id_from_url(filename)
    body_html = body_html.strip()

    return MediumExportPost(
        title=title or "Untitled",
        date_iso=date_iso,
        canonical=canonical,
        cover_image=cover_image,
        medium_id=medium_id,
        body_html=body_html,
    )


def build_md(post: MediumExportPost) -> str:
    fm_lines = [
        "---",
        f"title: {yaml_quote(post.title)}",
        f"date: {yaml_quote(post.date_iso)}",
    ]
    if post.cover_image:
        fm_lines.append(f"coverImage: {yaml_quote(post.cover_image)}")
    if post.canonical:
        fm_lines.append(f"canonical: {yaml_quote(post.canonical)}")
    fm_lines.append(f"mediumId: {yaml_quote(post.medium_id or '')}")
    fm_lines.append('source: "medium"')
    fm_lines.append("---")
    fm = "\n".join(fm_lines)

    footer = ""
    if post.canonical:
        footer = (
            "\n\n<hr>\n\n"
            f'<p><em>Originally published on Medium:</em> <a href="{html.escape(post.canonical)}">{html.escape(post.canonical)}</a></p>\n'
        )
    return f"{fm}\n\n{post.body_html}{footer}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default="", help="Path to Medium export zip (default: medium-export-*.zip in repo root)")
    ap.add_argument("--posts-dir", default="posts", help="Output posts directory")
    args = ap.parse_args()

    zip_path = args.zip
    if not zip_path:
        matches = sorted(glob.glob("medium-export-*.zip"))
        if not matches:
            print("No medium-export-*.zip found in repo root.", file=sys.stderr)
            return 2
        zip_path = matches[-1]

    posts_dir = args.posts_dir
    os.makedirs(posts_dir, exist_ok=True)

    existing = find_existing_by_medium_id(posts_dir)
    imported = 0
    skipped_drafts = 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        members = [m for m in zf.namelist() if m.startswith("posts/") and m.endswith(".html")]
        for member in sorted(members):
            base = os.path.basename(member)
            if base.startswith("draft_"):
                skipped_drafts += 1
                continue

            raw = zf.read(member).decode("utf-8", errors="replace")
            post = parse_export_post(raw, base)
            if post.medium_id and post.medium_id in SKIP_MEDIUM_IDS:
                continue

            # Decide output slug:
            # - Prefer updating an existing file with the same medium id.
            # - Otherwise, use a stable "-medium" suffix to avoid duplicates with any hand-authored slugs.
            slug = None
            if post.medium_id and post.medium_id in existing:
                slug = existing[post.medium_id]
            else:
                slug = f"{slugify(post.title)}-medium"
                out_path = os.path.join(posts_dir, f"{slug}.md")
                if os.path.exists(out_path):
                    # Fall back to including the id to avoid collisions across same-title posts.
                    mid = post.medium_id or "medium"
                    slug = f"{slugify(post.title)}-{mid}"

            out_path = os.path.join(posts_dir, f"{slug}.md")
            md = build_md(post)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md)
            imported += 1

    print(f"Imported/updated: {imported} posts")
    print(f"Skipped drafts: {skipped_drafts} posts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
