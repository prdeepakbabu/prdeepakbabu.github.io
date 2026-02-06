#!/usr/bin/env python3
"""Rebuild the homepage highlights block from data/homepage_highlights.json."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "homepage_highlights.json"
INDEX_PATH = ROOT / "index.html"
START_MARKER = "<!-- HOMEPAGE_HIGHLIGHTS:START -->"
END_MARKER = "<!-- HOMEPAGE_HIGHLIGHTS:END -->"


def load_data(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    highlights = payload.get("highlights")
    if not isinstance(highlights, list) or not highlights:
        raise SystemExit("homepage_highlights.json must contain a non-empty 'highlights' array")

    required_fields = {"id", "value", "label", "href"}
    normalized: list[dict[str, str]] = []
    for idx, item in enumerate(highlights, start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"highlights[{idx}] must be an object")

        missing = required_fields - item.keys()
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise SystemExit(f"highlights[{idx}] is missing required fields: {missing_fields}")

        normalized_item: dict[str, str] = {}
        for key in ("id", "value", "label", "href", "ariaLabel"):
            value = item.get(key, "")
            if value is None:
                value = ""
            normalized_item[key] = str(value).strip()

        normalized.append(normalized_item)

    return normalized


def render_cards(items: list[dict[str, str]]) -> str:
    lines = ['        <div class="highlights-grid">']
    for item in items:
        item_id = html.escape(item["id"])
        value = html.escape(item["value"])
        label = html.escape(item["label"])
        href = html.escape(item["href"])
        aria_label = html.escape(item.get("ariaLabel") or item["label"])

        lines.extend(
            [
                f'          <a class="highlight-card" href="{href}" aria-label="{aria_label}" data-analytics-event="home_highlight_click" data-analytics-label="{item_id}">',
                f'            <span class="highlight-value">{value}</span>',
                f'            <span class="highlight-label">{label}</span>',
                "          </a>",
            ]
        )

    lines.append("        </div>")
    return "\n".join(lines)


def update_index(cards_html: str) -> None:
    raw = INDEX_PATH.read_text(encoding="utf-8")
    start = raw.find(START_MARKER)
    end = raw.find(END_MARKER)
    if start == -1 or end == -1:
        raise SystemExit("index.html is missing homepage highlight markers")
    if start >= end:
        raise SystemExit("Invalid marker order in index.html")

    start_block_end = start + len(START_MARKER)
    updated = raw[:start_block_end] + "\n" + cards_html + "\n        " + raw[end:]
    INDEX_PATH.write_text(updated, encoding="utf-8")


def main() -> int:
    highlights = load_data(DATA_PATH)
    cards_html = render_cards(highlights)
    update_index(cards_html)
    print(f"Updated {INDEX_PATH.name} from {DATA_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
