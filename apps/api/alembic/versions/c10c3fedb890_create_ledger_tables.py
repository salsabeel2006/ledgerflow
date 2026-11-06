"""create_ledger_tables

Revision ID: c10c3fedb890
Revises: b4a41df24c86
Create Date: 2026-09-12 14:58:01.491546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c10c3fedb890'
down_revision: Union[str, Sequence[str], None] = 'b4a41df24c86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('accounts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('from_account_id', sa.UUID(), nullable=False),
    sa.Column('to_account_id', sa.UUID(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['from_account_id'], ['accounts.id'], ),
    sa.ForeignKeyConstraint(['to_account_id'], ['accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('transactions')
    op.drop_table('accounts')
