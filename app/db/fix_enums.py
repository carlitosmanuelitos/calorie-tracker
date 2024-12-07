from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..models.meal import MealType, FoodCategory, UnitType
from ..db.session import get_db
from ..db.base import Base

def fix_enum_values():
    """Fix existing enum values in the database to match the correct format."""
    db = next(get_db())
    try:
        # Fix meal_type values in meal_logs
        db.execute(text("""
            UPDATE meal_logs 
            SET meal_type = REPLACE(UPPER(REPLACE(meal_type, 'mealtype.', '')), ' ', '_')
            WHERE meal_type LIKE 'mealtype.%'
        """))

        # Fix category values in meal_components
        db.execute(text("""
            UPDATE meal_components 
            SET category = REPLACE(UPPER(REPLACE(category, 'foodcategory.', '')), ' ', '_')
            WHERE category LIKE 'foodcategory.%'
        """))

        # Fix unit values in meal_components
        db.execute(text("""
            UPDATE meal_components 
            SET unit = REPLACE(UPPER(REPLACE(unit, 'unittype.', '')), ' ', '_')
            WHERE unit LIKE 'unittype.%'
        """))

        db.commit()
        print("Successfully updated enum values in the database.")
    except Exception as e:
        db.rollback()
        print(f"Error updating enum values: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_enum_values()
