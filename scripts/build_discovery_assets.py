#!/usr/bin/env python3
"""
Build discovery assets for search engines and AI assistants.

Outputs:
- data/discovery_posts.json
- answers.txt
- llms.txt
- answers.html
- sitemap.xml
"""

from __future__ import annotations

import glob
import html
import json
import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SITE_ROOT = Path(".")
POSTS_DIR = SITE_ROOT / "posts"
DATA_DIR = SITE_ROOT / "data"
SEARCH_INTENT_ANSWERS_PATH = DATA_DIR / "search_intent_answers.json"
SITE_URL = "https://prdeepakbabu.github.io"
AUTHOR_NAME = "Deepak Babu Piskala"
ALLOWED_PRIMARY_CTA_URLS = {
    f"{SITE_URL}/index.html#about",
    f"{SITE_URL}/index.html#featured-work",
}


@dataclass
class PostRecord:
    slug: str
    title: str
    date_iso: str
    summary: str
    topics: list[str]
    question_targets: list[str]
    canonical_source: str
    source: str
    medium_id: str
    site_url: str
    body: str
    mtime_iso: str


@dataclass
class SearchIntentAnswer:
    question: str
    answer: str
    primary_cta_label: str
    primary_cta_url: str
    secondary_cta_label: str
    secondary_cta_url: str
    evidence_links: list[str]


@dataclass
class SearchIntentSection:
    section_id: str
    title: str
    intent_keywords: list[str]
    items: list[SearchIntentAnswer]


def parse_front_matter(md: str) -> tuple[dict[str, str] | None, str]:
    md = md.lstrip("\ufeff")
    if not md.startswith("---\n"):
        return None, md
    end = md.find("\n---\n", 4)
    if end == -1:
        return None, md

    block = md[4:end]
    body = md[end + len("\n---\n") :]
    out: dict[str, str] = {}

    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        out[key] = value

    return out, body


