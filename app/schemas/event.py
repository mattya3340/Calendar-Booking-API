from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class EventBase(BaseModel):
    event_date: date = Field(..., description="イベントの日付", examples=["2025-12-25"])
    start_time: time = Field(..., description="開始時刻", examples=["13:00:00"])
    end_time: time = Field(..., description="終了時刻", examples=["14:00:00"])
    representative_name: str = Field(..., description="代表者名")
    phone_number: str = Field(..., description="電話番号")
    num_adults: int = Field(1, ge=0, description="大人の人数")
    num_children: int = Field(0, ge=0, description="子供の人数")
    notes: Optional[str] = Field(None, description="備考欄")
    plan: Optional[str] = Field(None, description="利用プランなど")
    is_holiday: bool = Field(False, description="休日として設定するかどうか")
    holiday_name: Optional[str] = Field(None, description="休日の名称（is_holidayがtrueの場合）")

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
    id: int = Field(..., description="イベントID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: Optional[datetime] = Field(None, description="更新日時")
    user_id: Optional[int] = Field(None, description="関連付けられたユーザーID")

    class Config:
        from_attributes = True

    # データベースから来た値（v）を検証・変換するバリデータを定義します。
    # mode='before' にすることで、FastAPIがレスポンスを作成する前の段階で型変換が実行されます。
    @field_validator('event_date', 'start_time', 'end_time', mode='before')
    @classmethod
    def coerce_datetime_to_specific_type(cls, v, info):
        # 値がdatetimeオブジェクトの場合のみ処理
        if isinstance(v, datetime):
            # フィールド名に応じて、date型またはtime型に変換して返す
            if info.field_name == 'event_date':
                return v.date()
            return v.time()
        # datetimeでなければ元の値をそのまま返す
        return v

class Event(EventInDBBase):
    pass

class EventInDB(EventInDBBase):
    pass