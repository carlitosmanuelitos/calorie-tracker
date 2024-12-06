from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi import Request
import json

from app.core.enums import (
    Gender, FitnessGoal, TimePreference, ExerciseType, PreferredSport,
    MedicalCondition, CommonMedication, CommonAllergy, PastInjury
)

class HealthConditionSchema(BaseModel):
    condition: MedicalCondition
    details: Optional[str] = None
    diagnosed_year: Optional[int] = None
    is_current: bool = True

class MedicationSchema(BaseModel):
    medication: CommonMedication
    details: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None

class AllergySchema(BaseModel):
    allergy: CommonAllergy
    details: Optional[str] = None
    severity: Optional[str] = None
    diagnosed_year: Optional[int] = None

class InjurySchema(BaseModel):
    injury: PastInjury
    details: Optional[str] = None
    year: Optional[int] = None
    is_recovered: bool = True
    affects_exercise: bool = False

class SurveyCreate(BaseModel):
    # Basic Information
    age: int = Field(..., ge=13, le=120)
    gender: Gender
    height: float = Field(..., ge=100, le=250)  # in cm
    weight: float = Field(..., ge=30, le=300)   # in kg
    target_weight: float = Field(..., ge=30, le=300)  # in kg
    
    # Medical Information
    medical_conditions: List[MedicalCondition] = []
    medications: List[CommonMedication] = []
    allergies: List[CommonAllergy] = []
    past_injuries: List[PastInjury] = []
    
    # Activity Information
    fitness_goal: FitnessGoal
    time_preference: TimePreference
    exercise_types: List[ExerciseType] = []
    preferred_sports: List[PreferredSport] = []
    exercise_notes: Optional[str] = None
    
    # Nutrition Goals
    daily_calorie_goal: int = Field(..., ge=1200, le=8000)
    protein_goal: int = Field(..., ge=0, le=400)
    carbs_goal: int = Field(..., ge=0, le=600)
    fat_goal: int = Field(..., ge=0, le=200)
    water_goal: float = Field(..., ge=1, le=10)
    
    # Lifestyle Information
    sleep_hours: float = Field(..., ge=4, le=12)
    stress_level: int = Field(..., ge=1, le=5)
    meal_frequency: int = Field(..., ge=2, le=8)

    @classmethod
    async def as_form(cls, request: Request):
        """
        Parse a SurveyCreate object from a FastAPI request form.

        This method is used to parse a FastAPI request form into a SurveyCreate
        object. It handles enum fields, list enum fields, and medical multi-select
        fields.
        """
        form_data = await request.form()
        data = {}
        
        # Handle basic fields
        for field in ["age", "height", "weight", "target_weight", 
                     "daily_calorie_goal", "protein_goal", "carbs_goal", 
                     "fat_goal", "water_goal", "sleep_hours", "stress_level", 
                     "meal_frequency"]:
            if field in form_data:
                data[field] = float(form_data[field]) if field in ["height", "weight", "target_weight", "water_goal", "sleep_hours"] else int(form_data[field])
        
        # Handle enum fields
        if "gender" in form_data:
            data["gender"] = Gender(form_data["gender"])
        if "fitness_goal" in form_data:
            data["fitness_goal"] = FitnessGoal(form_data["fitness_goal"])
        if "time_preference" in form_data:
            data["time_preference"] = TimePreference(form_data["time_preference"])
        
        # Handle list enum fields
        if "exercise_types" in form_data:
            exercise_types = form_data.getlist("exercise_types")
            data["exercise_types"] = [ExerciseType(t) for t in (exercise_types if isinstance(exercise_types, list) else [exercise_types])]
        
        if "preferred_sports" in form_data:
            preferred_sports = form_data.getlist("preferred_sports")
            data["preferred_sports"] = [PreferredSport(s) for s in (preferred_sports if isinstance(preferred_sports, list) else [preferred_sports])]

        # Handle medical multi-select fields
        if "medical_conditions" in form_data:
            conditions = form_data.getlist("medical_conditions")
            data["medical_conditions"] = [MedicalCondition(c) for c in (conditions if isinstance(conditions, list) else [conditions])]
        
        if "medications" in form_data:
            meds = form_data.getlist("medications")
            data["medications"] = [CommonMedication(m) for m in (meds if isinstance(meds, list) else [meds])]
        
        if "allergies" in form_data:
            allergies = form_data.getlist("allergies")
            data["allergies"] = [CommonAllergy(a) for a in (allergies if isinstance(allergies, list) else [allergies])]
        
        if "past_injuries" in form_data:
            injuries = form_data.getlist("past_injuries")
            data["past_injuries"] = [PastInjury(i) for i in (injuries if isinstance(injuries, list) else [injuries])]
        
        # Handle optional text field
        if "exercise_notes" in form_data:
            data["exercise_notes"] = form_data["exercise_notes"]
        
        return cls(**data)
