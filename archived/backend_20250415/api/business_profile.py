# backend/api/business_profile.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sql_update
from typing import Dict, List, Optional, Any
import uuid

from ..database.postgres_connection import get_postgres_db
from ..database.mongodb_connection import mongodb
from ..models.postgres_models import Business, User
from ..repositories.business_data_repository import BusinessDataRepository
from ..schemas.mongodb_schemas import ScrapedWebsiteData, GoogleBusinessProfileData

# Pydantic schemas for request/response
from pydantic import BaseModel, HttpUrl, Field

router = APIRouter()

# Pydantic models for API requests/responses
class BusinessCreate(BaseModel):
    name: str
    description: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = "United States"
    timezone: Optional[str] = "America/New_York"
    business_hours: Optional[Dict[str, List[str]]] = None
    google_business_id: Optional[str] = None
    google_place_id: Optional[str] = None

class BusinessResponse(BusinessCreate):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: str
    updated_at: str
    subscription_active: bool
    
    class Config:
        orm_mode = True

class WebsiteDataResponse(BaseModel):
    id: str
    url: str
    last_scraped: str
    sections: List[Dict[str, Any]]
    
    class Config:
        orm_mode = True

class GoogleBusinessResponse(BaseModel):
    id: str
    business_name: str
    description: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    phone_number: Optional[str] = None
    categories: Optional[List[str]] = None
    services: Optional[List[Dict[str, Any]]] = None
    hours: Optional[Dict[str, List[str]]] = None
    
    class Config:
        orm_mode = True

class ScrapedDataCreate(BaseModel):
    url: str
    content: Dict[str, Any]
    sections: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

class GoogleBusinessDataCreate(BaseModel):
    google_place_id: Optional[str] = None
    business_name: str
    description: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    phone_number: Optional[str] = None
    categories: Optional[List[str]] = None
    services: Optional[List[Dict[str, Any]]] = None
    hours: Optional[Dict[str, List[str]]] = None
    photos_urls: Optional[List[str]] = None
    reviews: Optional[List[Dict[str, Any]]] = None
    attributes: Optional[Dict[str, Any]] = None

# Dependency to get the current user (implement your auth logic)
async def get_current_user(db: AsyncSession = Depends(get_postgres_db)) -> User:
    # This is a placeholder - implement your actual auth logic
    # For example, get user from JWT token
    user_id = "11111111-1111-1111-1111-111111111111"  # Example UUID
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return user

# Routes
@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    business_data: BusinessCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Create a new business profile."""
    # Create a new Business object
    new_business = Business(
        owner_id=current_user.id,
        **business_data.dict()
    )
    
    # Add to PostgreSQL
    db.add(new_business)
    await db.commit()
    await db.refresh(new_business)
    
    return new_business

@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Get a business profile by ID."""
    # Query from PostgreSQL
    business = await db.execute(
        select(Business).where(
            Business.id == business_id,
            Business.owner_id == current_user.id
        )
    )
    business = business.scalar_one_or_none()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    return business

@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: uuid.UUID,
    business_data: BusinessCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Update a business profile."""
    # Verify business exists and belongs to user
    business = await db.execute(
        select(Business).where(
            Business.id == business_id,
            Business.owner_id == current_user.id
        )
    )
    business = business.scalar_one_or_none()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Update the business
    await db.execute(
        sql_update(Business)
        .where(Business.id == business_id)
        .values(**business_data.dict(exclude_unset=True))
    )
    await db.commit()
    
    # Get the updated business
    updated_business = await db.execute(select(Business).where(Business.id == business_id))
    updated_business = updated_business.scalar_one()
    
    return updated_business

@router.post("/{business_id}/website-data", status_code=status.HTTP_201_CREATED)
async def store_website_data(
    business_id: uuid.UUID,
    website_data: ScrapedDataCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Store scraped website data for a business."""
    # Verify business exists and belongs to user
    business = await db.execute(
        select(Business).where(
            Business.id == business_id,
            Business.owner_id == current_user.id
        )
    )
    business = business.scalar_one_or_none()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Prepare data for MongoDB
    mongo_data = website_data.dict()
    mongo_data["business_id"] = str(business_id)
    
    # Store in MongoDB
    doc_id = await BusinessDataRepository.store_website_data(mongo_data)
    
    # Update PostgreSQL with a reference to MongoDB document
    await db.execute(
        sql_update(Business)
        .where(Business.id == business_id)
        .values(website_data_id=doc_id)
    )
    await db.commit()
    
    return {"message": "Website data stored successfully", "document_id": doc_id}

@router.post("/{business_id}/google-business-data", status_code=status.HTTP_201_CREATED)
async def store_google_business_data(
    business_id: uuid.UUID,
    gbp_data: GoogleBusinessDataCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Store Google Business Profile data for a business."""
    # Verify business exists and belongs to user
    business = await db.execute(
        select(Business).where(
            Business.id == business_id,
            Business.owner_id == current_user.id
        )
    )
    business = business.scalar_one_or_none()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Prepare data for MongoDB
    mongo_data = gbp_data.dict()
    mongo_data["business_id"] = str(business_id)
    
    # Store in MongoDB
    doc_id = await BusinessDataRepository.store_gbp_data(mongo_data)
    
    # Update PostgreSQL with a reference to MongoDB document
    await db.execute(
        sql_update(Business)
        .where(Business.id == business_id)
        .values(gbp_data_id=doc_id)
    )
    await db.commit()
    
    return {"message": "Google Business Profile data stored successfully", "document_id": doc_id}

@router.get("/{business_id}/website-data", response_model=WebsiteDataResponse)
async def get_website_data(
    business_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Get the latest scraped website data for a business."""
    # Verify business exists and belongs to user
    business = await db.execute(
        select(Business).where(
            Business.id == business_id,
            Business.owner_id == current_user.id
        )
    )
    business = business.scalar_one_or_none()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Get data from MongoDB
    website_data = await BusinessDataRepository.get_latest_website_data(str(business_id))
    
    if not website_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website data not found for this business"
        )
    
    # Convert MongoDB _id to string
    website_data["id"] = str(website_data.pop("_id"))
    
    return website_data

@router.get("/{business_id}/google-business-data", response_model=GoogleBusinessResponse)
async def get_google_business_data(
    business_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Get Google Business Profile data for a business."""
    # Verify business exists and belongs to user
    business = await db.execute(
        select(Business).where(
            Business.id == business_id,
            Business.owner_id == current_user.id
        )
    )
    business = business.scalar_one_or_none()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Get data from MongoDB
    gbp_data = await BusinessDataRepository.get_gbp_data(str(business_id))
    
    if not gbp_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google Business Profile data not found for this business"
        )
    
    # Convert MongoDB _id to string
    gbp_data["id"] = str(gbp_data.pop("_id"))
    
    return gbp_data

@router.get("/{business_id}/services")
async def get_business_services(
    business_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_db)
):
    """Extract services from both website and Google Business Profile data."""
    # Verify business exists and belongs to user
    business = await db.execute(
        select(Business).where(
            Business.id == business_id,
            Business.owner_id == current_user.id
        )
    )
    business = business.scalar_one_or_none()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Extract services using the repository
    services = await BusinessDataRepository.extract_business_services(str(business_id))
    
    return {"services": services}
