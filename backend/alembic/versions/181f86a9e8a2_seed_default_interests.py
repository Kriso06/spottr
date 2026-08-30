"""seed default interests

Revision ID: 181f86a9e8a2
Revises: cf9e7a751f89
Create Date: 2026-08-31 00:28:15.914599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '181f86a9e8a2'
down_revision: Union[str, Sequence[str], None] = 'cf9e7a751f89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

interests_table = sa.table(
    "interests",
    sa.column("name", sa.String),
    sa.column("category", sa.String),
)

interest_names = [
    "Coffee",
    "Photography",
    "Gaming",
    "Movies",
    "Food",
    "Music",
    "Fitness",
    "Travel",
    "Books",
    "Coding",
    "Hiking",
    "Art",
]

def upgrade() -> None:
    op.bulk_insert(
        interests_table,
        [
            {"name": "Coffee", "category": "Food"},
            {"name": "Photography", "category": "Creative"},
            {"name": "Gaming", "category": "Entertainment"},
            {"name": "Movies", "category": "Entertainment"},
            {"name": "Food", "category": "Food"},
            {"name": "Music", "category": "Entertainment"},
            {"name": "Fitness", "category": "Wellness"},
            {"name": "Travel", "category": "Lifestyle"},
            {"name": "Books", "category": "Learning"},
            {"name": "Coding", "category": "Technology"},
            {"name": "Hiking", "category": "Outdoors"},
            {"name": "Art", "category": "Creative"},
        ],
    )



def downgrade() -> None:
    op.execute(
        sa.delete(interests_table).where(
            interests_table.c.name.in_(interest_names)
        )
    )
