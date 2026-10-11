"""Core logic: heading parsing, slugs, TOC generation."""
import re
import unicodedata
from typing import List, NamedTuple, Optional

START = "<!-- toc -->"
END = "<!-- tocstop -->"

_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
_CLOSING = re.compile(r"(?:^|[ \t]+)#+$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


class Heading(NamedTuple):
    level: int
    text: str
    slug: str


def slugify(text: str) -> str:
    """GitHub-style anchor slug (without duplicate suffix)."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links/images
    text = text.replace("`", "")
    text = unicodedata.normalize("NFC", text).lower()
    out = []
    for ch in text:
        if ch in " \t":
            out.append("-")
        elif ch == "-" or ch == "_" or unicodedata.category(ch)[0] in "LN" \
                or unicodedata.category(ch) in ("Mn", "Mc"):
            out.append(ch)
    return "".join(out)


def parse_headings(text: str) -> List[Heading]:
    """Return all ATX headings outside fenced code blocks, with unique slugs."""
    headings: List[Heading] = []
    seen = {}
    fence: Optional[str] = None
    for line in text.splitlines():
        m = _FENCE.match(line)
        if fence is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence = m.group(1)
                continue
        else:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not m.group(2).strip():
                fence = None
            continue
        h = _HEADING.match(line)
        if not h:
            continue
        title = _CLOSING.sub("", h.group(2) or "").strip()
        if not title:
            continue
        base = slugify(title)
        n = seen.get(base, 0)
        seen[base] = n + 1
        slug = base if n == 0 else "%s-%d" % (base, n)
        headings.append(Heading(len(h.group(1)), title, slug))
    return headings


def build_toc(text: str, min_level: int = 1, max_level: int = 6) -> str:
    """Build TOC markdown (ending in newline, or empty string)."""
    hs = [h for h in parse_headings(text) if min_level <= h.level <= max_level]
    if not hs:
        return ""
    base = min(h.level for h in hs)
    return "".join("%s- [%s](#%s)\n" % ("  " * (h.level - base), h.text, h.slug)
                   for h in hs)


def update_document(text: str, min_level: int = 1, max_level: int = 6) -> str:
    """Return text with the block between markers regenerated.

    Raises ValueError if the markers are missing or misordered.
    """
    s = text.find(START)
    e = text.find(END, s + len(START)) if s != -1 else -1
    if s == -1 or e == -1:
        raise ValueError("markers %s and %s not found" % (START, END))
    # headings inside the old TOC block must not affect the new one
    toc = build_toc(text[:s] + text[e + len(END):], min_level, max_level)
    return text[:s] + START + "\n\n" + (toc + "\n" if toc else "") + text[e:]
