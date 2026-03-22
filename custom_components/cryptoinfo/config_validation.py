"""Voluptuous validators for Cryptoinfo configuration."""

from typing import Any

import voluptuous as vol


def precision(value: Any) -> str:
    """Normalize CoinGecko `precision` (empty, full, or 0–18)."""
    if value is None:
        return ""
    v = str(value).strip().lower()
    if not v:
        return ""
    if v == "full":
        return "full"
    if v.isdigit():
        n = int(v)
        if 0 <= n <= 18:
            return str(n)
    raise vol.Invalid(
        "Must be empty (CoinGecko default), full, or a whole number from 0 to 18"
    )
