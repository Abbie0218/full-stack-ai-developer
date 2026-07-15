"""add users table

Revision ID: f891e3eb23a8
Revises: 
Create Date: 2026-06-23 15:21:17.746727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f891e3eb23a8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   pass


def downgrade() -> None:
   pass
