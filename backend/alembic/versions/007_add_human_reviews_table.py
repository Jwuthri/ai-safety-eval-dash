"""add human reviews table

Revision ID: 007_add_human_reviews
Revises: 006_add_confidence_score
Create Date: 2025-10-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_human_reviews'
down_revision = '006_add_confidence_score'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create human_reviews table for low-confidence result reviews."""
    op.create_table(
        'human_reviews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('evaluation_result_id', sa.String(), nullable=False),
        sa.Column('reviewer_id', sa.String(), nullable=True),
        sa.Column('reviewer_name', sa.String(), nullable=True),
        sa.Column('original_grade', sa.String(length=10), nullable=False),
        sa.Column('original_confidence', sa.Integer(), nullable=False),
        sa.Column('reviewed_grade', sa.String(length=10), nullable=False),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_result_id'], ['evaluation_results.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_human_review_result', 'human_reviews', ['evaluation_result_id'])
    op.create_index('ix_human_review_reviewer', 'human_reviews', ['reviewer_id'])
    op.create_index('ix_human_review_date', 'human_reviews', ['reviewed_at'])


def downgrade() -> None:
    """Drop human_reviews table and indexes."""
    op.drop_index('ix_human_review_date', table_name='human_reviews')
    op.drop_index('ix_human_review_reviewer', table_name='human_reviews')
    op.drop_index('ix_human_review_result', table_name='human_reviews')
    op.drop_table('human_reviews')

