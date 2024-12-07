"""add meal tracking models

Revision ID: a5207d6d24c9
Revises: d3dc8b778185
Create Date: 2024-12-07 00:37:12.345678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = 'a5207d6d24c9'
down_revision: Union[str, None] = 'd3dc8b778185'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create meal_logs table
    op.create_table('meal_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('meal_type', sa.Enum('breakfast', 'lunch', 'dinner', 'snack', name='mealtype'), nullable=False),
        sa.Column('is_favorite', sa.Boolean(), default=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meal_logs_id'), 'meal_logs', ['id'], unique=False)

    # Create meal_components table
    op.create_table('meal_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meal_log_id', sa.Integer(), nullable=False),
        sa.Column('food_item', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('protein', 'carb', 'vegetable', 'fruit', 'dairy', 'fat', 'other', name='foodcategory'), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.Enum('g', 'oz', 'cups', 'pcs', 'servings', name='unittype'), nullable=False),
        sa.Column('calories', sa.Float(), nullable=False),
        sa.Column('protein', sa.Float(), nullable=True),
        sa.Column('carbs', sa.Float(), nullable=True),
        sa.Column('fat', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['meal_log_id'], ['meal_logs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meal_components_id'), 'meal_components', ['id'], unique=False)

    # Create favorite_meals table
    op.create_table('favorite_meals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('meal_type', sa.Enum('breakfast', 'lunch', 'dinner', 'snack', name='mealtype'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_favorite_meals_id'), 'favorite_meals', ['id'], unique=False)

    # Create favorite_meal_components table
    op.create_table('favorite_meal_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('favorite_meal_id', sa.Integer(), nullable=False),
        sa.Column('food_item', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('protein', 'carb', 'vegetable', 'fruit', 'dairy', 'fat', 'other', name='foodcategory'), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.Enum('g', 'oz', 'cups', 'pcs', 'servings', name='unittype'), nullable=False),
        sa.Column('calories', sa.Float(), nullable=False),
        sa.Column('protein', sa.Float(), nullable=True),
        sa.Column('carbs', sa.Float(), nullable=True),
        sa.Column('fat', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['favorite_meal_id'], ['favorite_meals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_favorite_meal_components_id'), 'favorite_meal_components', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_favorite_meal_components_id'), table_name='favorite_meal_components')
    op.drop_table('favorite_meal_components')
    op.drop_index(op.f('ix_favorite_meals_id'), table_name='favorite_meals')
    op.drop_table('favorite_meals')
    op.drop_index(op.f('ix_meal_components_id'), table_name='meal_components')
    op.drop_table('meal_components')
    op.drop_index(op.f('ix_meal_logs_id'), table_name='meal_logs')
    op.drop_table('meal_logs')
