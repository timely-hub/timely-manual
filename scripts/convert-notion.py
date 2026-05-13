#!/usr/bin/env python3
"""
Convert the Notion export under existing-guide/ into the docs/ tree for MkDocs.

This is a one-shot script. Once converted MD lives in docs/, content authoring
happens there directly. Re-running this script will OVERWRITE files under docs/
(except docs/index.md is replaced too — back up first if hand-edited).

Run:
    python3 scripts/convert-notion.py

What it does
------------
1. Walks existing-guide/, finds the 22 sub-page MDs + the root MD.
2. Maps each Notion .md → a clean slug path under docs/.
3. Copies each page's images into docs/assets/images/<page-slug>/imgNN.<ext>,
   renumbering them so we don't keep Notion's url-encoded hangul-jamo names.
4. Rewrites the markdown body:
   - <aside>...</aside> blocks → MkDocs admonitions, emoji → admonition kind.
   - FAQ "- 질문\n    본문" toggle pattern → ??? question "..." details.
   - Internal links (with notion id hash) → new slug paths.
   - Image src paths → new docs/assets/images/... paths.
5. Splits the root index into multiple top-level pages (tutorials/faq/app/...).
"""
from __future__ import annotations

import os
import re
import shutil
import unicodedata
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

def nfc(s: str) -> str:
    """macOS APFS stores Korean filenames as NFD; normalize for comparison."""
    return unicodedata.normalize("NFC", s)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "existing-guide" / "타임리GPT 서비스 사용 가이드"
SRC_ROOT_MD = ROOT / "existing-guide" / "타임리GPT 서비스 사용 가이드 272f49d7e77e80d7805fcfa1e3be7983.md"
OUT = ROOT / "docs"
IMG_OUT_BASE = OUT / "assets" / "images"

# -------------------------------------------------------------------------
# 1. Slug registry — keyed by Notion ID hash so internal links resolve.
# -------------------------------------------------------------------------

@dataclass
class PageEntry:
    notion_id: str            # e.g. "272f49d7e77e818ab03bd3572ecd180c"
    src_md: Path              # absolute path to source .md
    img_folder: Path | None   # absolute path to source image folder (or None)
    out_path: Path            # absolute path to dest .md under docs/
    slug: str                 # slug used for image dir naming

    @property
    def out_rel(self) -> str:
        """Path of output relative to docs/ (e.g. 'admin/getting-started/...md')."""
        return str(self.out_path.relative_to(OUT))

# Mapping: source MD filename stem (without trailing space + hash) → (rel_out, slug)
# All source files live directly under SRC.
PAGES: dict[str, tuple[str, str]] = {
    # admin getting-started
    "시작하기 스페이스 설정":     ("admin/getting-started/space-setup.md",  "admin-space-setup"),
    "유저 초대 관리":             ("admin/getting-started/invite-users.md", "admin-invite-users"),
    "템플릿 관리":                ("admin/getting-started/templates.md",    "admin-templates"),
    "크레딧 결제":                ("admin/getting-started/credits.md",      "admin-credits"),

    # user getting-started
    "시작하기":                   ("user/getting-started/overview.md",      "user-overview"),
    "서비스 활용하기":            ("user/getting-started/services.md",      "user-services"),
    "템플릿 더 알아보기":         ("user/getting-started/templates.md",     "user-templates"),
    "Labs 더 알아보기":           ("user/getting-started/labs.md",          "user-labs"),
    "내 계정 설정하기":           ("user/getting-started/my-account.md",    "user-my-account"),

    # extras (linked from root)
    "할루시네이션을 줄이는 방법을 알고싶어요": ("hallucination.md", "hallucination"),
}

# Subfolder pages — Notion "database" pages, stored under SRC/ㅤ/ and SRC/ㅤ 272f-5429/.
ADMIN_REF = "ㅤ"
USER_REF = "ㅤ 272f-5429"

SUBFOLDER_PAGES: dict[tuple[str, str], tuple[str, str]] = {
    # (subfolder_name, page_stem) → (rel_out, slug)
    (ADMIN_REF, "회원가입 및 로그인"):  ("admin/reference/signup-login.md",         "admin-signup-login"),
    (ADMIN_REF, "유저 관리"):           ("admin/reference/user-management.md",      "admin-user-management"),
    (ADMIN_REF, "템플릿 관리"):         ("admin/reference/template-management.md",  "admin-template-management"),
    (ADMIN_REF, "스페이스 관리"):       ("admin/reference/space-management.md",     "admin-space-management"),
    (ADMIN_REF, "크레딧 결제"):         ("admin/reference/credits.md",              "admin-ref-credits"),
    (ADMIN_REF, "통계"):                ("admin/reference/stats.md",                "admin-stats"),

    (USER_REF, "워크스페이스 만들기"):  ("user/reference/workspaces.md",            "user-workspaces"),
    (USER_REF, "다양한 LLM 채팅"):       ("user/reference/llm-chat.md",              "user-llm-chat"),
    (USER_REF, "권한"):                  ("user/reference/permissions.md",           "user-permissions"),
    (USER_REF, "계정 관리"):             ("user/reference/account.md",               "user-account"),
    (USER_REF, "템플릿 만들기"):         ("user/reference/templates-build.md",       "user-templates-build"),
    (USER_REF, "타임리 AI 에이전트"):    ("user/reference/ai-agents.md",             "user-ai-agents"),
}

