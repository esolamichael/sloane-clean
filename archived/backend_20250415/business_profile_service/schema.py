# backend/business_profile_service/schema.py

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AddressSchema(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    class Config:
        orm_mode = True


class ContactInfoSchema(BaseModel):
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        orm_mode = True


class BusinessHoursSchema(BaseModel):
    is_open: bool = True
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    
    class Config:
        orm_mode = True


class DailyHoursSchema(BaseModel):
    monday: Optional[BusinessHoursSchema] = None
    tuesday: Optional[BusinessHoursSchema] = None
    wednesday: Optional[BusinessHoursSchema] = None
    thursday: Optional[BusinessHoursSchema] = None
    friday: Optional[BusinessHoursSchema] = None
    saturday: Optional[BusinessHoursSchema] = None
    sunday: Optional[BusinessHoursSchema] = None
    
    class Config:
        orm_mode = True


class BusinessServiceSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    
    class Config:
        orm_mode = True


class BusinessProfileSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    google_business_id: Optional[str] = None
    business_name: str
    address: Optional[AddressSchema] = None
    contact_info: Optional[ContactInfoSchema] = None
    business_hours: Optional[Dict[str, BusinessHoursSchema]] = None
    services: Optional[List[BusinessServiceSchema]] = None
    description: Optional[str] = None
    attributes: Optional[Dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class BusinessProfileCreateSchema(BaseModel):
    google_business_id: Optional[str] = None
    business_name: str
    address: Optional[AddressSchema] = None
    contact_info: Optional[ContactInfoSchema] = None
    business_hours: Optional[Dict[str, BusinessHoursSchema]] = None
    services: Optional[List[BusinessServiceSchema]] = None
    description: Optional[str] = None
    attributes: Optional[Dict] = None


class OAuthTokenSchema(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expiry_date: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class GoogleAuthResponseSchema(BaseModel):
    success: bool
    redirect_url: Optional[str] = None
    error: Optional[str] = None


class GoogleBusinessAccountSchema(BaseModel):
    name: str
    display_name: str
    account_type: Optional[str] = None


class GoogleBusinessLocationSchema(BaseModel):
    name: str
    display_name: str
    address: Optional[AddressSchema] = None
    primary_phone: Optional[str] = None


class GoogleBusinessImportSchema(BaseModel):
    location_id: str


class ImportResponseSchema(BaseModel):
    success: bool
    profile_id: Optional[int] = None
    error: Optional[str] = None
