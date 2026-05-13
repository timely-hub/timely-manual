#!/usr/bin/env python3
"""
One-off cleanup pass over docs/*.md.

Fixes two recurring quality issues left by the Notion converter:

  1. Admonition titles that are just an emoji (e.g. `!!! note "❓"`). MkDocs Material
     renders these as a giant emoji header with no context. Drop the title so the
     admonition uses its default kind label.

  2. Image alt-text that is actually just a filename (e.g. `image.png`,
     `Group 427319669.png`, `대화기록예시.png`). These are useless to screen readers
     and confusing in the rendered page. Strip to empty alt so the image is treated
     as decorative.

Run:
    python3 scripts/cleanup-docs.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Same balanced-bracket regex as convert-notion.py
LINK_RE = re.compile(
    r"(?P<bang>!?)"
    r"\[(?P<alt>(?:[^\[\]]|\[[^\[\]]*\])*)\]"
    r"\((?P<url>(?:[^()\s]|\([^()]*\))+(?:\s+\"[^\"]*\")?)\)"
)

# Admonition / details with quoted title. Captures the inline title.
ADMONITION_TITLE_RE = re.compile(
    r'^(?P<lead>\s*(?:!!!|\?\?\?\+?)\s+\S+)\s+"(?P<title>[^"\n]+)"\s*$',
    re.MULTILINE,
)

# A title is "empty-ish" if after stripping symbols/whitespace nothing meaningful remains.
# We treat alphanumerics (Latin and Hangul/CJK ranges) as meaningful content.
MEANINGFUL_CHARS_RE = re.compile(
    r"[A-Za-z0-9가-힣ㄱ-ㅎㅏ-ㅣ一-龥]"
)

# A junk image-alt is anything that ends with a media file extension. Real alt prose
# never ends with .png/.jpg/.jpeg/.gif/.svg/.webp/.bmp.
JUNK_ALT_RE = re.compile(r"\.(?:png|jpe?g|gif|svg|webp|bmp)\s*$", re.IGNORECASE)

def title_is_emoji_only(title: str) -> bool:
    """True if the title has no Latin/Hangul/CJK characters worth keeping."""
    return MEANINGFUL_CHARS_RE.search(title) is None

def clean_admonition_titles(text: str) -> tuple[str, int]:
    changes = 0

    def replace(m: re.Match) -> str:
        nonlocal changes
        title = m.group("title").strip()
        if title_is_emoji_only(title):
            changes += 1
            return m.group("lead")
        return m.group(0)

    return ADMONITION_TITLE_RE.sub(replace, text), changes

def clean_image_alts(text: str) -> tuple[str, int]:
    changes = 0

    def replace(m: re.Match) -> str:
        nonlocal changes
        is_image = m.group("bang") == "!"
        if not is_image:
            return m.group(0)
        alt = m.group("alt")
        url = m.group("url")
        if alt and JUNK_ALT_RE.search(alt):
            changes += 1
            return f"![]({url})"
        return m.group(0)

    return LINK_RE.sub(replace, text), changes

def process(path: Path) -> tuple[int, int]:
    raw = path.read_text(encoding="utf-8")
    body, n_titles = clean_admonition_titles(raw)
    body, n_alts = clean_image_alts(body)
    if body != raw:
        path.write_text(body, encoding="utf-8")
    return n_titles, n_alts

def main() -> int:
    if not DOCS.exists():
        print(f"no docs/ found at {DOCS}", file=sys.stderr)
        return 1

    total_titles = 0
    total_alts = 0
    files_touched = 0
    for md in sorted(DOCS.rglob("*.md")):
        n_titles, n_alts = process(md)
        if n_titles or n_alts:
            files_touched += 1
            print(f"  {md.relative_to(ROOT)}: titles -{n_titles}, alts -{n_alts}")
            total_titles += n_titles
            total_alts += n_alts

    print()
    print(f"Touched {files_touched} files.  "
          f"Stripped {total_titles} emoji-only admonition titles, "
          f"{total_alts} filename-only image alts.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
