"""Base mapper class with safe-write helpers for LKPS Excel injection."""

from __future__ import annotations

from datetime import date
from typing import Any

from openpyxl.workbook import Workbook
from sqlalchemy.orm import Session

from app.models.lkps import LkpsSubmission

CHECK = "V"   # checkmark written to radio-button columns in the template

# Maps each sheet to the jenjang codes that must fill it (from Daftar Tabel).
# Derived directly from the √ marks in the template's Daftar Tabel sheet.
_SHEET_JENJANG: dict[str, frozenset[str]] = {
    "PS":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr"}),
    "PSPPI": frozenset({"PPI"}),
    "1":     frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "2a1":   frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "2a2":   frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "2a3":   frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "2b":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "3a1":   frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "3a2":   frozenset({"PPI"}),
    "3a3":   frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "3a4":   frozenset({"S1","S1Tr"}),
    "3a5":   frozenset({"S1","S1Tr"}),
    "3b":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "3c":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "4a":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "4b":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "4c":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "4d":    frozenset({"S1","S2","S3","PPI"}),
    "4e":    frozenset({"D1","D2","D3","S1Tr","S2Tr","S3Tr","PPI"}),
    "4f-1":  frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "4f-2":  frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "4f-3":  frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "4f-4":  frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "4g":    frozenset({"D1","D2","D3","S1Tr","S2Tr","S3Tr"}),
    "4h":    frozenset({"S1","S1Tr","S2","S2Tr","S3","S3Tr"}),
    "4i":    frozenset({"S1","S1Tr","S2","S2Tr","S3","S3Tr"}),
    "4j":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "4k":    frozenset({"PPI"}),
    "5a":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "5b":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "5c":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "6a":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "6b":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "6c1":   frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr"}),
    "6c2":   frozenset({"D1","D2","D3","S1","S1Tr"}),
    "6d":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "6e1":   frozenset({"S1","S2","S3"}),
    "6e2":   frozenset({"S1Tr","S2Tr","S3Tr"}),
    "6e3-1": frozenset({"S1","S1Tr","S2","S2Tr","S3","S3Tr"}),
    "6e3-2": frozenset({"S1","S1Tr","S2","S2Tr","S3","S3Tr"}),
    "6e3-3": frozenset({"S1","S1Tr","S2","S2Tr","S3","S3Tr"}),
    "6e3-4": frozenset({"S1","S1Tr","S2","S2Tr","S3","S3Tr"}),
    "6e4":   frozenset({"D1","D2","D3","S1Tr","S2Tr","S3Tr"}),
    "6f1":   frozenset({"D1","D2","D3","S1","S1Tr","PPI"}),
    "6f2":   frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr"}),
    "6g1":   frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","PPI"}),
    "6g2":   frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","PPI"}),
    "6h1":   frozenset({"S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "6h2":   frozenset({"S2","S2Tr","S3","S3Tr"}),
    "6i":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "7a":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
    "7b":    frozenset({"D1","D2","D3","S1","S1Tr","S2","S2Tr","S3","S3Tr","PPI"}),
}


class BaseMapper:
    def __init__(self, wb: Workbook, submission: LkpsSubmission, db: Session) -> None:
        self.wb = wb
        self.submission = submission
        self.db = db

    # ------------------------------------------------------------------
    # Jenjang applicability guard
    # ------------------------------------------------------------------

    def sheet_applies(self, sheet_name: str) -> bool:
        """Return True if this sheet should be filled for the submission's jenjang."""
        jenjang = self.submission.program_studi.jenjang  # e.g. "S1"
        allowed = _SHEET_JENJANG.get(sheet_name)
        if allowed is None:
            return True  # unknown sheet → don't block
        return jenjang in allowed

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
