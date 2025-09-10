from datetime import time as Time
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.crud_business import business_hours
from app.schemas.business import BusinessHours as BusinessHoursSchema, BusinessHoursCreate, BusinessHoursUpdate

router = APIRouter()

@router.get("/", response_model=List[BusinessHoursSchema])
def list_business_hours(
    db: Session = Depends(get_db),
):
    """List business hours for all weekdays (public)."""
    items = db.query(business_hours.model).order_by(business_hours.model.weekday.asc()).all()
    return items

@router.get("/{weekday}", response_model=BusinessHoursSchema)
def get_business_hours_by_weekday(
    *,
    db: Session = Depends(get_db),
    weekday: int,
):
    if weekday < 0 or weekday > 6:
        raise HTTPException(status_code=400, detail="weekday must be between 0 and 6")
    item = business_hours.get_by_weekday(db, weekday=weekday)
    if not item:
        raise HTTPException(status_code=404, detail="Business hours for this weekday not found")
    return item

@router.put("/{weekday}", response_model=BusinessHoursSchema)
def upsert_business_hours(
    *,
    db: Session = Depends(get_db),
    weekday: int,
    payload: BusinessHoursCreate,
):
    if weekday != payload.weekday:
        raise HTTPException(status_code=400, detail="Path weekday and body weekday must match")
    if payload.open_time >= payload.close_time:
        raise HTTPException(status_code=400, detail="open_time must be earlier than close_time")
    item = business_hours.upsert_by_weekday(
        db,
        weekday=payload.weekday,
        open_time=payload.open_time,
        close_time=payload.close_time,
    )
    return item
