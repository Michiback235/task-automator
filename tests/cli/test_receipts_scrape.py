from __future__ import annotations

from click.testing import CliRunner

from taskz.cli import cli
from taskz.db.connection import connect


def test_receipts_scrape(receipts_dir):
    runner = CliRunner()
    res = runner.invoke(
        cli,
        ["receipts", "scrape", "--from", str(receipts_dir), "--globs", "**/*.html", "--yes"],
    )
    assert res.exit_code == 0
    assert "Ingested" in res.output

    conn = connect()
    n = conn.execute("SELECT COUNT(*) c FROM receipt").fetchone()["c"]
    assert n == 3
    m = conn.execute("SELECT COUNT(*) c FROM expense WHERE source='receipt'").fetchone()["c"]
    assert m == 3
