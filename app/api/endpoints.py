from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User
from app.schemas import UserCreate, Token, TokenData
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.database import get_db

router = APIRouter()

@router.post("/v1/api/signup", response_model=Token, tags=["auth"])
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Sign up a new user.
    
    - **email**: user's email address
    - **password**: user's password
    
    Returns an access token upon successful registration.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": db_user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/v1/api/login", response_model=Token, tags=["auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.
    
    - **username**: user's email address
    - **password**: user's password
    
    Returns an access token upon successful authentication.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}