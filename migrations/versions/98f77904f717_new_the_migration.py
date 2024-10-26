"""New the migration

Revision ID: 98f77904f717
Revises: 20230101
Create Date: 2024-10-06 10:25:36.887982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '98f77904f717'
down_revision: Union[str, None] = '20230101'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Создаем временную таблицу для task
    op.create_table(
        'task_temp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )

    # Копируем данные из старой таблицы task в новую таблицу task_temp
    op.execute('INSERT INTO task_temp (id, title, description, status, user_id) SELECT id, title, description, status, user_id FROM task')

    # Удаляем старую таблицу task
    op.drop_table('task')

    # Переименовываем временную таблицу task_temp в task
    op.rename_table('task_temp', 'task')

def downgrade() -> None:
    # Создаем временную таблицу для task
    op.create_table(
        'task_temp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )

    # Копируем данные из старой таблицы task в новую таблицу task_temp
    op.execute('INSERT INTO task_temp (id, title, description, status, user_id) SELECT id, title, description, status, user_id FROM task')

    # Удаляем старую таблицу task
    op.drop_table('task')

    # Переименовываем временную таблицу task_temp в task
    op.rename_table('task_temp', 'task')