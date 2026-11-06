"""create_users_table

Revision ID: 2df8d601772c
Revises: 
Create Date: 2026-09-11 16:18:31.975170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2df8d601772c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
