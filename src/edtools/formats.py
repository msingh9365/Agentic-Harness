"""Recognise how string values are formatted. Deterministic signals the model can't fake."""

import re
from collections import Counter
from datetime import datetime

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d", "%d.%m.%Y", "%Y/%m/%d"]

NUMBER_FORMATS = {
    "plain_decimal": re.compile(r"^-?\d+(\.\d+)?$"),           # 12.50
    "comma_decimal": re.compile(r"^-?\d+,\d+$"),               # 12,50
    "currency_symbol": re.compile(r"^-?[$€£¥]\s?\d[\d,]*(\.\d+)?$"),  # $12.50
    "thousands_sep": re.compile(r"^-?\d{1,3}(,\d{3})+(\.\d+)?$"),     # 1,234.50
    "epoch_ms": re.compile(r"^1\d{12}$"),                      # 13 digits, 2001..2033
    "epoch_s": re.compile(r"^1\d{9}$"),
}


def shape(value: str) -> str:
    """'14/10/2026' -> '99/99/9999', 'USD' -> 'AAA'. Collapses values to their format."""
    return "".join("9" if c.isdigit() else "A" if c.isupper() else "a" if c.isalpha() else c for c in value)


def top_shapes(values: list[str], n: int = 3) -> list[dict]:
    if not values:
        return []
    counts = Counter(shape(v) for v in values)
    return [{"shape": s, "pct": round(100 * c / len(values), 1)} for s, c in counts.most_common(n)]


def _parses(value: str, fmt: str) -> bool:
    try:
        datetime.strptime(value, fmt)
        return True
    except ValueError:
        return False


def format_matches(values: list[str]) -> list[dict]:
    """Match rate of each known date/number format, only those that match something."""
    if not values:
        return []
    out = []
    for fmt in DATE_FORMATS:
        pct = 100 * sum(_parses(v, fmt) for v in values) / len(values)
        if pct:
            out.append({"format": fmt, "kind": "date", "match_pct": round(pct, 1)})
    for name, rx in NUMBER_FORMATS.items():
        pct = 100 * sum(bool(rx.match(v)) for v in values) / len(values)
        if pct:
            out.append({"format": name, "kind": "number", "match_pct": round(pct, 1)})
    full = {m["format"] for m in out if m["match_pct"] == 100}
    if {"%d/%m/%Y", "%m/%d/%Y"} <= full:
        # Every day value is <= 12, so the data alone can't tell DD/MM from MM/DD.
        out.append({"format": "ambiguous_day_month", "kind": "warning", "match_pct": 100.0})
    return sorted(out, key=lambda m: -m["match_pct"])
