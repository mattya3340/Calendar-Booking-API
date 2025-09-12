from datetime import time as Time
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.crud_business import business_hours
from app.schemas.business import (
    BusinessHours as BusinessHoursSchema,
    BusinessHoursCreate,
    BusinessHoursUpdate,
    BusinessHoursBatchUpdate,
    BusinessHoursUnifiedSet,
)

router = APIRouter()

@router.post("/set-unified", response_model=List[BusinessHoursSchema], tags=["営業時間"])
def set_unified_business_hours(
    *,
    db: Session = Depends(get_db),
    payload: BusinessHoursUnifiedSet,
):
    """
    全曜日の営業時間を単一の時間設定で統一します。
    このAPIを呼び出すと、既存のすべての営業時間設定は削除され、
    月曜から日曜までが全て同じ時間で新しく保存されます。
    """
    if payload.open_time >= payload.close_time:
        raise HTTPException(status_code=400, detail="開店時間は閉店時間より前に設定してください。")
        
    items = business_hours.set_unified_hours(
        db, open_time=payload.open_time, close_time=payload.close_time
    )
    return items


@router.put("/", response_model=List[BusinessHoursSchema], tags=["営業時間"])
def upsert_all_business_hours(
    *,
    db: Session = Depends(get_db),
    payload: BusinessHoursBatchUpdate,
):
    """
    【リスト指定用】全曜日の営業時間設定を一括で更新（全件入れ替え）します。
    """
    weekdays = set()
    for item in payload.items:
        if item.weekday in weekdays:
            raise HTTPException(status_code=400, detail=f"曜日 '{item.weekday}' が重複しています。")
        if item.open_time >= item.close_time:
            raise HTTPException(status_code=400, detail=f"曜日 '{item.weekday}' の開店時間は閉店時間より前に設定してください。")
        weekdays.add(item.weekday)
        
    items = business_hours.batch_upsert(db, items=payload.items)
    return items


@router.get("/", response_model=List[BusinessHoursSchema], tags=["営業時間"])
def list_business_hours(
    db: Session = Depends(get_db),
):
    """全曜日の営業時間の一覧を取得します（公開）。"""
    items = db.query(business_hours.model).order_by(business_hours.model.weekday.asc()).all()
    return items

@router.get("/{weekday}", response_model=BusinessHoursSchema, tags=["営業時間"])
def get_business_hours_by_weekday(
    *,
    db: Session = Depends(get_db),
    weekday: int,
):
    """【個別取得用】曜日を指定して営業時間を取得します（公開）。"""
    if weekday < 0 or weekday > 6:
        raise HTTPException(status_code=400, detail="曜日は0（月曜）から6（日曜）の間で指定してください。")
    item = business_hours.get_by_weekday(db, weekday=weekday)
    if not item:
        raise HTTPException(status_code=404, detail="この曜日の営業時間設定は見つかりません。")
    return item

@router.put("/{weekday}", response_model=BusinessHoursSchema, tags=["営業時間"])
def upsert_business_hours(
    *,
    db: Session = Depends(get_db),
    weekday: int,
    payload: BusinessHoursCreate,
):
    """
    【個別設定用】曜日ごとの営業時間を作成または更新します（公開）。
    """
    if weekday != payload.weekday:
        raise HTTPException(status_code=400, detail="URLの曜日とリクエストボディの曜日が一致しません。")
    if payload.open_time >= payload.close_time:
        raise HTTPException(status_code=400, detail="開店時間は閉店時間より前に設定してください。")
    item = business_hours.upsert_by_weekday(
        db,
        weekday=payload.weekday,
        open_time=payload.open_time,
        close_time=payload.close_time,
    )
    return item