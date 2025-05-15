"""merge heads

Revision ID: 4a6a87e2a396
Revises: add_support_ticket_table, add_user_preferences
Create Date: 2025-05-15 17:13:14.641309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a6a87e2a396'
down_revision = ('add_support_ticket_table', 'add_user_preferences')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
