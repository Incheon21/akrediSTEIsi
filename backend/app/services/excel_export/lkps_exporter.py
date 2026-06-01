"""LKPS Excel exporter – orchestrates all section mappers.

Usage:
    exporter = LkpsExporter(template_path="/path/to/template-lkps.xlsx")
    file_bytes = exporter.generate(submission, db)

The exported workbook is a filled copy of the original template:
- All formulas are preserved (never overwritten)
- Sheet protection is removed so the exported file remains fully editable
- Date cells receive Python date objects so Excel date-arithmetic formulas work
"""

from __future__ import annotations

from io import BytesIO

import openpyxl
from sqlalchemy.orm import Session

from app.models.lkps import LkpsSubmission
from .mappers.menu import MenuMapper, DaftarTabelMapper, ProgramStudiSheetMapper
from .mappers.section_1 import Section1Mapper
from .mappers.section_2 import Section2Mapper
from .mappers.section_3 import Section3Mapper
from .mappers.section_4 import Section4Mapper
from .mappers.section_5 import Section5Mapper
from .mappers.section_6 import Section6Mapper
from .mappers.section_7 import Section7Mapper


class LkpsExporter:
    def __init__(self, template_path: str) -> None:
        self.template_path = template_path

    def generate(self, submission: LkpsSubmission, db: Session) -> bytes:
        """Return the filled LKPS workbook as raw bytes (.xlsx)."""
        # Load template — keep_vba=False strips VBA macros (not needed, avoids issues)
        wb = openpyxl.load_workbook(self.template_path, data_only=False, keep_vba=False)

        # Unprotect all sheets so we can write.
        # Template uses no password (password=False) so this is safe.
        for ws in wb.worksheets:
            ws.protection.sheet = False

        # Run mappers in strict order: Menu MUST go first because Menu!S73
        # is the master TS date referenced by kerjasama status formulas.
        mappers = [
            MenuMapper,
            DaftarTabelMapper,
            ProgramStudiSheetMapper,
            Section1Mapper,
            Section2Mapper,
            Section3Mapper,
            Section4Mapper,
            Section5Mapper,
            Section6Mapper,
            Section7Mapper,
        ]
        for mapper_cls in mappers:
            mapper_cls(wb, submission, db).fill()

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.read()
