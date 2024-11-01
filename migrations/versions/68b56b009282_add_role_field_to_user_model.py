"""Add role field to User model

Revision ID: 68b56b009282
Revises: 
Create Date: 2024-10-31 20:41:00.530671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68b56b009282'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('patient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.String(length=50), nullable=True),
    sa.Column('family_name', sa.String(length=100), nullable=False),
    sa.Column('given_name', sa.String(length=100), nullable=False),
    sa.Column('gender', sa.String(length=20), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('address_line', sa.String(length=200), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('postal_code', sa.String(length=20), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('identifier')
    )
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('audio_file', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('meat_monitoring', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('meat_assessment', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('meat_evaluation', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('meat_treatment', sa.Text(), nullable=True))
        batch_op.alter_column('content',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('patient_id',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.drop_constraint('document_author_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['id'])
        batch_op.drop_column('meat_monitor')
        batch_op.drop_column('tamper_action')
        batch_op.drop_column('tamper_medical_necessity')
        batch_op.drop_column('meat_treat')
        batch_op.drop_column('tamper_response')
        batch_op.drop_column('meat_assess')
        batch_op.drop_column('tamper_plan')
        batch_op.drop_column('author_id')
        batch_op.drop_column('tamper_education')
        batch_op.drop_column('tamper_time')
        batch_op.drop_column('status')
        batch_op.drop_column('recording_path')
        batch_op.drop_column('meat_evaluate')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=64),
               type_=sa.String(length=80),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=256),
               type_=sa.String(length=120),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=120),
               type_=sa.VARCHAR(length=256),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
        batch_op.alter_column('username',
               existing_type=sa.String(length=80),
               type_=sa.VARCHAR(length=64),
               existing_nullable=False)

    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meat_evaluate', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('recording_path', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('tamper_time', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('tamper_education', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('tamper_plan', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('meat_assess', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('tamper_response', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('meat_treat', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('tamper_medical_necessity', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('tamper_action', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('meat_monitor', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('document_author_id_fkey', 'user', ['author_id'], ['id'])
        batch_op.alter_column('patient_id',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)
        batch_op.alter_column('content',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.drop_column('meat_treatment')
        batch_op.drop_column('meat_evaluation')
        batch_op.drop_column('meat_assessment')
        batch_op.drop_column('meat_monitoring')
        batch_op.drop_column('audio_file')
        batch_op.drop_column('user_id')

    op.drop_table('patient')
    # ### end Alembic commands ###
