from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.event import Event, EventCreate
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[Event])
def read_holidays(
    *,
    db: Session = Depends(get_db),
    start_date: date,
    end_date: date,
):
    """
    指定した期間内の休日設定を取得します（公開）。
    """
    holidays = crud.event.get_holidays_in_date_range(
        db, start_date=start_date, end_date=end_date
    )
    return holidays

@router.post("/", response_model=Event)
def create_holiday(
    *,
    db: Session = Depends(get_db),
    holiday_in: EventCreate,
):
    """
    新しい休日を設定します（公開）。
    """
    holiday_in.is_holiday = True
    # Use overlap-safe creation but skip business rules for holidays
    try:
        holiday = crud.event.create_with_overlap_check(
            db=db,
            obj_in=holiday_in,
            skip_business_rules=True,
        )
        return holiday
    except ValueError as e:
        # Conflict (e.g., overlapping holiday) or invalid time range
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{holiday_id}", response_model=Event)
def delete_holiday(
    *,
    db: Session = Depends(get_db),
    holiday_id: int,
):
    """
    休日設定を削除します（公開）。
    """
    holiday = crud.event.get(db=db, id=holiday_id)
    if not holiday or not holiday.is_holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    holiday = crud.event.remove(db=db, id=holiday_id)
    return holiday
