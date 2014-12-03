"""Venues are scoped to events

Revision ID: bdcaab46497
Revises: 49274cd3a412
Create Date: 2014-12-04 00:16:31.615846

"""

# revision identifiers, used by Alembic.
revision = 'bdcaab46497'
down_revision = '49274cd3a412'

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('venue', schema=None) as batch_op:
        batch_op.drop_constraint(u'venue_name_key')
        batch_op.create_unique_constraint(None, ['event_id', 'name'])


def downgrade():
    with op.batch_alter_table('venue', schema=None) as batch_op:
        batch_op.drop_constraint(None)
        batch_op.create_unique_constraint(u'venue_name_key', ['name'])
