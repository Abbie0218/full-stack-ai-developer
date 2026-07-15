"""added phone column

Revision ID: 28dbabd8f565
Revises: f891e3eb23a8
Create Date: 2026-06-23 15:26:56.253738

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '28dbabd8f565'
down_revision: Union[str, Sequence[str], None] = 'f891e3eb23a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('python_users',
        sa.Column('phone_number', sa.String(length=20), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('python_users', 'phone') 