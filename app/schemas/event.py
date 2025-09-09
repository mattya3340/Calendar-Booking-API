from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class EventBase(BaseModel):
    event_date: date
    start_time: time
    end_time: time
    representative_name: str
    phone_number: str
    num_adults: int = Field(ge=0, default=1)
    num_children: int = Field(ge=0, default=0)
    notes: Optional[str] = None
    plan: Optional[str] = None
    is_holiday: bool = False
    holiday_name: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    event_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    representative_name: Optional[str] = None
    phone_number: Optional[str] = None
    num_adults: Optional[int] = Field(None, ge=0)
    num_children: Optional[int] = Field(None, ge=0)

class EventInDBBase(EventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

class Event(EventInDBBase):
    pass

class EventInDB(EventInDBBase):
    pass