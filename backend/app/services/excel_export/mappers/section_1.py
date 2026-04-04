"""Section 1 mapper – Visi Misi Tujuan Strategi (sheet '1')."""

from __future__ import annotations

from sqlalchemy import select

from app.models.lkps import LkpsVmts
from .base import BaseMapper

# Template rows 7-15 are pre-numbered 1-9 with some jenis labels already locked.
# We only write cols C (pernyataan), D (no_sk), E (link_dokumen).
_NO_TO_ROW = {1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 12, 7: 13, 8: 14, 9: 15}


class Section1Mapper(BaseMapper):
    def fill(self) -> None:
        ws = self.wb["1"]
        records = (
            self.db.execute(
                select(LkpsVmts)
                .where(LkpsVmts.submission_id == self.submission.id)
                .order_by(LkpsVmts.no)
            )
            .scalars()
            .all()
        )
        for rec in records:
            row = _NO_TO_ROW.get(rec.no)
            if row is None:
                continue
            self.safe_write(ws, f"C{row}", rec.pernyataan)
            self.safe_write(ws, f"D{row}", rec.no_sk)
            self.safe_write(ws, f"E{row}", rec.link_dokumen)
