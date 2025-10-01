"""remove_business_type_id_from_ai_incidents

Revision ID: 871009c8f314
Revises: 20f81a9643ab
Create Date: 2025-10-01 00:51:05.660175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '871009c8f314'
down_revision = '20f81a9643ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop foreign key constraint and column
    with op.batch_alter_table('ai_incidents') as batch_op:
        batch_op.drop_constraint('ai_incidents_business_type_id_fkey', type_='foreignkey')
        batch_op.drop_column('business_type_id')


def downgrade() -> None:
    # Re-add column and foreign key constraint
    with op.batch_alter_table('ai_incidents') as batch_op:
        batch_op.add_column(sa.Column('business_type_id', sa.String(), nullable=True))
        batch_op.create_foreign_key(
            'ai_incidents_business_type_id_fkey',
            'business_types',
            ['business_type_id'],
            ['id']
        )
