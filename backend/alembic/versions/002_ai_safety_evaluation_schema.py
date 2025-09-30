"""AI Safety Evaluation Schema - Add evaluation tables

Revision ID: 002
Revises: 001
Create Date: 2025-09-30 00:00:00.000000

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
    # Create business_types table (predefined universal templates)
    op.create_table('business_types',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('use_cases', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('context', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_business_types_name'), 'business_types', ['name'], unique=True)

    # Create organizations table (companies using the platform)
    op.create_table('organizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('business_type_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_type_id'], ['business_types.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=True)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    # Create scenarios table (test scenarios for each business type)
    op.create_table('scenarios',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('business_type_id', sa.String(), nullable=False),
        sa.Column('evaluation_id', sa.String(length=50), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('sub_category', sa.String(length=100), nullable=True),
        sa.Column('input_topic', sa.String(length=255), nullable=True),
        sa.Column('methodology', sa.String(length=255), nullable=True),
        sa.Column('input_prompt', sa.Text(), nullable=False),
        sa.Column('expected_behavior', sa.Text(), nullable=True),
        sa.Column('tactics', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('use_case', sa.String(length=100), nullable=True),
        sa.Column('incident_reference', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_type_id'], ['business_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenario_evaluation_id'), 'scenarios', ['evaluation_id'], unique=False)
    op.create_index('ix_scenario_business_category', 'scenarios', ['business_type_id', 'category'], unique=False)
    op.create_index('ix_scenario_use_case', 'scenarios', ['use_case'], unique=False)

    # Create evaluation_rounds table
    op.create_table('evaluation_rounds',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('RUNNING', 'COMPLETED', 'UNDER_REVIEW', 'FAILED', name='evaluationroundstatus'), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eval_round_org_number', 'evaluation_rounds', ['organization_id', 'round_number'], unique=False)
    op.create_index('ix_eval_round_status', 'evaluation_rounds', ['status'], unique=False)

    # Create evaluation_results table (stores all judge responses)
    op.create_table('evaluation_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('evaluation_round_id', sa.String(), nullable=False),
        sa.Column('scenario_id', sa.String(), nullable=False),
        sa.Column('system_response', sa.Text(), nullable=False),
        sa.Column('final_grade', sa.String(length=10), nullable=True),
        # Judge 1 (Claude Sonnet 4.5)
        sa.Column('judge_1_grade', sa.String(length=10), nullable=True),
        sa.Column('judge_1_reasoning', sa.Text(), nullable=True),
        sa.Column('judge_1_recommendation', sa.Text(), nullable=True),
        sa.Column('judge_1_model', sa.String(length=100), nullable=True),
        # Judge 2 (GPT-5)
        sa.Column('judge_2_grade', sa.String(length=10), nullable=True),
        sa.Column('judge_2_reasoning', sa.Text(), nullable=True),
        sa.Column('judge_2_recommendation', sa.Text(), nullable=True),
        sa.Column('judge_2_model', sa.String(length=100), nullable=True),
        # Judge 3 (Grok-4 Fast)
        sa.Column('judge_3_grade', sa.String(length=10), nullable=True),
        sa.Column('judge_3_reasoning', sa.Text(), nullable=True),
        sa.Column('judge_3_recommendation', sa.Text(), nullable=True),
        sa.Column('judge_3_model', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_round_id'], ['evaluation_rounds.id'], ),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eval_result_round_grade', 'evaluation_results', ['evaluation_round_id', 'final_grade'], unique=False)
    op.create_index('ix_eval_result_scenario', 'evaluation_results', ['scenario_id'], unique=False)

    # Create human_reviews table
    op.create_table('human_reviews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('evaluation_result_id', sa.String(), nullable=False),
        sa.Column('reviewer_id', sa.String(), nullable=True),
        sa.Column('review_status', sa.Enum('APPROVED', 'FLAGGED', 'NEEDS_IMPROVEMENT', name='reviewstatus'), nullable=False),
        sa.Column('override_grade', sa.String(length=10), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_result_id'], ['evaluation_results.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_human_review_result', 'human_reviews', ['evaluation_result_id'], unique=False)
    op.create_index('ix_human_review_status', 'human_reviews', ['review_status'], unique=False)

    # Create agent_iterations table (track improvements per organization)
    op.create_table('agent_iterations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('iteration_number', sa.Integer(), nullable=False),
        sa.Column('changes_made', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_iter_org_number', 'agent_iterations', ['organization_id', 'iteration_number'], unique=False)

    # Create aiuc_certifications table (issued to organizations)
    op.create_table('aiuc_certifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('evaluation_round_id', sa.String(), nullable=False),
        sa.Column('certification_status', sa.Enum('PENDING', 'CERTIFIED', 'REVOKED', name='certificationstatus'), nullable=True),
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('final_pass_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('p2_count', sa.Integer(), nullable=True),
        sa.Column('p3_count', sa.Integer(), nullable=True),
        sa.Column('p4_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['evaluation_round_id'], ['evaluation_rounds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cert_org_status', 'aiuc_certifications', ['organization_id', 'certification_status'], unique=False)
    op.create_index('ix_cert_issued', 'aiuc_certifications', ['issued_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('aiuc_certifications')
    op.drop_table('agent_iterations')
    op.drop_table('human_reviews')
    op.drop_table('evaluation_results')
    op.drop_table('evaluation_rounds')
    op.drop_table('scenarios')
    op.drop_table('organizations')
    op.drop_table('business_types')

    # Drop custom enums
    op.execute("DROP TYPE IF EXISTS evaluationroundstatus")
    op.execute("DROP TYPE IF EXISTS reviewstatus")
    op.execute("DROP TYPE IF EXISTS certificationstatus")
