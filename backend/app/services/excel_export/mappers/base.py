"""Base mapper class with safe-write helpers for LKPS Excel injection."""

from __future__ import annotations

from datetime import date
from typing import Any

from openpyxl.workbook import Workbook
from sqlalchemy.orm import Session

from app.models.lkps import LkpsSubmission

CHECK = "√"   # checkmark written to radio-button columns in the template


class BaseMapper:
    def __init__(self, wb: Workbook, submission: LkpsSubmission, db: Session) -> None:
        self.wb = wb
        self.submission = submission
        self.db = db

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------

    def safe_write(self, ws, coord: str, value: Any) -> None:
        """Write ``value`` to ``coord`` only if the cell is NOT a formula.

        Formula cells (starting with '=') are NEVER overwritten — they must
        continue to auto-compute inside Excel exactly as in the original template.
        """
        cell = ws[coord]
        if isinstance(cell.value, str) and cell.value.startswith("="):
            return
        cell.value = value

    def write_rows(
        self,
        ws,
        records: list,
        start_row: int,
        col_map: dict[str, str],
    ) -> None:
        """Write a list of ORM objects into sequential rows using ``col_map``.

        ``col_map`` maps attribute names to Excel column letters.
        Formula columns must be omitted from ``col_map``.
        """
        for i, record in enumerate(records):
            row = start_row + i
            for attr, col in col_map.items():
                value = getattr(record, attr, None)
                if isinstance(value, date) and not hasattr(value, "hour"):
                    # openpyxl stores dates natively; Excel date arithmetic works
                    pass
                self.safe_write(ws, f"{col}{row}", value)

    def write_check(self, ws, col: str, row: int, condition: bool) -> None:
        """Write CHECK mark to a cell, or clear it, based on ``condition``."""
        self.safe_write(ws, f"{col}{row}", CHECK if condition else None)

    def write_tingkat_check(
        self, ws, row: int, tingkat: str | None,
        col_intr: str, col_nas: str, col_lokal: str,
    ) -> None:
        """Write a CHECK to the correct tingkat column (internasional/nasional/lokal)."""
        self.write_check(ws, col_intr,  row, tingkat == "internasional")
        self.write_check(ws, col_nas,   row, tingkat == "nasional")
        self.write_check(ws, col_lokal, row, tingkat == "lokal")

    def fill(self) -> None:
        raise NotImplementedError
