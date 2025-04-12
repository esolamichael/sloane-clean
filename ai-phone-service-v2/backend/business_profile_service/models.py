from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class BusinessProfile(Base):
    __tablename__ = 'business_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    google_business_id = Column(String(255), unique=True)
    business_name = Column(String(255), nullable=False)
    street_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    phone = Column(String(50))
    website = Column(String(255))
    email = Column(String(255))
    description = Column(Text)
    attributes = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_hours = relationship("BusinessHours", back_populates="business_profile", cascade="all, delete-orphan")
    services = relationship("BusinessService", back_populates="business_profile", cascade="all, delete-orphan")

class BusinessHours(Base):
    __tablename__ = 'business_hours'
    
    id = Column(Integer, primary_key=True)
    business_profile_id = Column(Integer, ForeignKey('business_profiles.id'), nullable=False)
    day_of_week = Column(String(10), nullable=False)
    is_open = Column(Boolean, default=True)
    open_time = Column(String(10))
    close_time = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    business_profile = relationship("BusinessProfile", back_populates="business_hours")
    
    # Unique constraint
    __table_args__ = (
        # Ensure each business profile has only one entry per day of week
        sqlalchemy.UniqueConstraint('business_profile_id', 'day_of_week', name='unique_business_day'),
    )

class BusinessService(Base):
    __tablename__ = 'business_services'
    
    id = Column(Integer, primary_key=True)
    business_profile_id = Column(Integer, ForeignKey('business_profiles.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    business_profile = relationship("BusinessProfile", back_populates="services")

class OAuthToken(Base):
    __tablename__ = 'oauth_tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    provider = Column(String(50), nullable=False)
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text)
    iv = Column(String(32))
    access_token_auth_tag = Column(String(32))
    refresh_token_auth_tag = Column(String(32))
    expiry_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Unique constraint
    __table_args__ = (
        # Ensure each user has only one entry per provider
        sqlalchemy.UniqueConstraint('user_id', 'provider', name='unique_user_provider'),
    )
