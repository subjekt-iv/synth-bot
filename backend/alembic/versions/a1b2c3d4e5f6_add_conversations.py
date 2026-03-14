"""Add conversations

Revision ID: a1b2c3d4e5f6
Revises: 5d4db55aa066
Create Date: 2026-03-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '5d4db55aa066'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('conversations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('chats', sa.Column('conversation_id', sa.String(), nullable=True))
    op.create_foreign_key('fk_chats_conversation_id', 'chats', 'conversations', ['conversation_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_chats_conversation_id', 'chats', type_='foreignkey')
    op.drop_column('chats', 'conversation_id')
    op.drop_table('conversations')
