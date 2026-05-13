#!/usr/bin/env python3
"""
Compact empty-bodied admonitions left by the Notion converter.

Notion `<aside>` blocks that have only an emoji + heading and no body were
converted to:

    !!! tip "최초 로그인 시, 회원가입을 먼저 진행해주세요"

        &nbsp;

The `&nbsp;` placeholder existed so mkdocs-material would recognize the
admonition syntax — without it the title-only line would be ignored. But it
renders as a tall empty box, which misrepresents the original intent (which
was a single-line hint callout).

This pass replaces those with a compact blockquote that includes the emoji
that signalled the kind in the original Notion aside:

    > 💡 **최초 로그인 시, 회원가입을 먼저 진행해주세요**

Run:
    python3 scripts/compact-empty-admonitions.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Reverse of the emoji → kind mapping used by convert-notion.py.
# When we collapse an empty admonition we surface this emoji as the prefix.
KIND_TO_EMOJI: dict[str, str] = {
    "note":    "📌",
    "tip":     "💡",
    "success": "✅",
    "warning": "⚠️",
    "info":    "👇",
    "danger":  "🚨",
    "question": "❓",
}

# Match an admonition whose only body is `    &nbsp;` (a single indented line).
# Captures: kind, title, the body line so we can replace the whole block.
EMPTY_ADMONITION_RE = re.compile(
    r'^(?P<indent>\s*)!!!\s+(?P<kind>\S+)\s+"(?P<title>[^"\n]+)"\s*\n'
    r'(?:\s*\n)+'                       # one or more blank lines
    r'(?P=indent)    &nbsp;\s*\n',
    re.MULTILINE,
)

def compact(text: str) -> tuple[str, int]:
    count = 0

    def replace(m: re.Match) -> str:
        nonlocal count
        kind = m.group("kind").lower()
        title = m.group("title").strip()
        indent = m.group("indent")
        emoji = KIND_TO_EMOJI.get(kind, "💡")
        count += 1
        return f"{indent}> {emoji} **{title}**\n"

    return EMPTY_ADMONITION_RE.sub(replace, text), count

def main() -> int:
    if not DOCS.exists():
        print(f"no docs/ found at {DOCS}", file=sys.stderr)
        return 1

    total = 0
    touched = 0
    for md in sorted(DOCS.rglob("*.md")):
        raw = md.read_text(encoding="utf-8")
        new, n = compact(raw)
        if n:
            md.write_text(new, encoding="utf-8")
            touched += 1
            total += n
            print(f"  {md.relative_to(ROOT)}: -{n}")

    print()
    print(f"Compacted {total} empty admonitions across {touched} files.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
