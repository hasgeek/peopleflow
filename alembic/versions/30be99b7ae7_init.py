"""init

Revision ID: 30be99b7ae7
Revises: None
Create Date: 2013-07-25 17:39:03.922325

"""

# revision identifiers, used by Alembic.
revision = '30be99b7ae7'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('name', sa.Unicode(length=80), nullable=False),
    sa.Column('title', sa.Unicode(length=80), nullable=False),
    sa.Column('from_date', sa.Date(), nullable=True),
    sa.Column('to_date', sa.Date(), nullable=True),
    sa.Column('doattend_id', sa.Unicode(length=10), nullable=True),
    sa.Column('venue', sa.Unicode(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cxlog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('users', sa.Unicode(length=200), nullable=False),
    sa.Column('sent', sa.Boolean(), nullable=False),
    sa.Column('log_message', sa.Unicode(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('username', sa.Unicode(length=80), nullable=True),
    sa.Column('lastuser_token_scope', sa.Unicode(length=250), nullable=True),
    sa.Column('userinfo', sa.UnicodeText(), nullable=True),
    sa.Column('lastuser_token_type', sa.Unicode(length=250), nullable=True),
    sa.Column('userid', sa.String(length=22), nullable=False),
    sa.Column('lastuser_token', sa.String(length=22), nullable=True),
    sa.Column('fullname', sa.Unicode(length=80), nullable=False),
    sa.Column('email', sa.Unicode(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('lastuser_token'),
    sa.UniqueConstraint('userid'),
    sa.UniqueConstraint('username')
    )
    op.create_table('kiosk',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('name', sa.Unicode(length=80), nullable=False),
    sa.Column('company', sa.Unicode(length=80), nullable=True),
    sa.Column('company_tag', sa.Unicode(length=150), nullable=True),
    sa.Column('company_logo', sa.Unicode(length=120), nullable=True),
    sa.Column('tap_msg', sa.Unicode(length=200), nullable=True),
    sa.Column('privacy_policy', sa.Unicode(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('participant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('ticket_number', sa.Unicode(length=15), nullable=True),
    sa.Column('name', sa.Unicode(length=80), nullable=False),
    sa.Column('email', sa.Unicode(length=80), nullable=False),
    sa.Column('company', sa.Unicode(length=80), nullable=True),
    sa.Column('job', sa.Unicode(length=80), nullable=True),
    sa.Column('city', sa.Unicode(length=80), nullable=True),
    sa.Column('phone', sa.Unicode(length=25), nullable=True),
    sa.Column('twitter', sa.Unicode(length=80), nullable=True),
    sa.Column('purchased_tee', sa.Boolean(), nullable=True),
    sa.Column('regdate', sa.DateTime(), nullable=False),
    sa.Column('nfc_id', sa.Unicode(length=80), nullable=True),
    sa.Column('online_reg', sa.Boolean(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('attended', sa.Boolean(), nullable=False),
    sa.Column('attend_date', sa.DateTime(), nullable=True),
    sa.Column('purchases', sa.Unicode(length=200), nullable=True),
    sa.Column('notes', sa.Unicode(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('event_id', 'email', 'name'),
    sa.UniqueConstraint('event_id','nfc_id'),
    sa.UniqueConstraint('ticket_number')
    )
    op.create_table('kiosk_participants',
    sa.Column('kiosk_id', sa.Integer(), nullable=True),
    sa.Column('participant_id', sa.Integer(), nullable=True),
    sa.Column('share_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['kiosk_id'], ['kiosk.id'], ),
    sa.ForeignKeyConstraint(['participant_id'], ['participant.id'], ),
    sa.PrimaryKeyConstraint()
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('kiosk_participants')
    op.drop_table('participant')
    op.drop_table('kiosk')
    op.drop_table('user')
    op.drop_table('cxlog')
    op.drop_table('event')
    ### end Alembic commands ###
