"""add_description_to_organizations

Revision ID: 82bde6a316fd
Revises: dd58743a2e78
Create Date: 2025-10-01 11:38:13.474378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82bde6a316fd'
down_revision = 'dd58743a2e78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add description field to organizations table
    op.add_column('organizations', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove description field from organizations table
    op.drop_column('organizations', 'description')
