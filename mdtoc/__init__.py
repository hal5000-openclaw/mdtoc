"""mdtoc: generate and update a table of contents for Markdown files."""
from .core import parse_headings, slugify, build_toc, update_document, Heading

__all__ = ["parse_headings", "slugify", "build_toc", "update_document", "Heading"]
__version__ = "0.1.0"
