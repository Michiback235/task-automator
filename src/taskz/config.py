from __future__ import annotations

import os
import tomli as tomllib  # py3.11: stdlib tomllib; pyproject pins fallback for older
from pathlib import Path

DEFAULT_CONFIG = {
    "database": {"path": "~/.task_automator/taskz.db"},
    "timezone": "Africa/Nairobi",
    "default_currency": "KES",
    "files": {
        "default_pattern": "{created:%Y-%m-%d}_{name}.{ext}",
        "ignore_globs": "*.tmp,*.swp,~$*",
        "exif_enabled": False,
    },
    "receipts": {
        "enabled_parsers": ["auto", "generic_html", "jumia", "uber"],
    },
    "reporting": {"locale": "en_KE", "decimals": 2},
}

def app_dir() -> Path:
    p = Path(os.path.expanduser("~/.task_automator"))
    p.mkdir(parents=True, exist_ok=True)
    return p

def config_path() -> Path:
    return app_dir() / "config.toml"

def load_config() -> dict:
    path = config_path()
    if not path.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with path.open("rb") as f:
        data = tomllib.load(f)
    # merge defaults shallowly
    cfg = DEFAULT_CONFIG | data
    cfg["database"] = DEFAULT_CONFIG["database"] | cfg.get("database", {})
    cfg["files"] = DEFAULT_CONFIG["files"] | cfg.get("files", {})
    cfg["receipts"] = DEFAULT_CONFIG["receipts"] | cfg.get("receipts", {})
    cfg["reporting"] = DEFAULT_CONFIG["reporting"] | cfg.get("reporting", {})
    return cfg

def save_config(cfg: dict) -> None:
    # Write TOML minimally; avoid extra dep by manual formatting
    lines = []
    if "database" in cfg:
        lines += ["[database]", f'path = "{cfg["database"]["path"]}"', ""]
    lines += [f'timezone = "{cfg.get("timezone","Africa/Nairobi")}"']
    lines += [f'default_currency = "{cfg.get("default_currency","KES")}"', ""]
    if "files" in cfg:
        files = cfg["files"]
        lines += [
            "[files]",
            f'default_pattern = "{files.get("default_pattern","{name}.{ext}")}"',
            f'ignore_globs = "{files.get("ignore_globs","")}"',
            f'exif_enabled = {str(bool(files.get("exif_enabled", False))).lower()}',
            "",
        ]
    if "receipts" in cfg:
        r = cfg["receipts"]
        enabled = ",".join([f'"{x}"' for x in r.get("enabled_parsers", [])])
        lines += ["[receipts]", f"enabled_parsers = [{enabled}]", ""]
    if "reporting" in cfg:
        rep = cfg["reporting"]
        lines += [
            "[reporting]",
            f'locale = "{rep.get("locale","en_KE")}"',
            f'decimals = {int(rep.get("decimals",2))}',
            "",
        ]
    config_path().write_text("\n".join(lines))