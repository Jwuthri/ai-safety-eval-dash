"""add_precomputed_answers_table

Revision ID: aab2459ea863
Revises: 005
Create Date: 2025-09-30 09:46:40.159633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aab2459ea863'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add precomputed_answers table."""
    op.create_table(
        'precomputed_answers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('scenario_id', sa.String(), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('assistant_output', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for common queries
    op.create_index(
        'ix_precomputed_answers_org_round',
        'precomputed_answers',
        ['organization_id', 'round_number']
    )
    op.create_index(
        'ix_precomputed_answers_scenario_round',
        'precomputed_answers',
        ['scenario_id', 'round_number', 'organization_id'],
        unique=True  # One answer per scenario/round/org combo
    )


def downgrade() -> None:
    """Remove precomputed_answers table."""
    op.drop_index('ix_precomputed_answers_scenario_round', table_name='precomputed_answers')
    op.drop_index('ix_precomputed_answers_org_round', table_name='precomputed_answers')
    op.drop_table('precomputed_answers')
