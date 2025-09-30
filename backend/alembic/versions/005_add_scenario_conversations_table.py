"""add_scenario_conversations_table

Revision ID: 005
Revises: 004
Create Date: 2025-09-30 00:42:11.730864

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add scenario_conversations table."""
    op.create_table(
        'scenario_conversations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('evaluation_round_id', sa.String(), nullable=False),
        sa.Column('scenario_id', sa.String(), nullable=False),
        sa.Column('conversation_data', JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['evaluation_round_id'], ['evaluation_rounds.id'], ),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for common queries
    op.create_index(
        'ix_scenario_conversations_org_round',
        'scenario_conversations',
        ['organization_id', 'evaluation_round_id']
    )
    op.create_index(
        'ix_scenario_conversations_scenario',
        'scenario_conversations',
        ['scenario_id']
    )


def downgrade() -> None:
    """Remove scenario_conversations table."""
    op.drop_index('ix_scenario_conversations_scenario', table_name='scenario_conversations')
    op.drop_index('ix_scenario_conversations_org_round', table_name='scenario_conversations')
    op.drop_table('scenario_conversations')
