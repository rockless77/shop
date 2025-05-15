"""Add SupportTicket model

Revision ID: add_support_ticket_table
Revises: 
Create Date: 2025-05-15 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_support_ticket_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create support_ticket table
    op.create_table(
        'support_ticket',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='open'),
        sa.Column('priority', sa.String(length=20), server_default='medium'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('support_ticket')
