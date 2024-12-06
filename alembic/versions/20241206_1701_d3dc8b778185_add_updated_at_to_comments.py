"""add updated_at to comments

Revision ID: d3dc8b778185
Revises: 6c26aec768de
Create Date: 2024-12-06 17:01:12.345678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = 'd3dc8b778185'
down_revision: Union[str, None] = '6c26aec768de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary table with the new column
    op.execute("""
        CREATE TABLE comments_new (
            id INTEGER PRIMARY KEY,
            category_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY(category_id) REFERENCES knowledge_categories(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    # Copy data from old table to new table
    op.execute("""
        INSERT INTO comments_new 
        SELECT id, category_id, user_id, content, likes, created_at, created_at 
        FROM comments
    """)
    
    # Drop old table
    op.execute("DROP TABLE comments")
    
    # Rename new table to old table name
    op.execute("ALTER TABLE comments_new RENAME TO comments")


def downgrade() -> None:
    # Create a temporary table without the updated_at column
    op.execute("""
        CREATE TABLE comments_new (
            id INTEGER PRIMARY KEY,
            category_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            created_at DATETIME NOT NULL,
            FOREIGN KEY(category_id) REFERENCES knowledge_categories(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    # Copy data from old table to new table
    op.execute("""
        INSERT INTO comments_new 
        SELECT id, category_id, user_id, content, likes, created_at 
        FROM comments
    """)
    
    # Drop old table
    op.execute("DROP TABLE comments")
    
    # Rename new table to old table name
    op.execute("ALTER TABLE comments_new RENAME TO comments")
