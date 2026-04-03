"""merge heads dashboard and lkps

Revision ID: b9c4d8e1f2a3
Revises: 7145d4e24792, a3f2b1c4d5e6
Create Date: 2026-04-03 18:10:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "b9c4d8e1f2a3"
down_revision: Union[str, Sequence[str], None] = ("7145d4e24792", "a3f2b1c4d5e6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
