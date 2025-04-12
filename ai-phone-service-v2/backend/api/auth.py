# backend/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import uuid
import os
from dotenv import load_dotenv

from ..database.postgres_connection import get_postgres_db
from ..database.mongodb_connection import mongodb
from ..models.postgres_models import User, Token

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-placeholder")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Setup router
router = APIRouter()

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# MongoDB collection for session data
SESSION_COLLECTION = "user_sessions"

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int  # seconds

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Helper functions
def verify_password(plain_password, hashed_password):
    """Verify password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password."""
    return pwd_context.hash(password)

async def authenticate_user(email: str, password: str, db: AsyncSession):
    """Authenticate a user by email and password."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT refresh token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_postgres_db)):
    """Get the current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    # Store session info in MongoDB
    session_data = {
        "user_id": str(user.id),
        "last_activity": datetime.utcnow(),
        "ip_address": None,  # Would capture from request in production
        "user_agent": None,  # Would capture from request in production
    }
    
    # Update or insert session data
    await mongodb.db[SESSION_COLLECTION].update_one(
        {"user_id": str(user.id)},
        {"$set": session_data},
        upsert=True
    )
    
    return user

# Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_postgres_db)):
    """Register a new user."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Get access and refresh tokens."""
    user = await authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login timestamp
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires
    )
    
    # Store refresh token in database
    token_expires = datetime.utcnow() + refresh_token_expires
    db_token = Token(
        user_id=user.id,
        token=refresh_token,
        token_type="refresh",
        expires_at=token_expires
    )
    db.add(db_token)
    await db.commit()
    
    # Store session data in MongoDB
    session_id = str(uuid.uuid4())
    session_data = {
        "user_id": str(user.id),
        "session_id": session_id,
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "ip_address": None,  # Would capture from request in production
        "user_agent": None,  # Would capture from request in production
        "is_active": True
    }
    
    await mongodb.db[SESSION_COLLECTION].insert_one(session_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_postgres_db)
):
    """Refresh access token using refresh token."""
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token exists in database and is not revoked
        result = await db.execute(
            select(Token).where(
                Token.user_id == user_id,
                Token.token == refresh_request.refresh_token,
                Token.is_revoked == False
            )
        )
        token = result.scalar_one_or_none()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token is expired
        if token.expires_at < datetime.utcnow():
            # Revoke expired token
            token.is_revoked = True
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=access_token_expires
        )
        
        # Create new refresh token
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = create_refresh_token(
            data={"sub": user_id},
            expires_delta=refresh_token_expires
        )
        
        # Revoke old refresh token
        token.is_revoked = True
        
        # Store new refresh token
        token_expires = datetime.utcnow() + refresh_token_expires
        new_db_token = Token(
            user_id=uuid.UUID(user_id),
            token=new_refresh_token,
            token_type="refresh",
            expires_at=token_expires
        )
        db.add(new_db_token)
        await db.commit()
        
        # Update session data in MongoDB
        await mongodb.db[SESSION_COLLECTION].update_one(
            {"user_id": user_id},
            {"$set": {"last_activity": datetime.utcnow()}}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Logout and invalidate tokens."""
    # Revoke all refresh tokens for the user
    await db.execute(
        select(Token).where(
            Token.user_id == current_user.id,
            Token.is_revoked == False
        ).update({"is_revoked": True})
    )
    await db.commit()
    
    # Deactivate user sessions in MongoDB
    await mongodb.db[SESSION_COLLECTION].update_many(
        {"user_id": str(current_user.id)},
        {"$set": {"is_active": False}}
    )
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the current user profile."""
    return current_user
