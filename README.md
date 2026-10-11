# mdtoc

A small, dependency-free Python 3 CLI that generates and updates a table of contents for Markdown files.

## Why

Hand-maintained TOCs drift. `mdtoc` builds one from your ATX headings (`# ...`), uses GitHub-style anchors (duplicates get `-1`, `-2`, ...), skips headings inside fenced code blocks, and can fail CI when the TOC is stale.

## Install

```
pip install .        # provides the `mdtoc` command
# or run without installing:
python -m mdtoc README.md
```

## Usage

```
mdtoc FILE                  # print TOC to stdout
mdtoc - < FILE              # read stdin
mdtoc --min-level 2 --max-level 3 FILE
mdtoc --write FILE          # update in place
mdtoc --check FILE          # exit 1 if out of date (2 on error)
```

`--write` and `--check` need markers in the file; everything between them is replaced:

```
<!-- toc -->
<!-- tocstop -->
```

Example output:

```
- [Title](#title)
  - [Intro](#intro)
  - [Intro](#intro-1)
```

## Tests

```
python -m unittest
```

## License

MIT
