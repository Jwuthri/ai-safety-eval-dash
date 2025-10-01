"""Remove evaluation_id from scenarios table

Revision ID: 004
Revises: 003
Create Date: 2025-09-30 01:40:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the confusing evaluation_id column
    op.drop_column('scenarios', 'evaluation_id')
    # Also drop the index if it exists
    op.drop_index('ix_scenario_evaluation_id', table_name='scenarios', if_exists=True)


def downgrade() -> None:
    # Add the column back if we need to rollback
    op.add_column('scenarios', sa.Column('evaluation_id', sa.String(length=50), nullable=True))
    op.create_index('ix_scenario_evaluation_id', 'scenarios', ['evaluation_id'], unique=False)
