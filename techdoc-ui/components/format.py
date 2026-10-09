"""Small shared rendering helpers."""

from __future__ import annotations

import html
from decimal import Decimal
from typing import Any

import streamlit as st


def money(value: Any, currency: str) -> str:
    return f"{currency} {Decimal(str(value)):,.2f}"


def hours(value: Any) -> str:
    d = Decimal(str(value))
    return f"{d:,.0f}" if d == d.to_integral() else f"{d:,.1f}"


def pct(rate: Any) -> str:
    """0.10 → '10%' (no trailing zeros)."""
    v = (Decimal(str(rate)) * 100).normalize()
    return f"{v:f}%"


def kpi_row(items: list[tuple[str, str]], small: bool = False) -> None:
    """Wrapping KPI tiles (st.metric truncates long values)."""
    cols = st.columns(len(items))
    size = "1.15rem" if small else "1.45rem"
    for col, (label, value) in zip(cols, items, strict=True):
        col.markdown(f'<div class="ps-kpi-label">{html.escape(label)}</div>'
                     f'<div class="ps-kpi" style="font-size:{size}">{html.escape(value)}</div>', unsafe_allow_html=True)
