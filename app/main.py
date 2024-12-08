from fastapi import FastAPI, Request, Depends, Form, HTTPException, status, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from functools import wraps
import secrets
from datetime import datetime, timedelta
from calendar import monthcalendar
from sqlalchemy.orm import selectinload
from .models.meal import MealLog, MealComponent, FavoriteMeal, FavoriteMealComponent, MealType, FoodCategory, UnitType

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user_from_token
from app.core.password_validation import password_validator
from app.core.enums import (
    Gender, FitnessGoal, TimePreference, ExerciseType, PreferredSport,
    MedicalCondition, CommonMedication, CommonAllergy, PastInjury
)
from app.db.session import get_db
from app.db.base import User, UserProfile
from app.models.knowledge import KnowledgeCategory, Comment
from app.schemas.survey import (
    SurveyCreate, HealthConditionSchema, MedicationSchema,
    AllergySchema, InjurySchema
)
from app.schemas.knowledge import KnowledgeCategoryCreate, CommentCreate
from pydantic import ValidationError
from .models.meal import MealLog, MealComponent, FavoriteMeal, FavoriteMealComponent, MealType, FoodCategory, UnitType

"""
FastAPI application for the Calorie Tracker web application.

This application provides API endpoints for user authentication, survey completion, and health data tracking.

The application is configured via environment variables. The following variables are required:

* `SECRET_KEY`: Secret key for secure password hashing and JWT token signing.
* `DATABASE_URL`: URL for the database connection.
* `FIRST_SUPERUSER_EMAIL`: Email address of the first superuser.
* `FIRST_SUPERUSER_PASSWORD`: Password of the first superuser.

The application is divided into the following modules:

* `app.core`: Core functionality, including security, password validation, and user authentication.
* `app.db`: Database models and database session management.
* `app.schemas`: Pydantic models for API endpoints.
* `app.routes`: API endpoints and route handlers.
"""
app = FastAPI(
    title=settings.PROJECT_NAME
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Add custom Jinja2 filters
def month_name(month_number):
    """Convert month number to month name."""
    return datetime(2000, month_number, 1).strftime('%B')

templates.env.filters["month_name"] = month_name

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
        
        # Get user from database
        db = next(get_db())
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        # Add user to request state
        request.state.user = user
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
    user = db.query(User).filter(User.email == request.state.user.email).first()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user
    })

@app.get("/logout")
@app.post("/logout")
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
    user_email = request.state.user.email
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
        email = request.state.user.email
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
    email = request.state.user.email
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

@app.get("/knowledge-base")
@login_required
async def knowledge_base(request: Request, db: Session = Depends(get_db)):
    """Display knowledge base categories."""
    categories = db.query(KnowledgeCategory).all()
    return templates.TemplateResponse(
        "knowledge_base.html",
        {"request": request, "categories": categories}
    )

@app.get("/knowledge-base/{category_id}")
@login_required
async def view_category(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db)
):
    """Display a specific knowledge category with its comments."""
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return templates.TemplateResponse(
        "knowledge_category.html",
        {
            "request": request, 
            "category": category,
            "current_user": request.state.user
        }
    )

