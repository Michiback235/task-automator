#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
taskz db init
pytest -q
