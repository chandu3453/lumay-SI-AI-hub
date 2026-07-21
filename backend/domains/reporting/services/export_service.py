"""Export — CSV/Excel generation for Enterprise Analytics (Sprint 29).

CSV needs nothing beyond the stdlib. Excel uses `openpyxl` (the one new
backend dependency this sprint adds — no system-level deps, unlike PDF
renderers). PDF is intentionally unimplemented; the spec explicitly allows
a placeholder ("PDF (placeholder if unavailable)").
"""

from __future__ import annotations

import csv
import io
from typing import Any

_FORMULA_TRIGGER_CHARS = ("=", "+", "-", "@")


def _sanitize_cell(value: Any) -> Any:
    """Prefix a leading formula-trigger character with a `'` so Excel/Sheets
    render CSV/XLSX cells as text instead of executing them as formulas
    (CSV/XLSX formula injection — a standard export-safety guard)."""
    if isinstance(value, str) and value.startswith(_FORMULA_TRIGGER_CHARS):
        return "'" + value
    return value


def rows_to_csv(rows: list[dict[str, Any]], *, columns: list[str] | None = None) -> bytes:
    if not rows and not columns:
        return b""
    fieldnames = columns or list(rows[0].keys())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _sanitize_cell(value) for key, value in row.items()})
    return buffer.getvalue().encode("utf-8")


def rows_to_xlsx(rows: list[dict[str, Any]], *, columns: list[str] | None = None, sheet_title: str = "Report") -> bytes:
    from openpyxl import Workbook

    fieldnames = columns or (list(rows[0].keys()) if rows else [])
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_title[:31]  # Excel sheet-name length limit
    sheet.append(fieldnames)
    for row in rows:
        sheet.append([_sanitize_cell(row.get(field, "")) for field in fieldnames])
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