@app.post("/knowledge-base/{category_id}/comments")
@login_required
async def add_comment(
    request: Request,
    category_id: int,
    comment_text: str = Form(...),
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    comment = Comment(
        category_id=category_id,
        user_id=user.id,
        content=comment_text,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    try:
        db.add(comment)
        db.commit()
        db.refresh(comment)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return RedirectResponse(url=f"/knowledge-base/{category_id}", status_code=303)

@app.post("/knowledge-base/comments/{comment_id}/like")
@login_required
async def like_comment(request: Request, comment_id: int, db: Session = Depends(get_db)):
    """Like a comment."""
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Increment likes
    comment.likes = (comment.likes or 0) + 1
    db.commit()

    # Return to the category page
    return RedirectResponse(
        url=f"/knowledge-base/{comment.category_id}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@app.post("/knowledge-base/comments/{comment_id}/delete")
@login_required
async def delete_comment(
    request: Request,
    comment_id: int,
    db: Session = Depends(get_db)
):
    """Delete a comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != request.state.user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    category_id = comment.category_id
    db.delete(comment)
    db.commit()
    
    return RedirectResponse(
        url=f"/knowledge-base/{category_id}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@app.get("/meal-tracker")
@login_required
async def meal_tracker_home(request: Request, db: Session = Depends(get_db)):
    """Meal tracker home page - redirects to current month."""
    today = datetime.now()
    return RedirectResponse(
        url=f"/meal-tracker/{today.year}/{today.month}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@app.get("/meal-tracker/view/{date}")
@login_required
async def view_day(request: Request, date: str, db: Session = Depends(get_db)):
    """Show detailed view of a specific day's meals."""
    user = request.state.user
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        # Parse the date string to datetime in UTC
        view_date = datetime.strptime(f"{date} 00:00:00", '%Y-%m-%d %H:%M:%S')
        next_day = datetime.strptime(f"{date} 23:59:59", '%Y-%m-%d %H:%M:%S')
        
        # Get all meals for the specified day
        meals = (
            db.query(MealLog)
            .filter(
                MealLog.user_id == user.id,
                MealLog.date >= view_date,
                MealLog.date <= next_day
            )
            .options(selectinload(MealLog.components))
            .order_by(MealLog.date)
            .all()
        )
        
        # Calculate totals for each meal and the day
        day_totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        meal_details = []
        
        for meal in meals:
            meal_totals = {
                "meal_type": meal.meal_type.value,
                "date": meal.date.strftime('%Y-%m-%d %H:%M:%S'),
                "total_calories": sum(c.calories or 0 for c in meal.components),
                "total_protein": sum(c.protein or 0 for c in meal.components),
                "total_carbs": sum(c.carbs or 0 for c in meal.components),
                "total_fat": sum(c.fat or 0 for c in meal.components)
            }
            day_totals["calories"] += meal_totals["total_calories"]
            day_totals["protein"] += meal_totals["total_protein"]
            day_totals["carbs"] += meal_totals["total_carbs"]
            day_totals["fat"] += meal_totals["total_fat"]
            meal_details.append(meal_totals)
        
        return {
            "meals": meal_details,
            "totals": day_totals
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/meal-tracker/{year}/{month}")
@login_required
async def meal_tracker(
    request: Request,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Meal tracker page."""
    user = request.state.user
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # If no year/month provided, use current date
    today = datetime.now()
    year = year or today.year
    month = month or today.month

    # Calculate previous and next month
    if month == 1:
        prev_month = datetime(year - 1, 12, 1)
    else:
        prev_month = datetime(year, month - 1, 1)
        
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
        end_date = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
        end_date = datetime(year, month + 1, 1)

    # Get start date for current month
    start_date = datetime(year, month, 1)

    # Get meal logs for the specified month
    meal_logs = db.query(MealLog)\
        .filter(
            MealLog.user_id == user.id,
            MealLog.date >= start_date,
            MealLog.date < end_date
        )\
        .order_by(MealLog.date.desc())\
        .all()

    # Generate calendar weeks
    cal = monthcalendar(year, month)
    calendar_weeks = []
    meal_dates = {meal.date.date() for meal in meal_logs}
    
    for week in cal:
        calendar_week = []
        for day in week:
            if day == 0:
                calendar_week.append({"date": None})
            else:
                current_date = datetime(year, month, day).date()
                calendar_week.append({
                    "date": current_date,
                    "has_meals": current_date in meal_dates
                })
        calendar_weeks.append(calendar_week)

    # Pass enum values and navigation data to template
    return templates.TemplateResponse(
        "meal_tracker.html",
        {
            "request": request,
            "meal_logs": meal_logs,
            "meal_types": list(MealType),
            "food_categories": list(FoodCategory),
            "unit_types": list(UnitType),
            "year": year,
            "month": month,
            "today": today.date(),
            "prev_month": prev_month,
            "next_month": next_month,
            "current_user": user,
            "calendar_weeks": calendar_weeks
        }
    )

@app.post("/meal-tracker/add-meal")
@login_required
async def add_meal(
    request: Request,
    date: str = Form(...),
    time: str = Form(...),
    meal_type: str = Form(...),
    favorite_meal: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Add a new meal log."""
    user = request.state.user
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        # Parse the date and time
        meal_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Create new meal log with proper enum value
        new_meal = MealLog(
            user_id=user.id,
            date=meal_datetime,
            meal_type=MealType(meal_type.lower()),  # Convert string to enum
            notes=notes
        )
        db.add(new_meal)
        db.flush()  # This assigns the ID to new_meal without committing the transaction
        
        # Get form data for components
        form_data = await request.form()
        component_data = []
        
        # Process each form field to extract component data
        for key, value in form_data.items():
            if key.startswith('components[') and '][food_item]' in key:
                # Extract the index from the key
                index = key[key.find('[')+1:key.find(']')]
                
                # Get all related component fields
                food_item = form_data.get(f'components[{index}][food_item]')
                category = form_data.get(f'components[{index}][category]')
                quantity = float(form_data.get(f'components[{index}][quantity]', 0))
                unit = form_data.get(f'components[{index}][unit]')
                calories = float(form_data.get(f'components[{index}][calories]', 0))
                protein = float(form_data.get(f'components[{index}][protein]', 0))
                carbs = float(form_data.get(f'components[{index}][carbs]', 0))
                fat = float(form_data.get(f'components[{index}][fat]', 0))
                
                if food_item and category:  # Only add if required fields are present
                    component = MealComponent(
                        meal_log_id=new_meal.id,  # Now we have the meal_log_id
                        food_item=food_item,
                        category=FoodCategory(category.lower()),  # Convert string to enum
                        quantity=quantity,
                        unit=UnitType(unit.lower()),  # Convert string to enum
                        calories=calories,
                        protein=protein,
                        carbs=carbs,
                        fat=fat
                    )
                    db.add(component)
        
        db.commit()
        
        # Redirect back to the meal tracker page
        return RedirectResponse(
            url=f"/meal-tracker/{meal_datetime.year}/{meal_datetime.month}",
            status_code=status.HTTP_303_SEE_OTHER
        )
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/meals")
@login_required
async def add_meal(
    request: Request,
    date: str = Form(...),
    time: str = Form(...),
    meal_type: str = Form(...),
    favorite_meal: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Add a new meal log."""
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Parse the date and time
        meal_date = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Create meal log
        meal = MealLog(
            user_id=user.id,
            date=meal_date,
            meal_type=meal_type,
            notes=notes
        )
        db.add(meal)
        
        # Add components
        form_data = await request.form()
        for key, value in form_data.items():
            if key.startswith('components[') and '][food_item]' in key:
                # Extract the index from the key
                index = key[key.find('[')+1:key.find(']')]
                
                # Get all related component fields
                food_item = form_data.get(f'components[{index}][food_item]')
                category = form_data.get(f'components[{index}][category]')
                quantity = float(form_data.get(f'components[{index}][quantity]', 0))
                unit = form_data.get(f'components[{index}][unit]')
                calories = float(form_data.get(f'components[{index}][calories]', 0))
                protein = float(form_data.get(f'components[{index}][protein]', 0))
                carbs = float(form_data.get(f'components[{index}][carbs]', 0))
                fat = float(form_data.get(f'components[{index}][fat]', 0))
                
                if food_item and category:  # Only add if required fields are present
                    component = MealComponent(
                        meal_id=meal.id,
                        food_item=food_item,
                        category=category,
                        quantity=quantity,
                        unit=unit,
                        calories=calories,
                        protein=protein,
                        carbs=carbs,
                        fat=fat
                    )
                    db.add(component)
        
        db.commit()
        return {"message": "Meal added successfully", "id": meal.id}
    
    finally:
        db.close()

@app.get("/api/meals/{meal_id}")
@login_required
async def get_meal(request: Request, meal_id: int, db: Session = Depends(get_db)):
    """Get a specific meal log."""
    user = request.state.user
    if not user:
        return JSONResponse(
            status_code=401, 
            content={"detail": "Not authenticated"}
        )
    
    try:
        meal = (
            db.query(MealLog)
            .filter(MealLog.id == meal_id, MealLog.user_id == user.id)
            .first()
        )
        
        if not meal:
            return JSONResponse(
                status_code=404, 
                content={"detail": "Meal not found"}
            )
        
        return JSONResponse(content={
            "id": meal.id,
            "datetime": meal.date.strftime("%Y-%m-%dT%H:%M"),
            "meal_type": meal.meal_type.value,
            "components": [
                {
                    "food_item": c.food_item,
                    "category": c.category.value,
                    "quantity": c.quantity,
                    "unit": c.unit.value,
                    "calories": c.calories,
                    "protein": c.protein,
                    "carbs": c.carbs,
                    "fat": c.fat
                }
                for c in meal.components
            ]
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error retrieving meal: {str(e)}"}
        )

@app.put("/api/meals/{meal_id}")
@login_required
async def update_meal(request: Request, meal_id: int, db: Session = Depends(get_db)):
    """Update an existing meal log."""
    user = request.state.user
    if not user:
        return JSONResponse(
            status_code=401, 
            content={"detail": "Not authenticated"}
        )
    
    try:
        # Get JSON data from request body
        meal_data = await request.json()
        
        # Find the existing meal
        existing_meal = (
            db.query(MealLog)
            .filter(MealLog.id == meal_id, MealLog.user_id == user.id)
            .first()
        )
        
        if not existing_meal:
            return JSONResponse(
                status_code=404, 
                content={"detail": "Meal not found"}
            )
        
        # Parse the datetime string
        meal_date = datetime.strptime(meal_data['datetime'], '%Y-%m-%dT%H:%M')
        
        # Update meal log
        existing_meal.date = meal_date
        existing_meal.meal_type = MealType(meal_data['meal_type'])
        
        # Delete existing components
        db.query(MealComponent).filter(MealComponent.meal_log_id == meal_id).delete()
        
        # Add new components
        for comp in meal_data['components']:
            component = MealComponent(
                meal_log_id=existing_meal.id,
                food_item=comp["food_item"],
                category=FoodCategory(comp["category"]),
                quantity=comp["quantity"],
                unit=UnitType(comp["unit"]),
                calories=comp["calories"],
                protein=comp["protein"],
                carbs=comp["carbs"],
                fat=comp["fat"]
            )
            db.add(component)
        
        db.commit()
        return JSONResponse(
            status_code=200,
            content={"message": "Meal updated successfully"}
        )
        
    except ValueError as e:
        db.rollback()
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid data format: {str(e)}"}
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error updating meal: {str(e)}"}
        )

@app.delete("/api/meals/{meal_id}")
@app.post("/api/meals/{meal_id}/delete")
@login_required
async def delete_meal(request: Request, meal_id: int, db: Session = Depends(get_db)):
    """Delete a meal log."""
    user = request.state.user
    if not user:
        return JSONResponse(
            status_code=401, 
            content={"detail": "Not authenticated"}
        )
    
    try:
        meal = (
            db.query(MealLog)
            .filter(MealLog.id == meal_id, MealLog.user_id == user.id)
            .first()
        )
        
        if not meal:
            return JSONResponse(
                status_code=404, 
                content={"detail": "Meal not found"}
            )
        
        # Delete associated meal components first
        db.query(MealComponent).filter(MealComponent.meal_log_id == meal_id).delete()
        
        # Then delete the meal
        db.delete(meal)
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={"message": "Meal deleted successfully"}
        )
    
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error deleting meal: {str(e)}"}
        )

@app.get("/api/favorite-meals/{meal_id}")
@login_required
async def get_favorite_meal(request: Request, meal_id: int):
    """Get a specific favorite meal."""
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = next(get_db())
    try:
        meal = (
            db.query(FavoriteMeal)
            .filter(FavoriteMeal.id == meal_id, FavoriteMeal.user_id == user.id)
            .options(selectinload(FavoriteMeal.components))
            .first()
        )
        
        if not meal:
            raise HTTPException(status_code=404, detail="Favorite meal not found")
        
        return {
            "id": meal.id,
            "name": meal.name,
            "meal_type": meal.meal_type,
            "components": [
                {
                    "food_item": c.food_item,
                    "category": c.category,
                    "quantity": c.quantity,
                    "unit": c.unit,
                    "calories": c.calories,
                    "protein": c.protein,
                    "carbs": c.carbs,
                    "fat": c.fat
                }
                for c in meal.components
            ]
        }
    
    finally:
        db.close()

@app.post("/api/favorite-meals")
@login_required
async def add_favorite_meal(
    request: Request,
    name: str = Form(...),
    meal_type: str = Form(...),
    components: List[Dict] = Form(...)
):
    """Add a new favorite meal."""
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = next(get_db())
    try:
        # Create favorite meal
        meal = FavoriteMeal(
            user_id=user.id,
            name=name,
            meal_type=meal_type
        )
        db.add(meal)
        db.flush()  # Get meal.id
        
        # Add components
        for comp in components:
            component = FavoriteMealComponent(
                meal_id=meal.id,
                food_item=comp["food_item"],
                category=comp["category"],
                quantity=float(comp["quantity"]),
                unit=comp["unit"],
                calories=int(comp["calories"]),
                protein=float(comp["protein"]) if comp.get("protein") else None,
                carbs=float(comp["carbs"]) if comp.get("carbs") else None,
                fat=float(comp["fat"]) if comp.get("fat") else None
            )
            db.add(component)
        
        db.commit()
        return {"message": "Favorite meal added successfully", "id": meal.id}
    
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
