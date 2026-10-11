import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest import mock

from mdtoc import parse_headings, slugify, build_toc, update_document
from mdtoc.cli import main

DOC = """# Title

<!-- toc -->

<!-- tocstop -->

## Intro
```
# not a heading
```
~~~
## also not
~~~
## Intro
### Sub ##
#### Deep
"""


class Core(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(slugify("Hello, World! `x`"), "hello-world-x")
        self.assertEqual(slugify("A [link](http://x) here_1"), "a-link-here_1")
        self.assertEqual(slugify("Café - Ünï"), "café---ünï")

    def test_fences_ignored_and_dupes(self):
        hs = parse_headings(DOC)
        self.assertEqual([h.slug for h in hs],
                         ["title", "intro", "intro-1", "sub", "deep"])
        self.assertEqual(hs[3].text, "Sub")

    def test_levels(self):
        toc = build_toc(DOC, 2, 3)
        self.assertEqual(toc, "- [Intro](#intro)\n- [Intro](#intro-1)\n"
                              "  - [Sub](#sub)\n")

    def test_update_idempotent(self):
        new = update_document(DOC)
        self.assertIn("- [Title](#title)", new)
        self.assertEqual(update_document(new), new)

    def test_no_markers(self):
        with self.assertRaises(ValueError):
            update_document("# x\n")


class Cli(unittest.TestCase):
    def run_cli(self, *args, stdin=None):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err), \
                mock.patch.object(sys, "stdin", io.StringIO(stdin or "")):
            code = main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_stdin(self):
        code, out, _ = self.run_cli("-", stdin="# A\n## B\n")
        self.assertEqual((code, out), (0, "- [A](#a)\n  - [B](#b)\n"))

    def test_check_and_write(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "a.md")
            with open(path, "w") as f:
                f.write(DOC)
            self.assertEqual(self.run_cli("--check", path)[0], 1)
            self.assertEqual(self.run_cli("--write", path)[0], 0)
            self.assertEqual(self.run_cli("--check", path)[0], 0)
            self.assertEqual(self.run_cli("--check", "--max-level", "2", path)[0], 1)

    def test_missing_markers(self):
        code, _, err = self.run_cli("--check", "-", stdin="# x\n")
        self.assertEqual(code, 2)
        self.assertIn("not found", err)


if __name__ == "__main__":
    unittest.main()
