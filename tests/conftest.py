from __future__ import annotations

import pytest

from taskz.cli import MIGRATIONS_DIR
from taskz.config import DEFAULT_CONFIG, save_config
from taskz.db.connection import apply_migrations, connect


@pytest.fixture(autouse=True)
def _isolate_home_tmp(tmp_path, monkeypatch):
    # Point app dir to temp by overriding HOME
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg = DEFAULT_CONFIG.copy()
    cfg["database"]["path"] = str(tmp_path / "taskz.db")
    save_config(cfg)
    # init DB
    conn = connect()
    apply_migrations(conn, sorted(MIGRATIONS_DIR.glob("*.sql")))
    yield


@pytest.fixture
def sample_files(tmp_path):
    base = tmp_path / "files"
    base.mkdir()
    (base / "A.txt").write_text("alpha")
    (base / "B.txt").write_text("beta")
    return base


@pytest.fixture
def receipts_dir(tmp_path):
    base = tmp_path / "receipts"
    (base / "uber").mkdir(parents=True)
    (base / "jumia").mkdir(parents=True)
    (base / "generic").mkdir(parents=True)
    (base / "uber" / "receipt1.html").write_text(
        "<html><body><h1>Uber Trip Receipt</h1>"
        "<p>Total: KES 450.00</p>"
        "<p>Oct 12, 2025 21:33</p></body></html>"
    )
    (base / "jumia" / "order1.html").write_text(
        "<html><body><h1>Jumia Order</h1>"
        "<p>Order #ABCD-1234</p>"
        "<p>Total: KES 999.00</p></body></html>"
    )
    (base / "generic" / "receipt1.html").write_text(
        "<html><body><p>Thank you. Total due KES 120.50</p></body></html>"
    )
    return base
