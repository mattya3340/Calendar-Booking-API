from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(DateTime, nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    representative_name = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=False)
    num_adults = Column(Integer, default=1)
    num_children = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    plan = Column(String(255), nullable=True)
    is_holiday = Column(Boolean, default=False, nullable=False)
    holiday_name = Column(String(255), nullable=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="events")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CalendarEvent {self.representative_name} - {self.event_date}>"
