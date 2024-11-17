from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.session import engine

def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

def drop_tables() -> None:
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)

def init_superuser(db: Session) -> None:
    """Create first superuser if it doesn't exist."""
    user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
    if not user:
        user = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username="admin",
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

def init_db(db: Session) -> None:
    """Initialize database with required initial data."""
    create_tables()
    init_superuser(db)