def strip_html_tags(s: str) -> str:
    s = re.sub(r"<script\\b[^>]*>.*?</script>", " ", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"<style\\b[^>]*>.*?</style>", " ", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\\s+", " ", s).strip()
    return s


def strip_markdown(s: str) -> str:
    s = re.sub(r"```.*?```", " ", s, flags=re.DOTALL)
    s = re.sub(r"^#{1,6}\\s+", "", s, flags=re.MULTILINE)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", s)
    s = s.replace("*", " ").replace("_", " ")
    s = re.sub(r"\\s+", " ", s).strip()
    return s


def summarize_body(body: str, limit: int = 180) -> str:
    text = strip_html_tags(body) if "<" in body and ">" in body else strip_markdown(body)
    text = re.split(r"Originally published on Medium:", text, maxsplit=1)[0].strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def split_csv(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def infer_topics(title: str, body: str) -> list[str]:
    text = f"{title} {body}".lower()
    topics: list[str] = []
    mapping = [
        ("Agentic AI", ["agent", "agentic", "sub-agent", "tool", "orchestration"]),
        ("LLMs", ["llm", "language model", "gpt", "transformer"]),
        ("RAG", ["rag", "retrieval", "retrieval-augmented"]),
        ("Speech / ASR", ["speech", "asr", "transcription", "voice"]),
        ("Evaluation", ["benchmark", "evaluate", "evaluation"]),
        ("Software Engineering", ["coding", "spec", "development", "architecture"]),
        ("Machine Learning", ["machine learning", "deep learning", "reinforcement"]),
    ]
    for label, needles in mapping:
        if any(needle in text for needle in needles):
            topics.append(label)
    if not topics:
        topics = ["AI Systems"]
    return topics[:5]


def clean_title_for_question(title: str) -> str:
    t = re.sub(r"\s+", " ", title).strip()
    t = re.sub(r"\s*[:\-–—]\s*$", "", t)
    return t


def infer_questions(title: str, topics: list[str]) -> list[str]:
    clean_title = clean_title_for_question(title)
    topic_clause = topics[0] if topics else "this topic"
    return [
        f"What are the key ideas in {clean_title}?",
        f"How does this relate to {topic_clause.lower()} in production systems?",
    ]


def as_iso_date_or_empty(value: str) -> str:
    if not value:
        return ""
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return value
    return ""


def file_mtime_iso(path: Path) -> str:
    dt = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return dt.date().isoformat()


def post_url(slug: str) -> str:
    return f"{SITE_URL}/post.html?post={urllib.parse.quote(slug)}"


def load_posts(*, dedupe: bool = True) -> list[PostRecord]:
    candidates: list[PostRecord] = []
    for path_str in glob.glob(str(POSTS_DIR / "*.md")):
        path = Path(path_str)
        slug = path.stem
        if slug == "template":
            continue

        raw = path.read_text(encoding="utf-8")
        fm, body = parse_front_matter(raw)
        fm = fm or {}

        title = fm.get("title", slug.replace("-", " ").title())
        date_iso = as_iso_date_or_empty(fm.get("date", ""))
        summary = fm.get("summary", "").strip() or summarize_body(body)
        topics = split_csv(fm.get("topics", "")) or infer_topics(title, body)
        question_targets = split_csv(fm.get("questionTargets", "")) or infer_questions(title, topics)
        canonical_source = fm.get("canonical", "").strip() or post_url(slug)
        source = fm.get("source", "").strip().lower()
        medium_id = fm.get("mediumId", "").strip().lower()

        candidates.append(
            PostRecord(
                slug=slug,
                title=title,
                date_iso=date_iso,
                summary=summary,
                topics=topics,
                question_targets=question_targets,
                canonical_source=canonical_source,
                source=source,
                medium_id=medium_id,
                site_url=post_url(slug),
                body=body,
                mtime_iso=file_mtime_iso(path),
            )
        )

    out = candidates
    if dedupe:
        # Deduplicate when historical imports generated multiple slugs for the same canonical source.
        by_key: dict[str, PostRecord] = {}
        for post in candidates:
            key = post.canonical_source or post.slug
            current = by_key.get(key)
            if not current:
                by_key[key] = post
                continue

            def score(item: PostRecord) -> tuple[int, int, int]:
                return (
                    1 if item.medium_id else 0,
                    1 if item.source == "medium" else 0,
                    -len(item.slug),
                )

            if score(post) > score(current):
                by_key[key] = post
        out = list(by_key.values())

    def sort_key(p: PostRecord) -> tuple[str, str]:
        return (p.date_iso or "0000-00-00", p.title.lower())

    out.sort(key=sort_key, reverse=True)
    return out


def load_search_intent_sections() -> list[SearchIntentSection]:
    if not SEARCH_INTENT_ANSWERS_PATH.exists():
        raise SystemExit(f"Missing curated answers file: {SEARCH_INTENT_ANSWERS_PATH}")

    raw = json.loads(SEARCH_INTENT_ANSWERS_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SystemExit("search_intent_answers.json must be an object")

    sections_raw = raw.get("sections")
    if not isinstance(sections_raw, list) or not sections_raw:
        raise SystemExit("search_intent_answers.json must contain non-empty sections[]")

    required_item_fields = {
        "question",
        "answer",
        "primary_cta_label",
        "primary_cta_url",
        "secondary_cta_label",
        "secondary_cta_url",
        "evidence_links",
    }

    sections: list[SearchIntentSection] = []
    seen_questions: set[str] = set()
    for idx, section in enumerate(sections_raw):
        if not isinstance(section, dict):
            raise SystemExit(f"sections[{idx}] must be an object")

        section_id = str(section.get("id", "")).strip()
        title = str(section.get("title", "")).strip()
        intent_keywords_raw = section.get("intent_keywords", [])
        items_raw = section.get("items", [])

        if not section_id or not title:
            raise SystemExit(f"sections[{idx}] must include non-empty id and title")
        if not isinstance(intent_keywords_raw, list):
            raise SystemExit(f"sections[{idx}].intent_keywords must be an array")
        if not isinstance(items_raw, list) or not items_raw:
            raise SystemExit(f"sections[{idx}].items must be a non-empty array")

        intent_keywords = [str(v).strip() for v in intent_keywords_raw if str(v).strip()]
        items: list[SearchIntentAnswer] = []
        for jdx, item in enumerate(items_raw):
            if not isinstance(item, dict):
                raise SystemExit(f"sections[{idx}].items[{jdx}] must be an object")
            missing = [f for f in required_item_fields if f not in item]
            if missing:
                raise SystemExit(f"sections[{idx}].items[{jdx}] missing fields: {', '.join(missing)}")

            question = str(item.get("question", "")).strip()
            answer = str(item.get("answer", "")).strip()
            primary_cta_label = str(item.get("primary_cta_label", "")).strip()
            primary_cta_url = str(item.get("primary_cta_url", "")).strip()
            secondary_cta_label = str(item.get("secondary_cta_label", "")).strip()
            secondary_cta_url = str(item.get("secondary_cta_url", "")).strip()
            evidence_links_raw = item.get("evidence_links", [])

            if not all([question, answer, primary_cta_label, primary_cta_url, secondary_cta_label, secondary_cta_url]):
                raise SystemExit(f"sections[{idx}].items[{jdx}] has empty required values")
            if primary_cta_url not in ALLOWED_PRIMARY_CTA_URLS:
                raise SystemExit(
                    f"sections[{idx}].items[{jdx}].primary_cta_url must be one of: {', '.join(sorted(ALLOWED_PRIMARY_CTA_URLS))}"
                )
            if not isinstance(evidence_links_raw, list) or not evidence_links_raw:
                raise SystemExit(f"sections[{idx}].items[{jdx}].evidence_links must be a non-empty array")

            evidence_links = [str(v).strip() for v in evidence_links_raw if str(v).strip()]
            if not evidence_links:
                raise SystemExit(f"sections[{idx}].items[{jdx}].evidence_links cannot be empty")

            q_key = question.lower()
            if q_key in seen_questions:
                raise SystemExit(f"Duplicate question in curated answers: {question}")
            seen_questions.add(q_key)

            items.append(
                SearchIntentAnswer(
                    question=question,
                    answer=answer,
                    primary_cta_label=primary_cta_label,
                    primary_cta_url=primary_cta_url,
                    secondary_cta_label=secondary_cta_label,
                    secondary_cta_url=secondary_cta_url,
                    evidence_links=evidence_links,
                )
            )

        sections.append(
            SearchIntentSection(
                section_id=section_id,
                title=title,
                intent_keywords=intent_keywords,
                items=items,
            )
        )

    return sections


def flattened_search_answers(sections: list[SearchIntentSection]) -> list[SearchIntentAnswer]:
    out: list[SearchIntentAnswer] = []
    for section in sections:
        out.extend(section.items)
    return out


def write_discovery_json(posts: list[PostRecord]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "slug": p.slug,
            "title": p.title,
            "url": p.site_url,
            "date": p.date_iso,
            "summary": p.summary,
            "topics": p.topics,
            "canonical_source": p.canonical_source,
            "question_targets": p.question_targets,
        }
        for p in posts
    ]
    (DATA_DIR / "discovery_posts.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def unique_question_entries(posts: list[PostRecord], limit: int = 24) -> list[tuple[str, PostRecord]]:
    seen: set[str] = set()
    out: list[tuple[str, PostRecord]] = []
    for post in posts:
        for q in post.question_targets:
            key = q.strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append((q.strip(), post))
            if len(out) >= limit:
                return out
    return out


def question_anchor(question: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", question.lower()).strip("-")
    return value or "question"


def write_answers_txt(sections: list[SearchIntentSection]) -> None:
    entries = flattened_search_answers(sections)
    lines: list[str] = []
    lines.append(f"Title: {AUTHOR_NAME} Answers Index")
    lines.append(f"Canonical: {SITE_URL}/answers.html")
    lines.append("")
    for idx, item in enumerate(entries, start=1):
        lines.append(f"{idx}. Q: {item.question}")
        lines.append(f"   A: {item.answer}")
        lines.append(f"   Primary: {item.primary_cta_url}")
        lines.append(f"   Supporting: {item.secondary_cta_url}")
        lines.append(f"   URL: {SITE_URL}/answers.html#{question_anchor(item.question)}")
        lines.append("")
    (SITE_ROOT / "answers.txt").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_llms_txt(posts: list[PostRecord], sections: list[SearchIntentSection]) -> None:
    curated_entries = flattened_search_answers(sections)
    curated_entries = curated_entries[:12]
    latest = posts[:10]

    lines: list[str] = []
    lines.append(f"Title: {AUTHOR_NAME}")
    lines.append(
        "Description: Personal site featuring research, publications, and technical essays on AI systems, LLM agents, speech, retrieval, and production engineering."
    )
    lines.append(f"Canonical: {SITE_URL}/")
    lines.append("")

    lines.append("Expertise:")
    lines.append("- Agentic AI systems and orchestration")
    lines.append("- LLMs, RAG, and retrieval architecture")
    lines.append("- Speech and ASR reliability")
    lines.append("- Evaluation frameworks for conversational systems")
    lines.append("- Spec-driven software and AI engineering")
    lines.append("")

    lines.append("Best answers by question:")
    for item in curated_entries:
        lines.append(f"- Q: {item.question}")
        lines.append(f"  A: {item.answer}")
        lines.append(f"  URL: {SITE_URL}/answers.html#{question_anchor(item.question)}")

    if len(curated_entries) < 12:
        fallback = unique_question_entries(posts, limit=12 - len(curated_entries))
        for question, post in fallback:
            lines.append(f"- Q: {question}")
            lines.append(f"  A: {post.summary}")
            lines.append(f"  URL: {post.site_url}")
    lines.append("")

    lines.append("Latest updates:")
    for post in latest:
        label_date = post.date_iso or post.mtime_iso
        lines.append(f"- {label_date}: {post.title} -> {post.site_url}")
    lines.append("")

    lines.append("Citation-preferred URLs:")
    for post in latest:
        lines.append(f"- {post.title}: {post.site_url}")
    lines.append("")

    lines.append("Sections:")
    lines.append(f"- About: {SITE_URL}/index.html#about")
    lines.append(f"- Research: {SITE_URL}/research.html")
    lines.append(f"- Publications: {SITE_URL}/publications.html")
    lines.append(f"- Blog: {SITE_URL}/blogs.html")
    lines.append(f"- Question Answers: {SITE_URL}/answers.html")
    lines.append(f"- Social Posts: {SITE_URL}/sm_posts.html")
    lines.append("")

    lines.append("Contact:")
    lines.append("- Email: mailto:prdeepak.babu@gmail.com")
    lines.append("- LinkedIn: https://www.linkedin.com/in/prdeepak")
    lines.append("- Google Scholar: https://scholar.google.com/citations?user=jBtBPqcAAAAJ&hl=en")
    lines.append("")

    lines.append("Social:")
    lines.append("- X: https://x.com/prdeepakbabu")
    lines.append("- Medium: https://medium.com/@prdeepak.babu")

    (SITE_ROOT / "llms.txt").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def answers_page_markup(sections: list[SearchIntentSection]) -> str:
    faq_entities: list[dict[str, object]] = []
    section_chunks: list[str] = []

    for section in sections:
        card_chunks: list[str] = []
        keyword_text = ", ".join(section.intent_keywords)
        for item in section.items:
            faq_entities.append(
                {
                    "@type": "Question",
                    "name": item.question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item.answer,
                    },
                }
            )

            evidence = "".join(
                [
                    (
                        f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">'
                        f"{html.escape(url)}</a></li>"
                    )
                    for url in item.evidence_links
                ]
            )
            card_chunks.append(
                "\n".join(
                    [
                        f'      <article class="qa-card" id="{html.escape(question_anchor(item.question))}">',
                        f"        <h3>{html.escape(item.question)}</h3>",
                        f"        <p>{html.escape(item.answer)}</p>",
                        '        <div class="qa-cta-row">',
                        (
                            f'          <a class="qa-cta qa-cta-primary" href="{html.escape(item.primary_cta_url)}">'
                            f"{html.escape(item.primary_cta_label)}</a>"
                        ),
                        (
                            f'          <a class="qa-cta qa-cta-secondary" href="{html.escape(item.secondary_cta_url)}">'
                            f"{html.escape(item.secondary_cta_label)}</a>"
                        ),
                        "        </div>",
                        "        <details>",
                        "          <summary>Evidence links</summary>",
                        f"          <ul>{evidence}</ul>",
                        "        </details>",
                        "      </article>",
                    ]
                )
            )

        section_chunks.append(
            "\n".join(
                [
                    f'    <section class="qa-section" id="{html.escape(section.section_id)}">',
                    f"      <h2>{html.escape(section.title)}</h2>",
                    f'      <p class="intent-keywords"><strong>Popular searches:</strong> {html.escape(keyword_text)}</p>',
                    '      <div class="qa-grid">',
                    "\n".join(card_chunks),
                    "      </div>",
                    "    </section>",
                ]
            )
        )

    faq_payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_entities,
    }
    faq_json = json.dumps(faq_payload, ensure_ascii=False, indent=2)
    sections_html = "\n".join(section_chunks)

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src=\"https://www.googletagmanager.com/gtag/js?id=G-XNWLG8DBTN\"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-XNWLG8DBTN');
  </script>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>AI Leadership Answers | {AUTHOR_NAME}</title>
  <meta name=\"description\" content=\"High-intent questions on principal AI scientist expertise in agentic AI, speech, NLP/NLU/NLG, and selective research collaboration.\">
  <link rel=\"canonical\" href=\"{SITE_URL}/answers.html\">
  <meta property=\"og:title\" content=\"AI Leadership Answers | {AUTHOR_NAME}\">
  <meta property=\"og:description\" content=\"Curated question-and-answer guide for agentic AI, speech and NLP leadership, and collaboration fit.\">
  <meta property=\"og:type\" content=\"website\">
  <meta property=\"og:url\" content=\"{SITE_URL}/answers.html\">
  <meta property=\"og:image\" content=\"{SITE_URL}/1DC549B4-26BA-4564-8BCA-40CBFABB7AC8.jpeg\">
  <meta name=\"twitter:card\" content=\"summary_large_image\">
  <meta name=\"twitter:title\" content=\"AI Leadership Answers | {AUTHOR_NAME}\">
  <meta name=\"twitter:description\" content=\"Curated question-and-answer guide for agentic AI, speech and NLP leadership, and collaboration fit.\">
  <meta name=\"twitter:image\" content=\"{SITE_URL}/1DC549B4-26BA-4564-8BCA-40CBFABB7AC8.jpeg\">
  <script type=\"application/ld+json\">
{faq_json}
  </script>
  <link rel=\"stylesheet\" href=\"styles.css\">
  <style>
    main {{
      max-width: 980px;
      margin: 0 auto 60px;
      padding: 0 20px;
    }}
    .hero {{
      background: var(--card);
      border: 3px solid var(--border);
      box-shadow: var(--shadow);
      border-radius: var(--radius);
      padding: 20px;
      margin-bottom: 18px;
    }}
    .hero p {{
      margin-bottom: 10px;
    }}
    .collab-note {{
      background: var(--subtle);
      border: 2px solid var(--border);
      padding: 12px;
      font-size: 0.95rem;
    }}
    .qa-section {{
      margin-bottom: 22px;
    }}
    .intent-keywords {{
      color: var(--muted);
      margin-bottom: 12px;
      font-size: 0.95rem;
    }}
    .qa-grid {{
      display: grid;
      gap: 16px;
    }}
    .qa-card {{
      background: var(--card);
      border: 3px solid var(--border);
      box-shadow: var(--shadow);
      border-radius: var(--radius);
      padding: 18px;
    }}
    .qa-card h3 {{
      margin: 0 0 10px;
      font-size: 1.2rem;
    }}
    .qa-card p {{
      margin: 0 0 10px;
      color: var(--muted);
    }}
    .qa-cta-row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin: 12px 0;
    }}
    .qa-cta {{
      text-decoration: none;
      font-weight: 900;
      border: 2px solid var(--border);
      padding: 8px 12px;
      color: var(--ink);
      box-shadow: var(--shadow-sm);
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }}
    .qa-cta-primary {{
      background: var(--accent);
    }}
    .qa-cta-secondary {{
      background: var(--card);
    }}
    .qa-cta:hover {{
      background: var(--accent);
    }}
    details summary {{
      cursor: pointer;
      font-weight: 800;
    }}
    details ul {{
      margin: 8px 0 0 16px;
      padding: 0;
    }}
  </style>
