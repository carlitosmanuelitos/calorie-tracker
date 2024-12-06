# Calorie Tracker Web Application

A web-based calorie tracking application built with FastAPI, SQLAlchemy, and Jinja2 templates.

## Features

- User Authentication
  - Email and password-based login
  - Secure session management using HTTP-only cookies
  - Password validation with strong security requirements
  - Protected routes using `@login_required` decorator

- User Profile Management
  - Basic user information
  - Health and fitness preferences
  - Activity level tracking
  - Personal goals setting

## Project Structure

```
calorie_tracker/
├── app/
│   ├── core/              # Core functionality
│   │   ├── config.py      # Application settings
│   │   ├── security.py    # Authentication & security
│   │   └── enums.py       # Shared enumerations
│   ├── db/                # Database
│   │   ├── base.py        # Base model imports
│   │   ├── init_db.py     # Database initialization
│   │   └── session.py     # Database session
│   ├── models/            # SQLAlchemy models
│   │   └── user.py        # User and profile models
│   └── main.py            # FastAPI application and routes
├── alembic/               # Database migrations
├── static/                # Static files (CSS, JS)
├── templates/             # Jinja2 templates
├── alembic.ini           # Alembic configuration
├── init_database.py      # Database initialization script
└── requirements.txt      # Project dependencies
```

## Prerequisites

- Python 3.8 or higher
- SQLite (included in Python)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd calorie_tracker
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python init_database.py
   ```

## Running the Application

Start the application with:
```bash
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

## Configuration

Create a `.env` file in the root directory with the following variables:
```env
PROJECT_NAME=Calorie Tracker
SECRET_KEY=your-secret-key
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=your-secure-password
```

## Security Features

- Secure password hashing using bcrypt
- HTTP-only session cookies
- Protected routes with authentication required
- Strong password requirements
- CSRF protection
- Input validation

## Database Management

- SQLAlchemy ORM for database operations
- Alembic for database migrations
- Automatic database initialization
- User and profile data models

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license here]


## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Jinja2](https://jinja.palletsprojects.com/)

