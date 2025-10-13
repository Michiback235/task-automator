# TaskZ — Task-Automator CLI (Python + Click + SQLite)

A pragmatic CLI to:
- **Bulk-rename files** safely with previews, counters, EXIF date (optional), and undo.
- **Scrape receipts** (generic HTML + Uber + Jumia in MVP) into a normalized SQLite DB.
- **Log and report expenses** with rules-based auto-categorization, CSV import/export.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
taskz db init
pytest -q
taskz --help
