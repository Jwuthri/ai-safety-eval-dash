"""add confidence score to evaluation results

Revision ID: 006_add_confidence_score
Revises: aab2459ea863
Create Date: 2025-10-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_add_confidence_score'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add confidence_score column to evaluation_results table."""
    op.add_column(
        'evaluation_results',
        sa.Column('confidence_score', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    """Remove confidence_score column from evaluation_results table."""
    op.drop_column('evaluation_results', 'confidence_score')

