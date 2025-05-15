"""Add user preferences

Revision ID: add_user_preferences
Revises: 
Create Date: 2025-05-15 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_preferences'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new preference columns
    op.add_column('user', sa.Column('push_notifications', sa.Boolean(), server_default='1', nullable=True))
    op.add_column('user', sa.Column('sms_notifications', sa.Boolean(), server_default='0', nullable=True))
    op.add_column('user', sa.Column('price_drop_notifications', sa.Boolean(), server_default='1', nullable=True))
    op.add_column('user', sa.Column('new_listing_notifications', sa.Boolean(), server_default='1', nullable=True))
    op.add_column('user', sa.Column('email_frequency', sa.String(20), server_default='daily', nullable=True))
    op.add_column('user', sa.Column('profile_visibility', sa.String(20), server_default='public', nullable=True))
    op.add_column('user', sa.Column('activity_visibility', sa.String(20), server_default='public', nullable=True))
    op.add_column('user', sa.Column('items_per_page', sa.Integer(), server_default='10', nullable=True))


def downgrade():
    op.drop_column('user', 'push_notifications')
    op.drop_column('user', 'sms_notifications')
    op.drop_column('user', 'price_drop_notifications')
    op.drop_column('user', 'new_listing_notifications')
    op.drop_column('user', 'email_frequency')
    op.drop_column('user', 'profile_visibility')
    op.drop_column('user', 'activity_visibility')
    op.drop_column('user', 'items_per_page')