ROOT_NOTION_ID = "272f49d7e77e80d7805fcfa1e3be7983"

# -------------------------------------------------------------------------
# 2. Aside → admonition mapping
# -------------------------------------------------------------------------

EMOJI_TO_ADMONITION: list[tuple[str, str]] = [
    ("📌", "note"),
    ("💡", "tip"),
    ("✅", "success"),
    ("🚫", "warning"),
    ("⚠️", "warning"),
    ("👇", "info"),
    ("🚨", "danger"),
    ("🔥", "warning"),
    ("🏡", "info"),
    ("🟢", "success"),
    ("🟡", "warning"),
    ("🔴", "danger"),
    ("ℹ️", "info"),
]

ADMONITION_DEFAULT = "note"

def detect_admonition_kind(body: str) -> tuple[str, str]:
    """Return (admonition_kind, body_with_emoji_stripped)."""
    stripped = body.lstrip()
    for emoji, kind in EMOJI_TO_ADMONITION:
        if stripped.startswith(emoji):
            return kind, stripped[len(emoji):].lstrip()
    return ADMONITION_DEFAULT, body

# -------------------------------------------------------------------------
# 3. Helpers — discovery, image collection
# -------------------------------------------------------------------------

NOTION_ID_RE = re.compile(r"\s+([0-9a-f]{32})(?:\.md|$)")

def discover_entries() -> tuple[PageEntry, dict[str, PageEntry]]:
    """Return (root_entry, by_notion_id) for every page."""
    by_id: dict[str, PageEntry] = {}

    # Root index
    root_match = NOTION_ID_RE.search(str(SRC_ROOT_MD))
    assert root_match, f"Couldn't find notion id in {SRC_ROOT_MD}"
    root_entry = PageEntry(
        notion_id=root_match.group(1),
        src_md=SRC_ROOT_MD,
        img_folder=SRC,            # root images live alongside sub-pages in SRC/
        out_path=OUT / "index.md",
        slug="home",
    )
    by_id[root_entry.notion_id] = root_entry

    # Index all .md files under SRC, keyed by their NFC stem (filename without " <hash>.md").
    def index_dir(d: Path) -> dict[str, Path]:
        index: dict[str, Path] = {}
        for p in d.glob("*.md"):
            m = NOTION_ID_RE.search(p.name)
            if not m:
                continue
            stem = nfc(p.name[: m.start()])
            index[stem] = p
        return index

    def index_subdirs(parent: Path) -> dict[str, Path]:
        index: dict[str, Path] = {}
        for p in parent.iterdir():
            if p.is_dir():
                # Normalize Korean folder name for comparison
                index[nfc(p.name)] = p
        return index

    top_pages = index_dir(SRC)
    sub_dirs = index_subdirs(SRC)

    # Top-level pages
    for stem, (rel_out, slug) in PAGES.items():
        src_md = top_pages.get(nfc(stem))
        if src_md is None:
            print(f"  ! missing source MD for: {stem}")
            continue
        m = NOTION_ID_RE.search(src_md.name)
        if not m:
            continue
        nid = m.group(1)
        img_folder_path = SRC / src_md.name[: m.start()]   # use raw, on-disk encoding
        img_folder = img_folder_path if img_folder_path.exists() else None
        entry = PageEntry(
            notion_id=nid,
            src_md=src_md,
            img_folder=img_folder,
            out_path=OUT / rel_out,
            slug=slug,
        )
        by_id[nid] = entry

    # Subfolder pages
    for (subfolder, stem), (rel_out, slug) in SUBFOLDER_PAGES.items():
        subdir = sub_dirs.get(nfc(subfolder))
        if subdir is None:
            print(f"  ! missing subfolder: {subfolder}")
            continue
        pages_in_sub = index_dir(subdir)
        src_md = pages_in_sub.get(nfc(stem))
        if src_md is None:
            print(f"  ! missing source MD: {subfolder}/{stem}")
            continue
        m = NOTION_ID_RE.search(src_md.name)
        if not m:
            continue
        nid = m.group(1)
        img_folder_path = subdir / src_md.name[: m.start()]
        img_folder = img_folder_path if img_folder_path.exists() else None
        entry = PageEntry(
            notion_id=nid,
            src_md=src_md,
            img_folder=img_folder,
            out_path=OUT / rel_out,
            slug=slug,
        )
        by_id[nid] = entry

    return root_entry, by_id

