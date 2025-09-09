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
    Retrieve holidays within a date range (public).
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
    Create new holiday (public).
    """
    holiday_in.is_holiday = True
    holiday = crud.event.create(db=db, obj_in=holiday_in)
    return holiday

@router.delete("/{holiday_id}", response_model=Event)
def delete_holiday(
    *,
    db: Session = Depends(get_db),
    holiday_id: int,
):
    """
    Delete a holiday (public).
    """
    holiday = crud.event.get(db=db, id=holiday_id)
    if not holiday or not holiday.is_holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    holiday = crud.event.remove(db=db, id=holiday_id)
    return holiday
