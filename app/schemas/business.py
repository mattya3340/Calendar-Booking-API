# app/schemas/business.py
from __future__ import annotations
from datetime import time, date as Date
from typing import Optional, List
from pydantic import BaseModel, Field

# ---------- Weekly Holiday Rule Schemas ----------
class WeeklyHolidayRuleBase(BaseModel):
    weekday: int = Field(..., ge=0, le=6, description="0=Mon ... 6=Sun")
    name: Optional[str] = Field(None, description="Rule name (e.g., Closed on Tuesday)")

class WeeklyHolidayRuleCreate(WeeklyHolidayRuleBase):
    pass

class WeeklyHolidayRuleUpdate(BaseModel):
    name: Optional[str] = None

class WeeklyHolidayRuleInDBBase(WeeklyHolidayRuleBase):
    id: int
    active: bool = True
    class Config:
        from_attributes = True

class WeeklyHolidayRule(WeeklyHolidayRuleInDBBase):
    pass

# For listing generated dates within a range
class WeeklyHolidayOccurrence(BaseModel):
    date: Date
    weekday: int
    name: Optional[str] = None
    open_time: Optional[time] = None
    close_time: Optional[time] = None

# ---------- Business Hours Schemas ----------
class BusinessHoursBase(BaseModel):
    weekday: int = Field(..., ge=0, le=6, description="0=Mon ... 6=Sun")
    open_time: time = Field(..., description="Opening time")
    close_time: time = Field(..., description="Closing time")

class BusinessHoursCreate(BusinessHoursBase):
    pass

class BusinessHoursUpdate(BaseModel):
    open_time: Optional[time] = None
    close_time: Optional[time] = None

class BusinessHoursInDBBase(BusinessHoursBase):
    id: int
    class Config:
        from_attributes = True

class BusinessHours(BusinessHoursInDBBase):
    pass
