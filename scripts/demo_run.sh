#!/usr/bin/env bash
set -euo pipefail

# Demo: rename + receipts + expenses reports
taskz db init
mkdir -p demo/files
echo "hello" > demo/files/a.txt
echo "world" > demo/files/b.txt
taskz files rename --src demo/files --pattern "{created:%Y-%m-%d}_{name}.{ext}" --yes

mkdir -p demo/receipts
cat > demo/receipts/uber1.html <<'HTML'
<html><body><h1>Uber Trip Receipt</h1><p>Total: KES 250.00</p><p>Oct 01, 2025 08:15</p></body></html>
HTML
taskz receipts scrape --from demo/receipts --globs "*.html" --yes

taskz expenses add --date 2025-10-02 --merchant "Cafe Java" --amount 320 --currency KES --category Food
taskz expenses rules add --field category --pattern Uber --value Transport
taskz expenses rules apply
taskz expenses report monthly --since 2025-10-01 --until 2025-10-31