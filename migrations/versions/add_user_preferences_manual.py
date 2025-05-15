"""Add user preferences manually

Revision ID: add_user_preferences_manual
Revises: 4a6a87e2a396
Create Date: 2025-05-15 15:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_preferences_manual'
down_revision = '4a6a87e2a396'
branch_labels = None
depends_on = None


def upgrade():
    # Add new preference columns
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('push_notifications', sa.Boolean(), server_default='1', nullable=True))
        batch_op.add_column(sa.Column('sms_notifications', sa.Boolean(), server_default='0', nullable=True))
        batch_op.add_column(sa.Column('price_drop_notifications', sa.Boolean(), server_default='1', nullable=True))
        batch_op.add_column(sa.Column('new_listing_notifications', sa.Boolean(), server_default='1', nullable=True))
        batch_op.add_column(sa.Column('email_frequency', sa.String(20), server_default='daily', nullable=True))
        batch_op.add_column(sa.Column('profile_visibility', sa.String(20), server_default='public', nullable=True))
        batch_op.add_column(sa.Column('activity_visibility', sa.String(20), server_default='public', nullable=True))
        batch_op.add_column(sa.Column('items_per_page', sa.Integer(), server_default='10', nullable=True))


def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('push_notifications')
        batch_op.drop_column('sms_notifications')
        batch_op.drop_column('price_drop_notifications')
        batch_op.drop_column('new_listing_notifications')
        batch_op.drop_column('email_frequency')
        batch_op.drop_column('profile_visibility')
        batch_op.drop_column('activity_visibility')
        batch_op.drop_column('items_per_page')
