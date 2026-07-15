"""add phone_number column

Revision ID: 7b27425603fc
Revises: 28dbabd8f565
Create Date: 2026-06-23 15:50:23.419902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b27425603fc'
down_revision: Union[str, Sequence[str], None] = '28dbabd8f565'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('python_users',
                sa.Column('phone_number', sa.String(20), nullable=True)
                )

def downgrade() -> None:
    op.drop_column('python_users','phone_number')