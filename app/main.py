from fastapi import FastAPI, Request, Depends, Form, HTTPException, status, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, List
from functools import wraps
import secrets
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user_from_token
from app.core.password_validation import password_validator
from app.core.enums import (
    Gender, FitnessGoal, TimePreference, ExerciseType, PreferredSport,
    MedicalCondition, CommonMedication, CommonAllergy, PastInjury
)
from app.db.session import get_db
from app.db.base import User, UserProfile
from app.schemas.survey import (
    SurveyCreate, HealthConditionSchema, MedicationSchema,
    AllergySchema, InjurySchema
)
from pydantic import ValidationError

app = FastAPI(
    title=settings.PROJECT_NAME
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

def login_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        email = get_current_user_from_token(token)
        if not email:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        # Add user to request state
        request.state.user_email = email
        return await func(request, *args, **kwargs)
    return wrapper

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Incorrect email or password"},
            status_code=400
        )
    
    if not user.is_active:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Account is not active"},
            status_code=400
        )
    
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        "access_token",
        access_token,  
        httponly=True,
        max_age=1800,
        secure=False  
    )
    return response

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Passwords do not match"},
            status_code=400
        )
    
    # Validate password
    is_valid, errors = password_validator.validate(password)
    if not is_valid:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": errors[0]},
            status_code=400
        )
    
    # Check if user already exists
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered"},
            status_code=400
        )
    
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username already taken"},
            status_code=400
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Create response with redirect
    response = Response(status_code=status.HTTP_303_SEE_OTHER)
    response.headers["location"] = "/survey"
    response.set_cookie(
        "access_token",
        f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        secure=False  
    )
    return response

@app.get("/dashboard")
@login_required
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.state.user_email).first()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user
    })

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@app.get("/reset-password-request")
async def reset_password_request_page(request: Request):
    return templates.TemplateResponse("reset_password_request.html", {"request": request})

@app.post("/reset-password-request")
async def reset_password_request(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse(
            "reset_password_request.html",
            {
                "request": request,
                "error": "No account found with this email."
            }
        )
    
    # Generate reset token (simple version for POC)
    reset_token = secrets.token_urlsafe(16)  
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    
    try:
        db.commit()
        # For POC: Display the reset link directly on the page
        reset_url = f"{request.base_url}reset-password/{reset_token}"
        return templates.TemplateResponse(
            "reset_password_request.html",
            {
                "request": request,
                "success": "Password reset link generated successfully!",
                "reset_url": reset_url
            }
        )
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "reset_password_request.html",
            {"request": request, "error": "An error occurred. Please try again."}
        )

@app.get("/reset-password/{token}")
async def reset_password_page(request: Request, token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        return templates.TemplateResponse(
            "reset_password_request.html",
            {"request": request, "error": "Invalid or expired reset link. Please request a new one."}
        )
    
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})

@app.post("/reset-password/{token}")
async def reset_password(
    request: Request,
    token: str,
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        return templates.TemplateResponse(
            "reset_password_request.html",
            {"request": request, "error": "Invalid or expired reset link. Please request a new one."}
        )
    
    if password != confirm_password:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": token, "error": "Passwords do not match"}
        )
    
    # Validate password
    is_valid, errors = password_validator.validate(password)
    if not is_valid:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": token, "error": errors[0]}
        )
    
    try:
        # Update password and clear reset token
        user.hashed_password = get_password_hash(password)
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": token, "error": "An error occurred. Please try again."}
        )

@app.get("/survey")
@login_required
async def survey_page(request: Request, db: Session = Depends(get_db)):
    # Get user profile
    user_email = request.state.user_email
    user = db.query(User).filter(User.email == user_email).first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    
    return templates.TemplateResponse(
        "survey.html",
        {
            "request": request,
            "user": user,
            "profile": profile,
            "genders": list(Gender),
            "fitness_goals": list(FitnessGoal),
            "time_preferences": list(TimePreference),
            "exercise_types": list(ExerciseType),
            "preferred_sports": list(PreferredSport),
            "medical_conditions": list(MedicalCondition),
            "common_medications": list(CommonMedication),
            "common_allergies": list(CommonAllergy),
            "past_injuries": list(PastInjury)
        }
    )

@app.post("/survey")
@login_required
async def submit_survey(
    request: Request,
    survey_data: SurveyCreate = Depends(SurveyCreate.as_form),
    db: Session = Depends(get_db)
):
    """Handle survey form submission."""
    try:
        # Get current user
        email = request.state.user_email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create or update user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.add(profile)

        # Update profile with survey data
        survey_dict = survey_data.dict(exclude_unset=True)
        
        # List of fields that contain lists of enums
        list_enum_fields = [
            "exercise_types", "preferred_sports",
            "medical_conditions", "medications",
            "allergies", "past_injuries"
        ]
        
        # List of fields that are single enums
        single_enum_fields = ["gender", "fitness_goal", "time_preference"]
        
        for key, value in survey_dict.items():
            if key in list_enum_fields and value is not None:
                # Handle list of enums from form
                setattr(profile, key, value if isinstance(value, list) else [value])
            elif key in single_enum_fields and value is not None:
                # Handle single enum from form
                setattr(profile, key, value)
            else:
                # Handle non-enum fields
                setattr(profile, key, value)

        db.commit()
        return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        return templates.TemplateResponse(
            "survey.html",
            {
                "request": request,
                "errors": e.errors(),
                "values": survey_dict
            },
            status_code=422
        )
    except Exception as e:
        return templates.TemplateResponse(
            "survey.html",
            {
                "request": request,
                "error": str(e),
                "values": survey_dict
            },
            status_code=500
        )

@app.get("/profile")
@login_required
async def profile_page(request: Request, db: Session = Depends(get_db)):
    """Display user profile page."""
    email = request.state.user_email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        return RedirectResponse(url="/survey", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "user_profile": profile
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
