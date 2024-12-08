from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from enum import Enum
from typing import Optional
from datetime import datetime

from app.db.base_class import Base

class ExerciseType(str, Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    HIIT = "hiit"

class ExerciseCategory(str, Enum):
    WEIGHT_TRAINING = "weight_training"
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    YOGA = "yoga"
    BODYWEIGHT = "bodyweight"
    OTHER = "other"

class ExerciseIntensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ExerciseLog(Base):
    __tablename__ = 'exercise_logs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    exercise_type = Column(SQLAlchemyEnum(ExerciseType), nullable=False)
    duration = Column(Float, nullable=False)  # in minutes
    intensity = Column(SQLAlchemyEnum(ExerciseIntensity), nullable=False)
    total_calories_burned = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)

    # Relationship to exercise components
    components = relationship("ExerciseComponent", back_populates="exercise_log", cascade="all, delete-orphan")

    # Relationship to user
    user = relationship("User", back_populates="exercise_logs")

class ExerciseComponent(Base):
    __tablename__ = 'exercise_components'

    id = Column(Integer, primary_key=True, index=True)
    exercise_log_id = Column(Integer, ForeignKey('exercise_logs.id'), nullable=False)
    exercise_name = Column(String, nullable=False)
    category = Column(SQLAlchemyEnum(ExerciseCategory), nullable=False)
    
    # Strength training specific
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # in kg or lbs
    
    # Cardio specific
    distance = Column(Float, nullable=True)  # in km or miles
    
    # Common metrics
    calories_burned = Column(Integer, nullable=True)

    # Relationship to exercise log
    exercise_log = relationship("ExerciseLog", back_populates="components")
