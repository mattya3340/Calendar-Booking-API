from sqlalchemy import Column, Integer, String, Boolean, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class WeeklyHolidayRule(Base):
    __tablename__ = "weekly_holiday_rules"

    id = Column(Integer, primary_key=True, index=True)
    # 0=Monday ... 6=Sunday
    weekday = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

class BusinessHours(Base):
    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True, index=True)
    # 0=Monday ... 6=Sunday
    weekday = Column(Integer, nullable=False, unique=True, index=True)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)
