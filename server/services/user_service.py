from sqlalchemy.orm import Session
from server.models.user import User
from server.core.security import get_password_hash, verify_password
from server.schemas.user_schema import UserCreate  # We'll create this next

def create_user(db: Session, user_data: UserCreate):
    """Create a new user with hashed password"""

    hashed_password = get_password_hash(user_data.password)

    db_user = User(
        email=user_data.email,
        password=hashed_password,  # Store the hash
        full_name=user_data.full_name,
        role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    # Verify password here!
    if not verify_password(password, user.password):
        return None
    return user

def get_user_by_email(db: Session, email: str):
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()