# -------------------------------------------------------------------------
# 4. Markdown content rewrites
# -------------------------------------------------------------------------

ASIDE_RE = re.compile(r"<aside>(.*?)</aside>", re.DOTALL)
# Markdown link regex that allows one level of balanced [...] inside alt
# (Notion exports nested brackets, e.g. "![alt with [keyword] inside](url)")
# and one level of balanced (...) inside URL (e.g. "...(단위선택)_Default.png").
LINK_RE = re.compile(
    r"(?P<bang>!?)"
    r"\[(?P<alt>(?:[^\[\]]|\[[^\[\]]*\])*)\]"
    r"\((?P<url>(?:[^()\s]|\([^()]*\))+(?:\s+\"[^\"]*\")?)\)"
)
NOTION_HASH_IN_PATH_RE = re.compile(r"([0-9a-f]{32})")

def url_decode(s: str) -> str:
    return urllib.parse.unquote(s)

def remap_aside(match: re.Match) -> str:
    raw = match.group(1).strip()
    # Drop image-tag asides (`<aside><img ../> ...`) into a plain blockquote.
    if raw.startswith("<img"):
        # extract any [text](url) inside; if multiple, keep as bullet list
        inner = re.sub(r"<img[^>]*/?>", "", raw).strip()
        return inner

    kind, body = detect_admonition_kind(raw)

    # Take the first non-blank line as title (if it looks short); rest as content.
    lines = [ln.rstrip() for ln in body.split("\n")]
    nonblank = [i for i, ln in enumerate(lines) if ln.strip()]
    if not nonblank:
        return ""
    first = lines[nonblank[0]].strip()
    rest = "\n".join(lines[nonblank[0] + 1:]).strip()

    # If `first` looks like a Notion heading "### ...", strip the hashes for title.
    title_match = re.match(r"^#{1,6}\s+(.+)$", first)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title = first

    title = title.replace('"', "'").strip()
    if not rest:
        return f'!!! {kind} "{title}"\n\n    &nbsp;\n'

    # Indent body lines by 4 spaces (admonition convention).
    indented = "\n".join("    " + ln if ln.strip() else "" for ln in rest.split("\n"))
    return f'!!! {kind} "{title}"\n\n{indented}\n'

def convert_asides(text: str) -> str:
    return ASIDE_RE.sub(remap_aside, text)

def convert_faq_toggles(text: str) -> str:
    """Convert Notion toggle pattern in FAQ-style lists.

    Pattern:
        - 질문 텍스트

            본문 ...
            본문 ...

    Becomes:
        ??? question "질문 텍스트"

            본문 ...
    """
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^- (.+?)\s*$", line)
        if m:
            # Look ahead: is there an indented continuation block?
            j = i + 1
            # skip a single blank line that Notion likes to leave
            if j < len(lines) and lines[j].strip() == "":
                j += 1
            # collect lines indented with 4+ spaces or tab
            body: list[str] = []
            while j < len(lines) and (lines[j].startswith("    ") or lines[j].startswith("\t") or lines[j].strip() == ""):
                # Stop if we hit a non-indented next list item (already left the block)
                if lines[j].strip() == "" and j + 1 < len(lines) and not (lines[j+1].startswith("    ") or lines[j+1].startswith("\t")):
                    break
                body.append(lines[j])
                j += 1
            if body and any(b.strip() for b in body):
                title = m.group(1).replace('"', "'").strip()
                out.append(f'??? question "{title}"')
                out.append("")
                # Body is already 4-space-indented in the source; keep that indentation
                for b in body:
                    out.append(b)
                # Trim trailing blanks
                while out and out[-1].strip() == "":
                    out.pop()
                out.append("")
                i = j
                continue
        out.append(line)
        i += 1
    return "\n".join(out)

def relpath_to_docs(from_md: Path, target_md: Path) -> str:
    """Posix relative path from `from_md` to `target_md` (both under docs/)."""
    rel = os.path.relpath(target_md, start=from_md.parent)
    return Path(rel).as_posix()

def relpath_to_image(from_md: Path, image_abs: Path) -> str:
    rel = os.path.relpath(image_abs, start=from_md.parent)
    return Path(rel).as_posix()

# -------------------------------------------------------------------------
# 5. Per-page image copy + URL rewrite
# -------------------------------------------------------------------------

def page_image_dir(entry: PageEntry) -> Path:
    return IMG_OUT_BASE / entry.slug

