from __future__ import annotations

from bs4 import BeautifulSoup

def detect_vendor(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ").lower()
    if "jumia" in text:
        return "jumia"
    if "uber" in text and ("trip" in text or "receipt" in text):
        return "uber"
    return "generic_html"