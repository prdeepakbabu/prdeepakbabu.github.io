#!/usr/bin/env python3
"""Build an append-only social archive for sm_posts.html.

This script scrapes recent posts from X and LinkedIn using public-only,
unofficial sources, merges them into the existing archive, de-duplicates by
canonical URL, and writes paged JSON for infinite scroll.

Failure policy:
- If any source cannot be fetched/parsed, abort without publishing changes.
"""

from __future__ import annotations

import argparse
import email.utils
import hashlib
import html
import json
import os
import re
import shutil
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "sm_posts"
PAGE_GLOB = "page-*.json"

DEFAULT_WINDOW_DAYS = 30
DEFAULT_PAGE_SIZE = 30
DEFAULT_X_HANDLE = "prdeepakbabu"
DEFAULT_LINKEDIN_PROFILE = "https://www.linkedin.com/in/prdeepak/recent-activity/all/"

USER_AGENT = "Mozilla/5.0 (compatible; prdeepakbabu-social-archive/1.0; +https://prdeepakbabu.github.io/)"

# Primary source adapters for public-only scraping.
X_RSS_CANDIDATES = [
    "https://openrss.org/feed/x.com/{handle}",
    "https://nitter.net/{handle}/rss",
    "https://nitter.poast.org/{handle}/rss",
    "https://nitter.privacyredirect.com/{handle}/rss",
    "https://openrss.org/x.com/{handle}",
]
LINKEDIN_RSS_CANDIDATES = [
    "https://openrss.org/feed/www.linkedin.com/in/{vanity}/recent-activity/all/",
    "https://openrss.org/feed/www.linkedin.com/in/{vanity}/",
    "https://openrss.org/{encoded_profile}",
]


