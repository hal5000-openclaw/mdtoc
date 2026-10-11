"""Command line interface."""
import argparse
import sys

from .core import build_toc, update_document


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="mdtoc",
        description="Generate or update a table of contents for Markdown files.")
    p.add_argument("file", help="Markdown file, or '-' for stdin")
    p.add_argument("--min-level", type=int, default=1, metavar="N")
    p.add_argument("--max-level", type=int, default=6, metavar="N")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true",
                   help="exit 1 if the TOC between markers is out of date")
    g.add_argument("--write", action="store_true",
                   help="update the file in place")
    a = p.parse_args(argv)
    if not (1 <= a.min_level <= a.max_level <= 6):
        p.error("levels must satisfy 1 <= min-level <= max-level <= 6")
    if a.file == "-" and a.write:
        p.error("--write cannot be used with stdin")
    try:
        if a.file == "-":
            text = sys.stdin.read()
        else:
            with open(a.file, encoding="utf-8", newline="") as f:
                text = f.read()
    except OSError as e:
        print("mdtoc: %s" % e, file=sys.stderr)
        return 2

    if not (a.check or a.write):
        sys.stdout.write(build_toc(text, a.min_level, a.max_level))
        return 0
    try:
        new = update_document(text, a.min_level, a.max_level)
    except ValueError as e:
        print("mdtoc: %s" % e, file=sys.stderr)
        return 2
    if a.check:
        if new != text:
            print("mdtoc: TOC is out of date", file=sys.stderr)
            return 1
        return 0
    if new != text:
        with open(a.file, "w", encoding="utf-8", newline="") as f:
            f.write(new)
    return 0
