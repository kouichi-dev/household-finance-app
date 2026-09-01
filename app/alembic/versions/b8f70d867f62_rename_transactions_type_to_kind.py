"""rename transactions.type to kind

Revision ID: b8f70d867f62
Revises: e6887590b77d
Create Date: 2026-09-01 18:11:50.948002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8f70d867f62'
down_revision: Union[str, Sequence[str], None] = 'e6887590b77d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('ck_transactions_type', 'transactions', type_='check')
    op.alter_column('transactions', 'type', new_column_name='kind')
    op.create_check_constraint('ck_transactions_kind', 'transactions', "kind IN ('income','expense')")

def downgrade() -> None:
    op.drop_constraint('ck_transactions_kind', 'transactions', type_='check')
    op.alter_column('transactions', 'kind', new_column_name='type')
    op.create_check_constraint('ck_transactions_type', 'transactions', "type IN ('income','expense')")

