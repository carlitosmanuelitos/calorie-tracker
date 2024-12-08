from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Enum
from datetime import datetime

from app.db.base_class import Base
from app.core.enums import (
    Gender, FitnessGoal, TimePreference, ExerciseType, PreferredSport,
    MedicalCondition, CommonMedication, CommonAllergy, PastInjury
)
from app.models.exercise import ExerciseLog

class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    
    # User preferences
    theme = Column(String, nullable=True)
    language = Column(String, nullable=True)
    reset_token = Column(String, unique=True, index=True, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    meal_logs = relationship("MealLog", back_populates="user", cascade="all, delete-orphan")
    favorite_meals = relationship("FavoriteMeal", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user")
    exercise_logs = relationship("ExerciseLog", back_populates="user")

class UserProfile(Base):
    """User profile model for storing user preferences and health data"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="profile")
    
    # Step 1: Basic Information
    age = Column(Integer, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    height = Column(Float, nullable=False)  # in cm
    weight = Column(Float, nullable=False)  # in kg
    target_weight = Column(Float, nullable=False)  # in kg

    # Step 2: Medical Information
    medical_conditions = Column(JSON, nullable=True, default=list)  # List of MedicalCondition values
    medications = Column(JSON, nullable=True, default=list)  # List of CommonMedication values
    allergies = Column(JSON, nullable=True, default=list)  # List of CommonAllergy values
    past_injuries = Column(JSON, nullable=True, default=list)  # List of PastInjury values

    # Step 3: Activity Information
    fitness_goal = Column(Enum(FitnessGoal), nullable=False)
    time_preference = Column(Enum(TimePreference), nullable=False)
    exercise_types = Column(JSON, nullable=False)  # List of ExerciseType values
    preferred_sports = Column(JSON, nullable=False, default=list)  # List of PreferredSport values
    exercise_notes = Column(String, nullable=True)

    # Step 4: Nutrition Goals
    daily_calorie_goal = Column(Integer, nullable=False)
    protein_goal = Column(Integer, nullable=False)  # in grams
    carbs_goal = Column(Integer, nullable=False)   # in grams
    fat_goal = Column(Integer, nullable=False)     # in grams
    water_goal = Column(Float, nullable=False)     # in liters
    
    # Step 5: Lifestyle Information
    sleep_hours = Column(Float, nullable=False)
    stress_level = Column(Integer, nullable=False)  # 1-5 scale
    meal_frequency = Column(Integer, nullable=False)  # meals per day
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
