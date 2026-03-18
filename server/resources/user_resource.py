from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from server.core.database import get_db
from server.services import user_service
from server.schemas.user_schema import UserCreate, UserResponse, UserLogin
from server.core.security import create_access_token  # add this

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = user_service.create_user(db, user_data)
    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
        }
    }

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
        }
    }