"""add legal metrics columns

Revision ID: add_legal_metrics
Revises: previous_revision
Create Date: 2026-05-21 15:07:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_legal_metrics'
down_revision = None  # Will be set automatically by Alembic
branch_labels = None
depends_on = None


def upgrade():
    """Add legal-specific metric columns to test_example_results table"""
    op.add_column('test_example_results', sa.Column('legal_term_precision', sa.Float(), nullable=True))
    op.add_column('test_example_results', sa.Column('legal_term_recall', sa.Float(), nullable=True))
    op.add_column('test_example_results', sa.Column('legal_term_f1', sa.Float(), nullable=True))
    op.add_column('test_example_results', sa.Column('citation_accuracy', sa.Float(), nullable=True))
    op.add_column('test_example_results', sa.Column('completeness_score', sa.Float(), nullable=True))


def downgrade():
    """Remove legal-specific metric columns from test_example_results table"""
    op.drop_column('test_example_results', 'completeness_score')
    op.drop_column('test_example_results', 'citation_accuracy')
    op.drop_column('test_example_results', 'legal_term_f1')
    op.drop_column('test_example_results', 'legal_term_recall')
    op.drop_column('test_example_results', 'legal_term_precision')

# Made with Bob
