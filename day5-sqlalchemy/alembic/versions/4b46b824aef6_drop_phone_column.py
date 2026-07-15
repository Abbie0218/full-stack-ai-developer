"""drop phone column

Revision ID: 4b46b824aef6
Revises: c78d45ccc409
Create Date: 2026-06-23 15:51:21.556538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b46b824aef6'
down_revision: Union[str, Sequence[str], None] = 'c78d45ccc409'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("python_users","phone")


def downgrade() -> None:
    op.add_column("python_users",sa.Column("phone",sa.String(20),nullable=True))