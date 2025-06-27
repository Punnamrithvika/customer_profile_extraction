"""Add resume_data table

Revision ID: c2c121746369
Revises: 
Create Date: 2025-06-10 16:51:18.300447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2c121746369'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), default=False, nullable=False),
    )
    op.create_table(
        'resume_data',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('work_experience', sa.JSON(), nullable=True),
    )
    op.create_unique_constraint('uq_resume_data_combo', 'resume_data', ['full_name', 'email', 'phone_number'])
    op.create_index(op.f('ix_resume_data_full_name'), 'resume_data', ['full_name'], unique=False)
    op.create_index(op.f('ix_resume_data_email'), 'resume_data', ['email'], unique=False)
    op.create_index(op.f('ix_resume_data_phone_number'), 'resume_data', ['phone_number'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_resume_data_phone_number'), table_name='resume_data')
    op.drop_index(op.f('ix_resume_data_email'), table_name='resume_data')
    op.drop_index(op.f('ix_resume_data_full_name'), table_name='resume_data')
    op.drop_constraint('uq_resume_data_combo', 'resume_data', type_='unique')
    op.drop_table('resume_data')
    op.drop_table('users')