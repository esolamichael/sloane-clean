# ~/Desktop/clean-code/app/models/call.py

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Call(Base):
    """
    Call model for PostgreSQL database to store call metadata
    """
    __tablename__ = 'calls'
    
    id = Column(String(36), primary_key=True)
    business_id = Column(String(36), ForeignKey('businesses.id'), nullable=False)
    caller_number = Column(String(20), nullable=False)
    caller_name = Column(String(100), nullable=True)
    forwarded_from = Column(String(20), nullable=True)
    twilio_sid = Column(String(50), nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default='in-progress')  # in-progress, completed, failed
    duration = Column(Integer, default=0)  # in seconds
    recording_url = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    action_required = Column(Boolean, default=False)
    action_items = Column(Text, nullable=True)  # JSON string of action items
    
    def __repr__(self):
        return f"<Call(id='{self.id}', business_id='{self.business_id}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert object to dictionary"""
        return {
            "id": self.id,
            "business_id": self.business_id,
            "caller_number": self.caller_number,
            "caller_name": self.caller_name,
            "forwarded_from": self.forwarded_from,
            "twilio_sid": self.twilio_sid,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "duration": self.duration,
            "recording_url": self.recording_url,
            "summary": self.summary,
            "action_required": self.action_required,
            "action_items": json.loads(self.action_items) if self.action_items else None
        }
