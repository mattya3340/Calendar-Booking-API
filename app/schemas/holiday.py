from datetime import date as Date
from typing import Optional
from pydantic import BaseModel, Field

class HolidayBase(BaseModel):
    name: str = Field(..., description="祝日・休日の名称")
    date: Date = Field(..., description="休日の日付")
    description: Optional[str] = Field(None, description="休日に関する説明（任意）")

class HolidayCreate(HolidayBase):
    pass

class HolidayUpdate(HolidayBase):
    name: Optional[str] = Field(None, description="新しい祝日・休日の名称")
    date: Optional[Date] = Field(None, description="新しい休日の日付")

class HolidayInDBBase(HolidayBase):
    id: int = Field(..., description="休日ID")
    class Config:
        from_attributes = True

class Holiday(HolidayInDBBase):
    pass