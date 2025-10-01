"""add_safeguards_table

Revision ID: 20f81a9643ab
Revises: 217d678d2c6d
Create Date: 2025-10-01 00:47:49.684271

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20f81a9643ab'
down_revision = '217d678d2c6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create safeguards table
    op.create_table(
        'safeguards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('why_it_works', sa.Text(), nullable=True),
        sa.Column('implementation_type', sa.String(length=100), nullable=False),
        sa.Column('implementation_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('aiuc_requirement', sa.String(length=100), nullable=True),
        sa.Column('compliance_level', sa.String(length=50), nullable=True),
        sa.Column('effectiveness_rating', sa.String(length=20), nullable=True),
        sa.Column('reduces_severity', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('detection_method', sa.Text(), nullable=True),
        sa.Column('automated_response', sa.Text(), nullable=True),
        sa.Column('incident_types', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_safeguards_category'), 'safeguards', ['category'], unique=False)
    op.create_index(op.f('ix_safeguards_name'), 'safeguards', ['name'], unique=False)
    
    # Create incident_safeguard_mappings table
    op.create_table(
        'incident_safeguard_mappings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('incident_id', sa.String(), nullable=False),
        sa.Column('safeguard_id', sa.String(), nullable=False),
        sa.Column('effectiveness_note', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['ai_incidents.id'], ),
        sa.ForeignKeyConstraint(['safeguard_id'], ['safeguards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mappings_incident'), 'incident_safeguard_mappings', ['incident_id'], unique=False)
    op.create_index(op.f('ix_mappings_safeguard'), 'incident_safeguard_mappings', ['safeguard_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_mappings_safeguard'), table_name='incident_safeguard_mappings')
    op.drop_index(op.f('ix_mappings_incident'), table_name='incident_safeguard_mappings')
    op.drop_table('incident_safeguard_mappings')
    
    op.drop_index(op.f('ix_safeguards_name'), table_name='safeguards')
    op.drop_index(op.f('ix_safeguards_category'), table_name='safeguards')
    op.drop_table('safeguards')
