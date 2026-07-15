"""backfill phone number

Revision ID: c78d45ccc409
Revises: 7b27425603fc
Create Date: 2026-06-23 15:50:52.304262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c78d45ccc409'
down_revision: Union[str, Sequence[str], None] = '7b27425603fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   op.execute("""
        UPDATE python_users set phone_number = phone where phone is not null
   """)


def downgrade() -> None:
   op.execute("""
        update python_users set phone = phone_number where phone_number is not null
   """)
