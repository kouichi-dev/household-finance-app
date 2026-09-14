"""rename refresh_tokens token to token_hash

Revision ID: 4370c5418281
Revises: 694d2d9d3a71
Create Date: 2026-09-14 11:38:21.132155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4370c5418281'
down_revision: Union[str, Sequence[str], None] = '694d2d9d3a71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('refresh_tokens', 'token', new_column_name='token_hash')
    op.execute("UPDATE refresh_tokens SET token_hash = encode(sha256(convert_to(token_hash, 'UTF8')), 'hex')")

def downgrade() -> None:
    op.execute("DELETE FROM refresh_tokens")
    op.alter_column('refresh_tokens', 'token_hash', new_column_name='token')

