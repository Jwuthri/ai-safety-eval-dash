"""Extend scenario text fields for longer values

Revision ID: 003
Revises: 002
Create Date: 2025-09-30 01:33:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extend sub_category and methodology to TEXT for long values
    op.alter_column('scenarios', 'sub_category', 
                    type_=sa.Text(), 
                    existing_type=sa.String(length=100))
    op.alter_column('scenarios', 'methodology', 
                    type_=sa.Text(), 
                    existing_type=sa.String(length=255))


def downgrade() -> None:
    # Revert to original VARCHAR lengths
    op.alter_column('scenarios', 'sub_category',
                    type_=sa.String(length=100),
                    existing_type=sa.Text())
    op.alter_column('scenarios', 'methodology',
                    type_=sa.String(length=255),
                    existing_type=sa.Text())
