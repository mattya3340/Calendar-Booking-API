# app/schemas/holiday.py
from __future__ import annotations
from datetime import date as Date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class HolidayBase(BaseModel):
    name: str = Field(..., description="祝日名")
    date: Date = Field(..., description="祝日の日付")
    description: Optional[str] = Field(None, description="祝日の説明")


class HolidayCreate(HolidayBase):
    pass


class HolidayUpdate(HolidayBase):
    name: Optional[str] = Field(None, description="祝日名")
    date: Optional[Date] = Field(None, description="祝日の日付")


class HolidayInDBBase(HolidayBase):
    id: int
    class Config:
        from_attributes = True


class Holiday(HolidayInDBBase):
    pass