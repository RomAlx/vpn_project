"""vpn updates

Revision ID: c5b93e2bd3c4
Revises: 83645c429b4f
Create Date: 2024-09-10 15:10:48.144560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c5b93e2bd3c4'
down_revision: Union[str, None] = '83645c429b4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vpn_keys', sa.Column('uuid', sa.String(length=255), nullable=False))
    op.add_column('vpn_keys', sa.Column('client_id', sa.String(length=255), nullable=False))
    op.drop_column('vpn_keys', 'key')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vpn_keys', sa.Column('key', mysql.VARCHAR(length=255), nullable=False))
    op.drop_column('vpn_keys', 'client_id')
    op.drop_column('vpn_keys', 'uuid')
    # ### end Alembic commands ###