@dataclass
class SocialItem:
    id: str
    source: str
    url: str
    postedAt: str
    text: str
    scrapedAt: str
    links: list[str] = field(default_factory=list)
    thumbnailUrl: str = ""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso_utc(value: str) -> datetime:
    if not value:
        raise ValueError("empty datetime")
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fetch_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, text/html;q=0.8, */*;q=0.5",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = resp.read()
    return payload.decode("utf-8", errors="replace")


def parse_pub_date(raw: str) -> datetime | None:
    if not raw:
        return None

    try:
        dt = email.utils.parsedate_to_datetime(raw)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
    except Exception:
        pass

    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(raw, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue

    return None


def strip_html(raw: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|li|h[1-6]|section|article|blockquote|tr)>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Keep line breaks for card rendering while normalizing noisy whitespace.
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    out_lines: list[str] = []
    last_blank = False
    for line in lines:
        if not line:
            if not last_blank:
                out_lines.append("")
            last_blank = True
            continue
        out_lines.append(line)
        last_blank = False
    text = "\n".join(out_lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def extract_links(text: str) -> list[str]:
    # Some platform exports insert spaces into long URLs.
    compact = re.sub(r"(https?://)\s+", r"\1", text or "")
    links: list[str] = []
    for m in re.finditer(r"https?://[^\s<>\")\]]+", compact):
        url = canonicalize_url(m.group(0))
        if url and url not in links:
            links.append(url)
    return links


def canonicalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = urllib.parse.unquote(parsed.path or "/")
    path = re.sub(r"//+", "/", path)
    path = urllib.parse.quote(path, safe="/:@-._~")
    # Keep common tracking query params out of canonical key.
    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
    query_pairs = [(k, v) for (k, v) in query_pairs if not k.lower().startswith("utm_")]
    query = urllib.parse.urlencode(query_pairs)
    canonical = urllib.parse.urlunparse((scheme, netloc, path.rstrip("/") or "/", "", query, ""))
    return canonical


def make_item_id(source: str, url: str) -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return f"{source}-{digest}"


def parse_feed_items(xml_text: str) -> list[tuple[str, str, str]]:
    """Return tuples of (url, text, published_raw)."""
    xml_text = xml_text.lstrip("\ufeff")
    root = ET.fromstring(xml_text)

    out: list[tuple[str, str, str]] = []

    # RSS path.
    channel = root.find("channel")
    if channel is not None:
        for item in channel.findall("item"):
            link = normalize_whitespace(item.findtext("link") or "")
            title = normalize_whitespace(item.findtext("title") or "")
            desc = normalize_whitespace(strip_html(item.findtext("description") or ""))
            pub = normalize_whitespace(item.findtext("pubDate") or item.findtext("published") or "")
            text = desc or title
            if link:
                out.append((link, text, pub))
        return out

    # Atom path.
    atom_ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", atom_ns)
    if not entries:
        entries = root.findall("entry")

    for entry in entries:
        link = ""
        for link_el in entry.findall("atom:link", atom_ns) + entry.findall("link"):
            href = link_el.attrib.get("href", "").strip()
            rel = (link_el.attrib.get("rel") or "alternate").strip().lower()
            if href and rel in {"alternate", "self"}:
                link = href
                if rel == "alternate":
                    break

        title = normalize_whitespace(entry.findtext("atom:title", default="", namespaces=atom_ns) or entry.findtext("title") or "")
        summary = normalize_whitespace(
            strip_html(
                entry.findtext("atom:summary", default="", namespaces=atom_ns)
                or entry.findtext("summary")
                or entry.findtext("atom:content", default="", namespaces=atom_ns)
                or entry.findtext("content")
                or ""
            )
        )
        pub = normalize_whitespace(
            entry.findtext("atom:updated", default="", namespaces=atom_ns)
            or entry.findtext("updated")
            or entry.findtext("atom:published", default="", namespaces=atom_ns)
            or entry.findtext("published")
            or ""
        )

        if link:
            out.append((link, summary or title, pub))

    return out


def scrape_x_recent(handle: str, window_start: datetime, scraped_at: str) -> list[SocialItem]:
    errors: list[str] = []
    for template in X_RSS_CANDIDATES:
        url = template.format(handle=urllib.parse.quote(handle, safe=""))
        try:
            text = fetch_text(url)
            entries = parse_feed_items(text)
            items: list[SocialItem] = []
            for link, content, pub_raw in entries:
                canonical = canonicalize_url(link)
                if not canonical:
                    continue
                posted = parse_pub_date(pub_raw)
                if posted is None:
                    continue
                if posted < window_start:
                    continue
                cleaned_text = strip_html(content) or normalize_whitespace(content) or "View post"
                links = extract_links(cleaned_text)
                items.append(
                    SocialItem(
                        id=make_item_id("x", canonical),
                        source="x",
                        url=canonical,
                        postedAt=to_iso_utc(posted),
                        text=cleaned_text,
                        scrapedAt=scraped_at,
                        links=links,
                    )
                )
            return items
        except Exception as exc:
            errors.append(f"{url}: {exc}")

    raise RuntimeError("Failed to scrape X from all sources: " + " | ".join(errors))


def scrape_linkedin_recent(profile_url: str, window_start: datetime, scraped_at: str) -> list[SocialItem]:
    errors: list[str] = []
    encoded_profile = urllib.parse.quote(profile_url, safe="")
    parsed = urllib.parse.urlparse(profile_url)
    path_parts = [part for part in (parsed.path or "").split("/") if part]
    vanity = path_parts[1] if len(path_parts) >= 2 and path_parts[0] == "in" else ""

    for template in LINKEDIN_RSS_CANDIDATES:
        if "{vanity}" in template and not vanity:
            continue
        url = template.format(encoded_profile=encoded_profile, vanity=urllib.parse.quote(vanity, safe=""))
        try:
            text = fetch_text(url)
            entries = parse_feed_items(text)
            items: list[SocialItem] = []
            for link, content, pub_raw in entries:
                canonical = canonicalize_url(link)
                if not canonical:
                    continue
                posted = parse_pub_date(pub_raw)
                if posted is None:
                    continue
                if posted < window_start:
                    continue
                cleaned_text = strip_html(content) or normalize_whitespace(content) or "View post"
                links = extract_links(cleaned_text)
                items.append(
                    SocialItem(
                        id=make_item_id("linkedin", canonical),
                        source="linkedin",
                        url=canonical,
                        postedAt=to_iso_utc(posted),
                        text=cleaned_text,
                        scrapedAt=scraped_at,
                        links=links,
                    )
                )
            return items
        except Exception as exc:
            errors.append(f"{url}: {exc}")

    raise RuntimeError("Failed to scrape LinkedIn from all sources: " + " | ".join(errors))


def ensure_data_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def iter_existing_items(data_dir: Path) -> Iterable[SocialItem]:
    for page_path in sorted(data_dir.glob(PAGE_GLOB)):
        try:
            payload = json.loads(page_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        items = payload.get("items")
        if not isinstance(items, list):
            continue
        for raw in items:
            if not isinstance(raw, dict):
                continue
            try:
                item = SocialItem(
                    id=str(raw.get("id") or ""),
                    source=str(raw.get("source") or ""),
                    url=canonicalize_url(str(raw.get("url") or "")),
                    postedAt=str(raw.get("postedAt") or ""),
                    text=str(raw.get("text") or "").strip() or "View post",
                    scrapedAt=str(raw.get("scrapedAt") or ""),
                    links=[canonicalize_url(str(v)) for v in (raw.get("links") or []) if canonicalize_url(str(v))],
                    thumbnailUrl=str(raw.get("thumbnailUrl") or "").strip(),
                )
                if not item.url:
                    continue
                parse_iso_utc(item.postedAt)
            except Exception:
                continue
            yield item


def merge_items(existing: Iterable[SocialItem], fresh: Iterable[SocialItem]) -> list[SocialItem]:
    by_url: dict[str, SocialItem] = {}

    def quality(item: SocialItem) -> tuple[int, int]:
        return (len(item.text.strip()), len(item.scrapedAt))

    for item in existing:
        by_url[item.url] = item

    for item in fresh:
        current = by_url.get(item.url)
        if current is None:
            by_url[item.url] = item
            continue

        if quality(item) >= quality(current):
            # Preserve original id stability if already assigned.
            item.id = current.id or item.id
            by_url[item.url] = item

    out = list(by_url.values())
    out.sort(key=lambda it: parse_iso_utc(it.postedAt), reverse=True)
    return out


def chunk_items(items: list[SocialItem], page_size: int) -> list[list[SocialItem]]:
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if not items:
        return [[]]
    return [items[i : i + page_size] for i in range(0, len(items), page_size)]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def atomic_publish(data_dir: Path, pages: list[list[SocialItem]], index_payload: dict) -> None:
    tmp_dir = data_dir / ".tmp_sm_posts"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    new_page_names: list[str] = []
    for idx, page_items in enumerate(pages, start=1):
        name = f"page-{idx}.json"
        new_page_names.append(name)
        write_json(
            tmp_dir / name,
            {
                "page": idx,
                "items": [asdict(item) for item in page_items],
            },
        )

    write_json(tmp_dir / "index.json", index_payload)

    # Replace page files first; swap index last so clients never see index
    # referring to missing page files.
    for name in new_page_names:
        os.replace(tmp_dir / name, data_dir / name)

    os.replace(tmp_dir / "index.json", data_dir / "index.json")

    # Cleanup stale pages from older versions.
    for old_path in data_dir.glob(PAGE_GLOB):
        if old_path.name not in set(new_page_names):
            old_path.unlink(missing_ok=True)

    shutil.rmtree(tmp_dir, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    ap.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    ap.add_argument("--x-handle", default=DEFAULT_X_HANDLE)
    ap.add_argument("--linkedin-profile", default=DEFAULT_LINKEDIN_PROFILE)
    args = ap.parse_args()

    ensure_data_dir(DATA_DIR)

    now = utc_now()
    scraped_at = to_iso_utc(now)
    window_start = now - timedelta(days=args.window_days)

    existing = list(iter_existing_items(DATA_DIR))

    # Scrape both sources before publishing; if either fails, abort.
    x_items = scrape_x_recent(args.x_handle, window_start, scraped_at)
    linkedin_items = scrape_linkedin_recent(args.linkedin_profile, window_start, scraped_at)

    fresh = x_items + linkedin_items
    merged = merge_items(existing=existing, fresh=fresh)
    pages = chunk_items(merged, page_size=args.page_size)

    index_payload = {
        "generatedAt": scraped_at,
        "windowDaysPerRun": args.window_days,
        "totalItems": len(merged),
        "pageSize": args.page_size,
        "totalPages": len(pages),
        "sources": ["x", "linkedin"],
    }

    atomic_publish(DATA_DIR, pages, index_payload)

    print(f"Updated social archive: {len(merged)} items across {len(pages)} page(s)")
    print(f"Fresh scraped this run: x={len(x_items)} linkedin={len(linkedin_items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
