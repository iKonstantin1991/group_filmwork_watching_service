"""add total price for reservation

Revision ID: be2dd49ec774
Revises: e656a8ee9fa0
Create Date: 2024-09-01 14:58:31.567787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be2dd49ec774'
down_revision: Union[str, None] = 'e656a8ee9fa0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'reservations',
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reservations', 'total_price')
    # ### end Alembic commands ###
