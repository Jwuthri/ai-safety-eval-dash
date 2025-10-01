"""add_generated_scenarios_table

Revision ID: dd58743a2e78
Revises: 871009c8f314
Create Date: 2025-10-01 11:23:56.941127

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'dd58743a2e78'
down_revision = '871009c8f314'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create generated_scenarios table for AI-generated test scenarios
    op.create_table('generated_scenarios',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('business_type_id', sa.String(), nullable=False),
        
        # Scenario identification
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('sub_category', sa.Text(), nullable=True),
        sa.Column('input_topic', sa.String(length=255), nullable=True),
        
        # Attack methodology
        sa.Column('methodology', sa.Text(), nullable=True),
        sa.Column('input_prompt', sa.Text(), nullable=False),
        sa.Column('expected_behavior', sa.Text(), nullable=True),
        
        # Categorization
        sa.Column('tactics', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('use_case', sa.String(length=100), nullable=True),
        sa.Column('incident_reference', sa.String(length=255), nullable=True),
        
        # Generation metadata
        sa.Column('generation_prompt', sa.Text(), nullable=True),  # Store the prompt used to generate
        sa.Column('model_used', sa.String(length=100), nullable=True),  # Track which model generated it
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False),
        
        # Constraints
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['business_type_id'], ['business_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for common queries
    op.create_index('ix_generated_scenario_org_id', 'generated_scenarios', ['organization_id'], unique=False)
    op.create_index('ix_generated_scenario_business_type', 'generated_scenarios', ['business_type_id'], unique=False)
    op.create_index('ix_generated_scenario_category', 'generated_scenarios', ['category'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_generated_scenario_category', table_name='generated_scenarios')
    op.drop_index('ix_generated_scenario_business_type', table_name='generated_scenarios')
    op.drop_index('ix_generated_scenario_org_id', table_name='generated_scenarios')
    op.drop_table('generated_scenarios')
