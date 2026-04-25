"""Section 1 mapper – Visi Misi Tujuan Strategi (sheet '1').

Template row layout (fixed by BAN-PT):
  Row 7-8   → VMTS PT        (2 slots)
  Row 9-10  → VMTS UPPS      (2 slots)
  Row 11-20 → Visi Keilmuan PS (10 slots)

Each jenis_vmts group is written sequentially starting from its section's
first row.  The 'no' field in the DB is just a UI counter — it is NOT used
to pick the Excel row.
"""

from __future__ import annotations

from sqlalchemy import select

from app.models.lkps import LkpsVmts
from .base import BaseMapper

# First data row and max slots for each jenis_vmts section
_SECTION: dict[str, tuple[int, int]] = {
    "VMTS PT":          (7,  2),
    "VMTS UPPS":        (9,  2),
    "Visi Keilmuan PS": (11, 10),
}


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

        # Track how many rows have been written per jenis section
        counters: dict[str, int] = {}
        for rec in records:
            section = _SECTION.get(rec.jenis_vmts)
            if section is None:
                continue
            first_row, max_slots = section
            idx = counters.get(rec.jenis_vmts, 0)
            if idx >= max_slots:
                continue  # template has no more rows for this type
            row = first_row + idx
            counters[rec.jenis_vmts] = idx + 1

            self.safe_write(ws, f"C{row}", rec.pernyataan)
            self.safe_write(ws, f"D{row}", rec.no_sk)
            self.safe_write(ws, f"E{row}", rec.link_dokumen)
