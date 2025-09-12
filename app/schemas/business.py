from datetime import time, date as Date
from typing import Optional, List
from pydantic import BaseModel, Field

# ---------- 定休日ルール関連のスキーマ ----------
class WeeklyHolidayRuleBase(BaseModel):
    weekday: int = Field(..., ge=0, le=6, description="曜日（0=月曜, 1=火曜, ..., 6=日曜）")
    name: Optional[str] = Field(None, description="ルールの名称（例: '毎週火曜定休'）")

class WeeklyHolidayRuleCreate(WeeklyHolidayRuleBase):
    pass

class WeeklyHolidayRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, description="新しいルールの名称")

class WeeklyHolidayRuleInDBBase(WeeklyHolidayRuleBase):
    id: int = Field(..., description="ルールID")
    active: bool = Field(True, description="ルールが有効かどうか")
    class Config:
        from_attributes = True

class WeeklyHolidayRule(WeeklyHolidayRuleInDBBase):
    pass

class WeeklyHolidayOccurrence(BaseModel):
    date: Date = Field(..., description="定休日となる日付")
    weekday: int = Field(..., description="曜日（0-6）")
    name: Optional[str] = Field(None, description="ルールの名称")
    open_time: Optional[time] = Field(None, description="その曜日の開店時間（参考情報）")
    close_time: Optional[time] = Field(None, description="その曜日の閉店時間（参考情報）")


# ---------- 営業時間関連のスキーマ ----------
class BusinessHoursBase(BaseModel):
    weekday: int = Field(..., ge=0, le=6, description="曜日（0=月曜, ..., 6=日曜）")
    open_time: time = Field(..., description="開店時間")
    close_time: time = Field(..., description="閉店時間")

class BusinessHoursCreate(BusinessHoursBase):
    pass

class BusinessHoursUpdate(BaseModel):
    open_time: Optional[time] = Field(None, description="新しい開店時間")
    close_time: Optional[time] = Field(None, description="新しい閉店時間")

class BusinessHoursBatchUpdate(BaseModel):
    items: List[BusinessHoursCreate] = Field(..., description="営業時間のリスト")

class BusinessHoursInDBBase(BusinessHoursBase):
    id: int = Field(..., description="営業時間設定ID")
    class Config:
        from_attributes = True

class BusinessHours(BusinessHoursInDBBase):
    pass

# 全曜日統一設定用の新しいスキーマ
class BusinessHoursUnifiedSet(BaseModel):
    open_time: time = Field(..., description="開店時間")
    close_time: time = Field(..., description="閉店時間")
