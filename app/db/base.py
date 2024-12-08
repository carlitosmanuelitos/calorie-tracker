"""Import all models and setup Base."""
from app.db.base_class import Base  # noqa
from app.models.user import User, UserProfile  # noqa
from app.models.knowledge import KnowledgeCategory, Comment  # noqa
from app.models.exercise import ExerciseLog, ExerciseComponent  # noqa
from app.core.enums import Gender, FitnessGoal, TimePreference, ExerciseType, PreferredSport  # noqa

# Import all models here for Alembic autogeneration
__all__ = ["Base", "User", "UserProfile", "KnowledgeCategory", "Comment", 
           "Gender", "FitnessGoal", "TimePreference", "ExerciseType", "PreferredSport",
           "ExerciseLog", "ExerciseComponent"]
