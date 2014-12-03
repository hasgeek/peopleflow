"""Explara orders are strings

Revision ID: 49274cd3a412
Revises: 519731dea59
Create Date: 2014-12-03 23:06:11.426726

"""

# revision identifiers, used by Alembic.
revision = '49274cd3a412'
down_revision = '519731dea59'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('participant', 'order_id', type_=sa.Unicode(80))


def downgrade():
    op.alter_column('participant', 'order_id', type_=sa.Integer)