def copy_and_remap_images(entry: PageEntry, body: str) -> tuple[str, int]:
    """Rewrite `![](...)` image links in `body`. Returns (new_body, num_images)."""
    if entry.img_folder is None:
        return body, 0

    page_img_dir = page_image_dir(entry)
    page_img_dir.mkdir(parents=True, exist_ok=True)

    counter = [0]
    seen: dict[str, str] = {}  # original_url → new_relative_path

    def replace(m: re.Match) -> str:
        is_image = m.group("bang") == "!"
        alt = m.group("alt")
        raw_url = m.group("url")
        if not is_image:
            return m.group(0)

        # Skip absolute URLs
        if raw_url.startswith(("http://", "https://")):
            return m.group(0)

        decoded = url_decode(raw_url)
        if decoded in seen:
            return f"![{alt}]({seen[decoded]})"

        # Image lives under img_folder (or, for root, anywhere under SRC).
        # The decoded path is relative to the MD file's directory.
        src_md_dir = entry.src_md.parent
        candidate = (src_md_dir / decoded).resolve()
        if not candidate.exists():
            # Sometimes Notion encodes percent-encoded paths nested deeper; try basename-fallback
            bn = Path(decoded).name
            # search recursively in img_folder
            matches = list(entry.img_folder.rglob(bn)) if entry.img_folder else []
            if matches:
                candidate = matches[0]
            else:
                print(f"  ! image not found, leaving link: {decoded} (in {entry.src_md.name})")
                return m.group(0)

        # Decide new filename: sequential to avoid encoding mess.
        counter[0] += 1
        ext = candidate.suffix.lower() or ".png"
        new_name = f"img{counter[0]:02d}{ext}"
        new_abs = page_img_dir / new_name
        if not new_abs.exists():
            shutil.copy2(candidate, new_abs)
        new_rel = relpath_to_image(entry.out_path, new_abs)
        seen[decoded] = new_rel
        return f"![{alt}]({new_rel})"

    new_body = LINK_RE.sub(replace, body)
    return new_body, counter[0]

# -------------------------------------------------------------------------
# 6. Internal link rewriting
# -------------------------------------------------------------------------

def remap_internal_links(entry: PageEntry, body: str, by_id: dict[str, PageEntry]) -> tuple[str, int]:
    misses = [0]
    hits = [0]

    def replace(m: re.Match) -> str:
        is_image = m.group("bang") == "!"
        if is_image:
            return m.group(0)
        text = m.group("alt")
        raw_url = m.group("url")
        if raw_url.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        # Try to extract Notion ID from URL
        id_match = NOTION_HASH_IN_PATH_RE.search(raw_url)
        if not id_match:
            return m.group(0)
        nid = id_match.group(1)
        target = by_id.get(nid)
        if target is None:
            # CSV "database" pages — these are nav-only, will be replaced by index pages later.
            # For now, drop the link to plain text.
            misses[0] += 1
            return text
        rel = relpath_to_docs(entry.out_path, target.out_path)
        hits[0] += 1
        return f"[{text}]({rel})"

    new_body = LINK_RE.sub(replace, body)
    return new_body, hits[0]

# -------------------------------------------------------------------------
# 7. Per-page conversion
# -------------------------------------------------------------------------

def write_page(entry: PageEntry, by_id: dict[str, PageEntry]) -> None:
    raw = entry.src_md.read_text(encoding="utf-8")

    # Order matters: process asides BEFORE link-remap so we don't touch things inside asides twice.
    body, img_count = copy_and_remap_images(entry, raw)
    body, link_count = remap_internal_links(entry, body, by_id)
    body = convert_asides(body)
    body = convert_faq_toggles(body)

    entry.out_path.parent.mkdir(parents=True, exist_ok=True)
    entry.out_path.write_text(body, encoding="utf-8")
    print(f"  ✓ {entry.out_rel}  (imgs: {img_count}, links: {link_count})")

# -------------------------------------------------------------------------
# 8. Root index handling — split into multiple pages
# -------------------------------------------------------------------------

# We won't try to fully programmatically split the root index because its
# structure is very Notion-specific.  Instead we:
#   - convert it as-is into docs/index.md (with all the rewrites above),
#   - then leave manual structural cleanup as a follow-up pass.
#
# This keeps the script robust; nav-tree will determine final page order.

# -------------------------------------------------------------------------
# main
# -------------------------------------------------------------------------

def main() -> None:
    if not SRC_ROOT_MD.exists():
        raise SystemExit(f"Source not found: {SRC_ROOT_MD}")
    OUT.mkdir(parents=True, exist_ok=True)

    print("== discovering pages")
    root_entry, by_id = discover_entries()
    print(f"  found {len(by_id)} pages")

    print("== converting")
    write_page(root_entry, by_id)
    for entry in by_id.values():
        if entry is root_entry:
            continue
        write_page(entry, by_id)

    print("done.")

if __name__ == "__main__":
    main()
