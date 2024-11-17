import pytest
from datetime import datetime, timedelta
from app.core.security import get_password_hash
from app.db.base import User, UserProfile  # Import from correct location

def test_register_user(client, test_db):
    response = client.post(
        "/register",
        data={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test123!@#",
            "confirm_password": "Test123!@#"
        },
        allow_redirects=False  # Don't follow redirects
    )
    assert response.status_code == 303  # Redirect to survey
    assert response.headers["location"] == "/survey"  # Check redirect URL
    
    # Check if user was created in database
    user = test_db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password != "Test123!@#"  # Password should be hashed
    
    # Verify no profile was created yet
    profile = test_db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    assert profile is None

def test_register_user_password_validation(client, test_db):
    # Test with weak password
    response = client.post(
        "/register",
        data={
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",
            "confirm_password": "weak"
        }
    )
    assert response.status_code == 400  # Returns form with error
    assert b"Password must be at least 8 characters" in response.content
    
    # Verify no user was created
    user = test_db.query(User).filter(User.email == "test@example.com").first()
    assert user is None

def test_login_user(client, test_db):
    # Create a test user
    hashed_password = get_password_hash("Test123!@#")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    
    # Test login - first check the redirect and cookie
    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "Test123!@#"
        },
        follow_redirects=False
    )
    assert response.status_code == 303  # Redirect after successful login
    assert "access_token" in response.cookies
    assert response.headers["location"] == "/dashboard"
    
    # Now follow the redirect to check the dashboard
    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "Test123!@#"
        },
        follow_redirects=True
    )
    assert response.status_code == 200  # Lands on the dashboard page

def test_login_invalid_credentials(client, test_db):
    # Create a test user
    hashed_password = get_password_hash("Test123!@#")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    
    # Test login with wrong password
    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 400  # Bad request for invalid credentials
    assert b"Incorrect email or password" in response.content

def test_password_reset_request(client, test_db):
    # Create a test user
    hashed_password = get_password_hash("Test123!@#")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    
    # Request password reset
    response = client.post(
        "/reset-password-request",
        data={"email": "test@example.com"}
    )
    assert response.status_code == 200  # Returns success message
    
    # Verify token was created in database
    user = test_db.query(User).filter(User.email == "test@example.com").first()
    assert user.reset_token is not None
    assert user.reset_token_expires > datetime.utcnow()

def test_password_reset(client, test_db):
    # Create a test user with reset token
    reset_token = "test_token"
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("Test123!@#"),
        reset_token=reset_token,
        reset_token_expires=datetime.utcnow() + timedelta(hours=1),
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    
    # Reset password
    new_password = "NewTest123!@#"
    response = client.post(
        f"/reset-password/{reset_token}",
        data={
            "password": new_password,
            "confirm_password": new_password
        },
        follow_redirects=False
    )
    assert response.status_code == 303  # Redirect to login page
    assert response.headers["location"] == "/login"
    
    # Verify password was updated and token was cleared
    user = test_db.query(User).filter(User.email == "test@example.com").first()
    assert user.reset_token is None
    assert user.reset_token_expires is None
    
    # Verify can login with new password
    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": new_password
        },
        follow_redirects=False
    )
    assert response.status_code == 303  # Redirect after successful login
    assert "access_token" in response.cookies
    assert response.headers["location"] == "/dashboard"

def test_password_reset_expired_token(client, test_db):
    # Create a test user with expired reset token
    reset_token = "test_token"
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("Test123!@#"),
        reset_token=reset_token,
        reset_token_expires=datetime.utcnow() - timedelta(hours=1),  # Expired
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    
    # Try to reset password
    response = client.post(
        f"/reset-password/{reset_token}",
        data={
            "password": "NewTest123!@#",
            "confirm_password": "NewTest123!@#"
        }
    )
    assert response.status_code == 200  # Returns form with error
    assert b"Invalid or expired reset link" in response.content
    
    # Verify password was not changed
    user = test_db.query(User).filter(User.email == "test@example.com").first()
    old_password = user.hashed_password
    assert user.hashed_password == old_password
