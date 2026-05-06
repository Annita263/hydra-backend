from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models.models import User
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True

@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    user = User(name=payload.name, email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    token = create_access_token(user.id, user.email)
    return AuthResponse(access_token=token, user_id=user.id, name=user.name, email=user.email)

@router.post("/login", response_model=AuthResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = create_access_token(user.id, user.email)
    return AuthResponse(access_token=token, user_id=user.id, name=user.name, email=user.email)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user