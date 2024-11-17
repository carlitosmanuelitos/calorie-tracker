"""remove_specified_columns

Revision ID: 20241117_fix
Revises: df8be496aa16
Create Date: 2024-11-17 01:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '20241117_fix'
down_revision = 'df8be496aa16'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # The table is already in the desired state with only the columns we want to keep
    pass

def downgrade() -> None:
    # Add back all the removed columns if needed
    op.execute("""
    CREATE TABLE user_profiles_old (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        age INTEGER NOT NULL,
        gender VARCHAR(6) NOT NULL,
        height FLOAT NOT NULL,
        weight FLOAT NOT NULL,
        target_weight FLOAT NOT NULL,
        blood_type VARCHAR(11),
        activity_level VARCHAR(17) NOT NULL,
        experience_level VARCHAR(12) NOT NULL,
        workout_time_preference VARCHAR(9),
        daily_calorie_goal INTEGER NOT NULL,
        protein_goal INTEGER NOT NULL,
        carbs_goal INTEGER NOT NULL,
        fat_goal INTEGER NOT NULL,
        water_goal FLOAT NOT NULL,
        use_metric BOOLEAN,
        body_fat_percentage FLOAT,
        waist_circumference FLOAT,
        medical_conditions VARCHAR,
        allergies VARCHAR,
        food_intolerances JSON,
        family_health_history JSON,
        dietary_preference VARCHAR(11),
        food_preferences JSON,
        sleep_time TIME,
        wake_time TIME,
        fitness_goal VARCHAR(15),
        workout_frequency INTEGER,
        preferred_workout_types VARCHAR,
        weight_goal_rate FLOAT,
        meal_preferences JSON,
        notification_preferences JSON,
        tracking_frequency JSON,
        created_at DATETIME,
        updated_at DATETIME,
        FOREIGN KEY(user_id) REFERENCES users(id),
        UNIQUE(user_id)
    )
    """)

    # Copy existing data
    op.execute("""
    INSERT INTO user_profiles_old (
        id, user_id, age, gender, height, weight, target_weight,
        activity_level, experience_level, body_fat_percentage,
        waist_circumference, medical_conditions, allergies,
        fitness_goal, workout_frequency, preferred_workout_types,
        created_at, updated_at
    )
    SELECT * FROM user_profiles
    """)

    # Drop current table and rename the new one
    op.execute("DROP TABLE user_profiles")
    op.execute("ALTER TABLE user_profiles_old RENAME TO user_profiles")
