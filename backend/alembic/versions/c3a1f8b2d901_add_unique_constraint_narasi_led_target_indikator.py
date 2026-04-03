"""add unique constraint narasi_led target-indikator pair

Revision ID: c3a1f8b2d901
Revises: 7145d4e24792
Create Date: 2026-04-03 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3a1f8b2d901"
down_revision: Union[str, None] = "7145d4e24792"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_narasi_led_target_indikator",
        "narasi_led",
        ["target_akreditasi_id", "indikator_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_narasi_led_target_indikator",
        "narasi_led",
        type_="unique",
    )