</head>
<body>
  <div class=\"ambient-bg\" aria-hidden=\"true\"></div>
  <header>
    <h1>AI Leadership Answers</h1>
    <p>Curated answers for people searching principal-level expertise in agentic AI, speech, and NLP/NLU/NLG.</p>
  </header>

  <nav>
    <a href=\"index.html\">About</a>
    <a href=\"research.html\">Research</a>
    <a href=\"publications.html\">Publications</a>
    <a href=\"awards.html\">Awards</a>
    <a href=\"blogs.html\">Blog</a>
    <a href=\"projects.html\">My Works</a>
    <a href=\"resources.html\">Resources</a>
    <a href=\"contact.html\">Contact</a>
  </nav>

  <main>
    <section class=\"hero\">
      <p><strong>Positioning:</strong> Principal AI Scientist focused on agentic AI architecture, speech systems, and language technologies from research to production.</p>
      <p class=\"collab-note\"><strong>Collaboration:</strong> Selective but open to high-signal collaborations in agentic AI, ASR/NLP, evaluation frameworks, and research-to-production system design.</p>
    </section>
{sections_html}
    <section class=\"hero\">
      <p><strong>Where to start:</strong> Use profile links for background, featured work for quick signal, and contact for scoped collaboration outreach.</p>
    </section>
  </main>
