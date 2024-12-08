from app.db.base_class import Base  # noqa

# Import models after Base to avoid circular imports
from app.models.user import User, UserProfile  # noqa
from app.models.exercise import ExerciseLog, ExerciseComponent  # noqa
from app.models.meal import MealLog, MealComponent, FavoriteMeal, FavoriteMealComponent  # noqa
from app.models.knowledge import KnowledgeCategory, Comment  # noqa
from app.core.enums import Gender, FitnessGoal, TimePreference, ExerciseType, PreferredSport  # noqa

__all__ = [
    "Base",
    "User",
    "UserProfile",
    "ExerciseLog",
    "ExerciseComponent",
    "MealLog", 
    "MealComponent", 
    "FavoriteMeal", 
    "FavoriteMealComponent",
    "KnowledgeCategory",
    "Comment",
    "Gender",
    "FitnessGoal",
    "TimePreference",
    "ExerciseType",
    "PreferredSport"
]
