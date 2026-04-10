# Vehicle Search Pages

Publishes Markdown search results from `../searches/` as a polished MkDocs Material website — searchable, navigable, mobile-friendly, with dark/light mode.

## Prerequisites

```
pip install mkdocs mkdocs-material
```

## One-time GitHub setup

1. Create a new repo on GitHub (e.g. `vehicle-searches`). Public or private — the Pages site will be public either way.
2. From this folder:
   ```
   git init
   git remote add origin git@github.com:<user>/<repo>.git
   ```
3. Commit the scaffolding:
   ```
   git add build.py .gitignore README.md
   git commit -m "Initial MkDocs setup"
   git push -u origin main
   ```
4. Deploy once to create the `gh-pages` branch:
   ```
   python3 build.py --deploy
   ```
5. In the GitHub repo go to **Settings > Pages** and set source to the **gh-pages** branch, root `/`. The site will be live at `https://<user>.github.io/<repo>/`.

## Daily usage

| Command | What it does |
|---------|-------------|
| `python3 build.py --serve` | Preview locally at http://localhost:8000 |
| `python3 build.py` | Build static site into `site/` (for zipping and sending) |
| `python3 build.py --deploy` | Build and push to GitHub Pages |

## Sharing via Telegram

**As a link:** deploy, then send the GitHub Pages URL.

**As a file:** run `python3 build.py`, then zip `site/` and send. Recipient opens `index.html` in any browser — works offline, search included.

## How it works

`build.py` scans `../searches/` for subdirectories. For each one it:
- Copies all MD/image files into `docs/<search-name>/`
- Renames `search.md` to `index.md` (MkDocs section landing page)
- Rewrites internal links accordingly
- Generates `mkdocs.yml` with full navigation
- Runs MkDocs to build or deploy
