"""Add AI Safety Evaluation Dashboard schema

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create evaluation_results table
    op.create_table('evaluation_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('evaluation_id', sa.String(255), nullable=False),
        sa.Column('vendor_name', sa.String(255), nullable=False),
        sa.Column('model_name', sa.String(255), nullable=False),
        sa.Column('use_case', sa.String(255), nullable=False),
        sa.Column('industry', sa.String(255), nullable=False),
        sa.Column('modality', sa.String(50), nullable=False),
        
        # Test execution details
        sa.Column('test_round', sa.Integer(), nullable=False),
        sa.Column('test_type', sa.Enum('single_turn', 'multi_turn', name='testtype'), nullable=False),
        sa.Column('total_tests', sa.Integer(), nullable=False),
        sa.Column('passed_tests', sa.Integer(), nullable=False),
        sa.Column('failed_tests', sa.Integer(), nullable=False),
        
        # Severity breakdown with P0-P4 definitions
        sa.Column('p0_incidents', sa.Integer(), nullable=False, default=0),
        sa.Column('p1_incidents', sa.Integer(), nullable=False, default=0),
        sa.Column('p2_incidents', sa.Integer(), nullable=False, default=0),
        sa.Column('p3_incidents', sa.Integer(), nullable=False, default=0),
        sa.Column('p4_incidents', sa.Integer(), nullable=False, default=0),
        
        # Testing tactics by modality
        sa.Column('tactics_tested', sa.JSON(), nullable=True),
        
        # Metadata
        sa.Column('evaluation_date', sa.DateTime(), nullable=False),
        sa.Column('framework_version', sa.String(50), nullable=False),
        sa.Column('evaluator_organization', sa.String(255), nullable=True),
        sa.Column('is_third_party_verified', sa.Boolean(), nullable=False, default=True),
        
        # Additional data
        sa.Column('test_methodology', sa.JSON(), nullable=True),
        sa.Column('detailed_results', sa.JSON(), nullable=True),
        sa.Column('example_failures', sa.JSON(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for evaluation_results
    op.create_index('idx_evaluation_results_vendor', 'evaluation_results', ['vendor_name'])
    op.create_index('idx_evaluation_results_industry', 'evaluation_results', ['industry', 'use_case'])
    op.create_index('idx_evaluation_results_date', 'evaluation_results', ['evaluation_date'])
    op.create_index('idx_evaluation_results_round', 'evaluation_results', ['test_round'])
    op.create_index('idx_evaluation_results_type', 'evaluation_results', ['test_type'])

    # Create ai_incidents table
    op.create_table('ai_incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('incident_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        
        # Incident → Harm → Tactic → Use Case → Context flow
        sa.Column('harm_type', sa.String(255), nullable=False),
        sa.Column('attack_tactic', sa.String(255), nullable=True),
        sa.Column('use_case', sa.String(255), nullable=False),
        sa.Column('context', sa.Text(), nullable=True),
        
        # Classification
        sa.Column('severity', sa.Enum('PASS', 'P4', 'P3', 'P2', 'P1', 'P0', name='severitylevel'), nullable=False),
        sa.Column('modality', sa.String(50), nullable=False),
        sa.Column('industry', sa.String(255), nullable=True),
        
        # Business impact (concrete examples like Air Canada)
        sa.Column('financial_impact_usd', sa.Numeric(15, 2), nullable=True),
        sa.Column('legal_defense_cost_usd', sa.Numeric(15, 2), nullable=True),
        sa.Column('brand_impact_description', sa.Text(), nullable=True),
        sa.Column('regulatory_impact', sa.Text(), nullable=True),
        
        # Base rate data for risk assessment
        sa.Column('base_rate_frequency', sa.String(20), nullable=True),
        sa.Column('base_rate_severity', sa.String(20), nullable=True),
        
        # Technical details and prevention
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('aiuc_safeguard_ids', sa.JSON(), nullable=True),
        sa.Column('prevention_measures', sa.JSON(), nullable=True),
        sa.Column('example_prompt', sa.Text(), nullable=True),
        
        # Metadata
        sa.Column('incident_date', sa.Date(), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_featured_example', sa.Boolean(), nullable=False, default=False),
        
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for ai_incidents
    op.create_index('idx_ai_incidents_harm_type', 'ai_incidents', ['harm_type'])
    op.create_index('idx_ai_incidents_industry', 'ai_incidents', ['industry'])
    op.create_index('idx_ai_incidents_severity', 'ai_incidents', ['severity'])
    op.create_index('idx_ai_incidents_featured', 'ai_incidents', ['is_featured_example'])

    # Create test_taxonomy table
    op.create_table('test_taxonomy',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('category', sa.String(255), nullable=False),
        sa.Column('subcategory', sa.String(255), nullable=True),
        sa.Column('tactic_type', sa.String(255), nullable=True),
        
        # Framework alignment
        sa.Column('aiuc_requirement', sa.String(255), nullable=False),
        sa.Column('framework_section', sa.String(255), nullable=True),
        
        # Test details
        sa.Column('test_description', sa.Text(), nullable=False),
        sa.Column('example_prompt', sa.Text(), nullable=True),
        sa.Column('expected_behavior', sa.Text(), nullable=True),
        
        # Incident mapping (incident → harm → tactic → test)
        sa.Column('related_incident_ids', sa.JSON(), nullable=True),
        sa.Column('harm_types_addressed', sa.JSON(), nullable=True),
        
        # Metadata
        sa.Column('modality', sa.String(50), nullable=False),
        sa.Column('difficulty_level', sa.String(20), nullable=True),
        sa.Column('research_references', sa.JSON(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for test_taxonomy
    op.create_index('idx_test_taxonomy_category', 'test_taxonomy', ['category'])
    op.create_index('idx_test_taxonomy_modality', 'test_taxonomy', ['modality'])

    # Create aiuc_certifications table
    op.create_table('aiuc_certifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('vendor_name', sa.String(255), nullable=False),
        sa.Column('model_name', sa.String(255), nullable=False),
        
        # Certification status
        sa.Column('certification_status', sa.Enum('pending', 'active', 'expired', 'revoked', name='certificationstatus'), nullable=False),
        sa.Column('certification_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('framework_version', sa.String(50), nullable=False),
        
        # Insurance coverage
        sa.Column('insurance_eligible', sa.Boolean(), nullable=False, default=False),
        sa.Column('insurance_coverage_usd', sa.Numeric(15, 2), nullable=True),
        sa.Column('insurance_provider', sa.String(255), nullable=True),
        sa.Column('policy_start_date', sa.Date(), nullable=True),
        sa.Column('policy_end_date', sa.Date(), nullable=True),
        
        # Evaluation linkage
        sa.Column('evaluation_ids', sa.JSON(), nullable=True),
        
        # Compliance details
        sa.Column('compliance_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('aiuc_controls_passed', sa.JSON(), nullable=True),
        sa.Column('residual_risks', sa.JSON(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for aiuc_certifications
    op.create_index('idx_aiuc_certifications_vendor', 'aiuc_certifications', ['vendor_name'])
    op.create_index('idx_aiuc_certifications_status', 'aiuc_certifications', ['certification_status'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('aiuc_certifications')
    op.drop_table('test_taxonomy')
    op.drop_table('ai_incidents')
    op.drop_table('evaluation_results')
    
    # Drop custom enums
    op.execute("DROP TYPE IF EXISTS certificationstatus")
    op.execute("DROP TYPE IF EXISTS testtype")
    op.execute("DROP TYPE IF EXISTS severitylevel")