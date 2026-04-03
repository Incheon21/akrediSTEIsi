"""make narasi_led.narasi non-nullable

Revision ID: f1a92d4b7c10
Revises: c3a1f8b2d901
Create Date: 2026-04-03 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a92d4b7c10"
down_revision: Union[str, None] = "c3a1f8b2d901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure no existing NULL values violate the new constraint.
    op.execute("UPDATE narasi_led SET narasi = '' WHERE narasi IS NULL")

    op.alter_column(
        "narasi_led",
        "narasi",
        existing_type=sa.Text(),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "narasi_led",
        "narasi",
        existing_type=sa.Text(),
        nullable=True,
    )
