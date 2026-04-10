#!/usr/bin/env python3
"""
Sync vehicle search Markdown files into an MkDocs Material site.

Reads every subfolder in ../searches/, copies the MD and image files
into docs/, generates mkdocs.yml with proper nav, then builds or deploys.

Usage:
    python3 build.py              # Build site locally (output in site/)
    python3 build.py --serve      # Live-preview at localhost:8000
    python3 build.py --deploy     # Build and push to GitHub Pages (gh-pages branch)
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEARCHES_DIR = ROOT.parent / "searches"
DOCS_DIR = ROOT / "docs"


# ── MkDocs config (everything except nav, which is generated) ────────────

MKDOCS_BASE = """\
site_name: Vehicle Searches

theme:
  name: material
  features:
    - navigation.indexes
    - navigation.sections
    - navigation.top
    - search.highlight
    - search.suggest
    - content.tooltips
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

plugins:
  - search

markdown_extensions:
  - tables
  - toc:
      permalink: true
  - attr_list
  - def_list
  - pymdownx.magiclink
"""


# ── Helpers ──────────────────────────────────────────────────────────────

def extract_title(md_path: Path) -> str:
    """Return the first H1 heading from a Markdown file, or the file stem."""
    if not md_path.exists():
        return md_path.stem
    for line in md_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#\s+(.+)", line)
        if m:
            return m.group(1).strip()
    return md_path.stem


def yaml_quote(s: str) -> str:
    """Wrap a string in double-quotes, escaping for YAML."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ── Core ─────────────────────────────────────────────────────────────────

def sync_docs():
    """Copy search folders into docs/ and write mkdocs.yml."""
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir()

    search_dirs = sorted(
        [d for d in SEARCHES_DIR.iterdir() if d.is_dir()],
        reverse=True,  # newest searches first
    )

    if not search_dirs:
        print(f"No search folders found in {SEARCHES_DIR}")
        sys.exit(1)

    home_lines = ["# Vehicle Searches\n\n"]
    nav_lines = ["nav:\n", "  - Home: index.md\n"]

    for search_dir in search_dirs:
        name = search_dir.name
        dest = DOCS_DIR / name
        dest.mkdir()

        title = extract_title(search_dir / "search.md")

        # ── copy files ──
        for f in search_dir.iterdir():
            if not f.is_file():
                continue
            if f.name == "search.md":
                # search.md becomes the section index page
                (dest / "index.md").write_text(
                    f.read_text(encoding="utf-8"), encoding="utf-8"
                )
            else:
                shutil.copy2(f, dest / f.name)

        # ── rewrite internal links from search.md → index.md ──
        for md in dest.glob("*.md"):
            content = md.read_text(encoding="utf-8")
            updated = content.replace("](search.md)", "](index.md)")
            updated = updated.replace("](./search.md)", "](./index.md)")
            if updated != content:
                md.write_text(updated, encoding="utf-8")

        # ── home page entry ──
        home_lines.append(f"- [{title}]({name}/index.md)\n")

        # ── nav section ──
        nav_lines.append(f"  - {yaml_quote(title)}:\n")
        nav_lines.append(f"    - Overview: {name}/index.md\n")
        for md in sorted(dest.glob("*.md")):
            if md.name == "index.md":
                continue
            page_title = extract_title(md)
            nav_lines.append(
                f"    - {yaml_quote(page_title)}: {name}/{md.name}\n"
            )

    # ── write home page ──
    (DOCS_DIR / "index.md").write_text("".join(home_lines), encoding="utf-8")

    # ── write mkdocs.yml ──
    config = MKDOCS_BASE + "\n" + "".join(nav_lines)
    (ROOT / "mkdocs.yml").write_text(config, encoding="utf-8")

    print(f"Synced {len(search_dirs)} search(es) into docs/")


def mkdocs(*args):
    """Run mkdocs via python3 -m (avoids PATH issues)."""
    return subprocess.run(
        [sys.executable, "-m", "mkdocs", *args], cwd=ROOT, check=True
    )


def main():
    sync_docs()

    if "--deploy" in sys.argv:
        mkdocs("gh-deploy", "--force")
    elif "--serve" in sys.argv:
        mkdocs("serve")
    else:
        mkdocs("build")
        print(f"Site ready at {ROOT / 'site'}/")


if __name__ == "__main__":
    main()