</body>
</html>
"""


def write_answers_html(sections: list[SearchIntentSection]) -> None:
    (SITE_ROOT / "answers.html").write_text(answers_page_markup(sections), encoding="utf-8")


def xml_escape(s: str) -> str:
    return html.escape(s, quote=True)


def write_sitemap(posts: list[PostRecord]) -> None:
    static_pages = [
        ("/", "weekly", "1.0", "index.html"),
        ("/research.html", "monthly", "0.9", "research.html"),
        ("/publications.html", "weekly", "0.9", "publications.html"),
        ("/awards.html", "monthly", "0.7", "awards.html"),
        ("/blogs.html", "weekly", "0.9", "blogs.html"),
        ("/answers.html", "weekly", "0.8", "answers.html"),
        ("/sm_posts.html", "weekly", "0.8", "sm_posts.html"),
        ("/paperreviews.html", "monthly", "0.7", "paperreviews.html"),
        ("/projects.html", "monthly", "0.7", "projects.html"),
        ("/resources.html", "monthly", "0.7", "resources.html"),
        ("/contact.html", "monthly", "0.6", "contact.html"),
    ]

    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    for path_url, changefreq, priority, local_file in static_pages:
        abs_url = f"{SITE_URL}{path_url}"
        local_path = SITE_ROOT / local_file
        lastmod = file_mtime_iso(local_path) if local_path.exists() else datetime.now(tz=timezone.utc).date().isoformat()
        lines.extend(
            [
                "  <url>",
                f"    <loc>{xml_escape(abs_url)}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                f"    <changefreq>{changefreq}</changefreq>",
                f"    <priority>{priority}</priority>",
                "  </url>",
            ]
        )

    for post in posts:
        lastmod = post.date_iso or post.mtime_iso
        lines.extend(
            [
                "  <url>",
                f"    <loc>{xml_escape(post.site_url)}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                "    <changefreq>monthly</changefreq>",
                "    <priority>0.7</priority>",
                "  </url>",
                "  <url>",
                f"    <loc>{xml_escape(f'{SITE_URL}/posts/{urllib.parse.quote(post.slug)}.md')}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                "    <changefreq>monthly</changefreq>",
                "    <priority>0.5</priority>",
                "  </url>",
            ]
        )

    lines.append("</urlset>")
    (SITE_ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    posts = load_posts(dedupe=True)
    all_posts = load_posts(dedupe=False)
    search_intent_sections = load_search_intent_sections()
    write_discovery_json(posts)
    write_answers_txt(search_intent_sections)
    write_llms_txt(posts, search_intent_sections)
    write_answers_html(search_intent_sections)
    write_sitemap(all_posts)
    qa_count = len(flattened_search_answers(search_intent_sections))
    print(
        f"Generated discovery assets for {len(posts)} deduplicated posts ({len(all_posts)} total markdown posts) "
        f"and {qa_count} curated Q/A items"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
