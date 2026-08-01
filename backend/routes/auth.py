"""
Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

from models.database import get_db
from models.user import User
from models.role import Role
from utils.config import settings
from utils.audit import log_audit

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Pydantic schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name_ar: Optional[str] = None
    first_name_en: Optional[str] = None
    last_name_ar: Optional[str] = None
    last_name_en: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    first_name_ar: Optional[str]
    first_name_en: Optional[str]
    last_name_ar: Optional[str]
    last_name_en: Optional[str]
    is_active: bool
    is_super_admin: bool

class LoginResponse(BaseModel):
    user: UserResponse
    token: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="غير مصرح - Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

@router.post("/register", response_model=LoginResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if email exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="البريد الإلكتروني مسجل مسبقاً"
        )
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name_ar=user_data.first_name_ar,
        first_name_en=user_data.first_name_en,
        last_name_ar=user_data.last_name_ar,
        last_name_en=user_data.last_name_en,
        phone=user_data.phone,
        is_active=True
    )
    
    # Assign default role
    default_role = db.query(Role).filter(Role.name == "viewer").first()
    if default_role:
        user.roles.append(default_role)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log audit
    log_audit(db, user.id, "create", "user", user.id, None, user_data.model_dump())
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return LoginResponse(
        user=UserResponse.model_validate(user),
        token=access_token
    )

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user"""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بيانات الدخول غير صحيحة"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="الحساب غير نشط"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Log audit
    log_audit(db, user.id, "login", "user", user.id)
    
    access_token = create_access_token(data={"sub": user.id})
    
    return LoginResponse(
        user=UserResponse.model_validate(user),
        token=access_token
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse.model_validate(current_user)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user"""
    log_audit(db, current_user.id, "logout", "user", current_user.id)
    return {"message": "تم تسجيل الخروج"}
