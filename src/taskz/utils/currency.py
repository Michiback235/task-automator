from __future__ import annotations

def to_gross(amount_net: float | None, tax: float | None) -> float:
    net = float(amount_net or 0.0)
    tx = float(tax or 0.0)
    return round(net + tx, 2)