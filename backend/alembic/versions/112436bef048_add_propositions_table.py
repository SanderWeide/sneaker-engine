"""Add propositions table

Revision ID: 112436bef048
Revises: 67af63af6319
Create Date: 2025-12-29 20:12:07.291817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '112436bef048'
down_revision: Union[str, None] = '67af63af6319'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'propositions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('buyer_id', sa.Integer(), nullable=True),
        sa.Column('sneaker_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('agreed_datetime', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['sneaker_id'], ['sneakers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_propositions_id'), 'propositions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_propositions_id'), table_name='propositions')
    op.drop_table('propositions')
