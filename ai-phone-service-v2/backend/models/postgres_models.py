# backend/models/postgres_models.py
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, 
    DateTime, ForeignKey, Text, JSON, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database.postgres_connection import Base

# Association tables for many-to-many relationships
user_role_association = Table(
    'user_role_association', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

# User authentication and management models
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))
    
    users = relationship("User", secondary=user_role_association, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    roles = relationship("Role", secondary=user_role_association, back_populates="users")
    businesses = relationship("Business", back_populates="owner")
    
    def __repr__(self):
        return f"<User {self.email}>"

class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    phone_number = Column(String(20))
    email = Column(String(255))
    website_url = Column(String(255))
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(50), default="United States")
    timezone = Column(String(50), default="America/New_York")
    business_hours = Column(JSON)  # Store business hours as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # External services integration
    google_business_id = Column(String(255))  # Google Business Profile ID
    google_place_id = Column(String(255))     # Google Place ID
    calendar_integration_id = Column(String(255))  # ID for calendar integration
    crm_integration_id = Column(String(255))  # ID for CRM integration
    
    # Mongo relationship fields
    website_data_id = Column(String(255))  # Link to MongoDB document ID
    gbp_data_id = Column(String(255))      # Link to MongoDB document ID
    
    # Subscription and plan details
    subscription_active = Column(Boolean, default=False)
    plan_id = Column(Integer, ForeignKey("plans.id"))
    subscription_start_date = Column(DateTime)
    subscription_end_date = Column(DateTime)
    
    # AI configuration
    ai_voice_id = Column(String(50), default="default")  # Voice ID for the AI
    custom_greeting = Column(Text)
    custom_closing = Column(Text)
    ai_personality = Column(String(50), default="professional")
    
    # Relationships
    owner = relationship("User", back_populates="businesses")
    phone_numbers = relationship("PhoneNumber", back_populates="business")
    calls = relationship("Call", back_populates="business")
    plan = relationship("Plan")
    
    def __repr__(self):
        return f"<Business {self.name}>"

class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    is_primary = Column(Boolean, default=False)
    provider = Column(String(50), default="twilio")  # Phone service provider
    provider_id = Column(String(255))  # ID in the provider's system
    capabilities = Column(JSON)  # JSON object with capabilities (SMS, voice, etc.)
    monthly_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="phone_numbers")
    
    def __repr__(self):
        return f"<PhoneNumber {self.phone_number}>"

class Call(Base):
    __tablename__ = "calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    caller_number = Column(String(20))
    caller_name = Column(String(255))
    call_sid = Column(String(255), unique=True)  # Call ID from telephony provider
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    status = Column(String(50))  # "in-progress", "completed", "failed", etc.
    direction = Column(String(20), default="inbound")  # "inbound" or "outbound"
    recording_url = Column(String(255))
    
    # Link to MongoDB transcript
    transcript_id = Column(String(255))
    
    # Call metadata
    call_purpose = Column(String(100))  # Determined by AI
    action_taken = Column(String(100))  # "message_taken", "appointment_scheduled", etc.
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text)
    
    # Relationships
    business = relationship("Business", back_populates="calls")
    appointment = relationship("Appointment", uselist=False, back_populates="call")
    
    def __repr__(self):
        return f"<Call {self.id} from {self.caller_number}>"

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"))
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    client_name = Column(String(255))
    client_phone = Column(String(20))
    client_email = Column(String(255))
    appointment_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    service_type = Column(String(255))
    notes = Column(Text)
    status = Column(String(50), default="scheduled")  # "scheduled", "completed", "cancelled", "no-show"
    created_at = Column(DateTime, default=datetime.utcnow)
    calendar_event_id = Column(String(255))  # ID in the calendar service
    
    # Relationships
    call = relationship("Call", back_populates="appointment")
    
    def __repr__(self):
        return f"<Appointment {self.id} at {self.appointment_time}>"

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price_monthly = Column(Float, nullable=False)
    price_yearly = Column(Float)
    minutes_included = Column(Integer, default=0)
    additional_minute_cost = Column(Float, default=0.05)
    max_businesses = Column(Integer, default=1)
    features = Column(JSON)  # JSON array of feature strings
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Plan {self.name}>"

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), default="stripe")  # Payment processor
    provider_id = Column(String(255))  # ID in the provider's system
    card_last4 = Column(String(4))
    card_brand = Column(String(50))
    card_exp_month = Column(Integer)
    card_exp_year = Column(Integer)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PaymentMethod {self.card_brand} *{self.card_last4}>"

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"))
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")  # "pending", "paid", "failed", "refunded"
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    payment_date = Column(DateTime)
    description = Column(Text)
    line_items = Column(JSON)  # JSON array of line items
    provider_invoice_id = Column(String(255))  # ID in the payment provider's system
    
    def __repr__(self):
        return f"<Invoice {self.id} for ${self.amount}>"

# Token table for secure authentication tokens
class Token(Base):
    __tablename__ = "tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    token_type = Column(String(50), default="access")  # "access", "refresh", "reset_password", etc.
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Token {self.token_type} for user {self.user_id}>"
