"""Add document reference to assessment result

Revision ID: 8680d69adbc2
Revises: 623f1adba55d
Create Date: 2024-11-13 15:27:34.049992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8680d69adbc2'
down_revision = '623f1adba55d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assessment_result', schema=None) as batch_op:
        batch_op.add_column(sa.Column('document_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('entry_mode', sa.String(length=20), nullable=False))
        batch_op.create_index('idx_assessment_result_document', ['document_id'], unique=False)
        batch_op.create_foreign_key(None, 'document', ['document_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assessment_result', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index('idx_assessment_result_document')
        batch_op.drop_column('entry_mode')
        batch_op.drop_column('document_id')

    # ### end Alembic commands ###
