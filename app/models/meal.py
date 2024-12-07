from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Table
from sqlalchemy.orm import relationship
from ..db.base_class import Base
import enum

class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class FoodCategory(str, enum.Enum):
    PROTEIN = "protein"
    CARB = "carb"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    DAIRY = "dairy"
    FAT = "fat"
    OTHER = "other"

class UnitType(str, enum.Enum):
    GRAMS = "g"
    OUNCES = "oz"
    CUPS = "cups"
    PIECES = "pcs"
    SERVINGS = "servings"

class MealLog(Base):
    """Model for logging meals"""
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    meal_type = Column(Enum(MealType), nullable=False)
    is_favorite = Column(Boolean, default=False)
    notes = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="meal_logs")
    components = relationship("MealComponent", back_populates="meal_log", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "meal_type": self.meal_type,
            "is_favorite": self.is_favorite,
            "notes": self.notes,
            "components": [comp.to_dict() for comp in self.components]
        }

class MealComponent(Base):
    """Model for individual food components in a meal"""
    __tablename__ = "meal_components"

    id = Column(Integer, primary_key=True, index=True)
    meal_log_id = Column(Integer, ForeignKey("meal_logs.id"), nullable=False)
    food_item = Column(String, nullable=False)
    category = Column(Enum(FoodCategory), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(Enum(UnitType), nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    
    # Relationships
    meal_log = relationship("MealLog", back_populates="components")

    def to_dict(self):
        return {
            "id": self.id,
            "food_item": self.food_item,
            "category": self.category,
            "quantity": self.quantity,
            "unit": self.unit,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat
        }

class FavoriteMeal(Base):
    """Model for saving favorite/template meals"""
    __tablename__ = "favorite_meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    meal_type = Column(Enum(MealType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="favorite_meals")
    components = relationship("FavoriteMealComponent", back_populates="favorite_meal", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "meal_type": self.meal_type,
            "created_at": self.created_at.isoformat(),
            "components": [comp.to_dict() for comp in self.components]
        }

class FavoriteMealComponent(Base):
    """Model for components in favorite/template meals"""
    __tablename__ = "favorite_meal_components"

    id = Column(Integer, primary_key=True, index=True)
    favorite_meal_id = Column(Integer, ForeignKey("favorite_meals.id"), nullable=False)
    food_item = Column(String, nullable=False)
    category = Column(Enum(FoodCategory), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(Enum(UnitType), nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    
    # Relationships
    favorite_meal = relationship("FavoriteMeal", back_populates="components")

    def to_dict(self):
        return {
            "id": self.id,
            "food_item": self.food_item,
            "category": self.category,
            "quantity": self.quantity,
            "unit": self.unit,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat
        }
