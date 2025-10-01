"""add_ai_incidents_table

Revision ID: 217d678d2c6d
Revises: 007_add_human_reviews
Create Date: 2025-10-01 00:28:53.359215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '217d678d2c6d'
down_revision = '007_add_human_reviews'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ai_incidents table
    op.create_table(
        'ai_incidents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('incident_name', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('date_occurred', sa.DateTime(), nullable=True),
        sa.Column('harm_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('impact_description', sa.Text(), nullable=True),
        sa.Column('estimated_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('affected_users', sa.Integer(), nullable=True),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('incident_reference', sa.String(length=255), nullable=True),
        sa.Column('business_type_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_type_id'], ['business_types.id'], ),
        sa.UniqueConstraint('incident_reference')
    )
    op.create_index(op.f('ix_ai_incidents_company'), 'ai_incidents', ['company'], unique=False)
    op.create_index(op.f('ix_ai_incidents_severity'), 'ai_incidents', ['severity'], unique=False)
    op.create_index(op.f('ix_ai_incidents_harm_type'), 'ai_incidents', ['harm_type'], unique=False)
    
    # Add description column to business_types if not exists
    op.add_column('business_types', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    # Drop description from business_types
    op.drop_column('business_types', 'description')
    
    # Drop ai_incidents table
    op.drop_index(op.f('ix_ai_incidents_harm_type'), table_name='ai_incidents')
    op.drop_index(op.f('ix_ai_incidents_severity'), table_name='ai_incidents')
    op.drop_index(op.f('ix_ai_incidents_company'), table_name='ai_incidents')
    op.drop_table('ai_incidents')
