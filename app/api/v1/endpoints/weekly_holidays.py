from datetime import date, timedelta, time as Time
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.crud.crud_business import weekly_holiday_rule, business_hours
from app.schemas.business import (
    WeeklyHolidayRule as WeeklyHolidayRuleSchema,
    WeeklyHolidayRuleCreate,
    WeeklyHolidayRuleUpdate,
    WeeklyHolidayOccurrence,
)

router = APIRouter()

@router.get("/", response_model=List[WeeklyHolidayRuleSchema])
def list_rules(
    db: Session = Depends(get_db),
):
    """List active weekly holiday rules (public)."""
    return weekly_holiday_rule.get_active(db)

@router.post("/", response_model=WeeklyHolidayRuleSchema)
def create_rule(
    *,
    db: Session = Depends(get_db),
    rule_in: WeeklyHolidayRuleCreate,
):
    """Create a weekly holiday rule (public)."""
    return weekly_holiday_rule.create(db, obj_in=rule_in)

@router.delete("/{rule_id}", response_model=WeeklyHolidayRuleSchema)
def deactivate_rule(
    *,
    db: Session = Depends(get_db),
    rule_id: int,
):
    """Deactivate a weekly holiday rule (public)."""
    rule = weekly_holiday_rule.deactivate(db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.get("/occurrences", response_model=List[WeeklyHolidayOccurrence])
def list_occurrences(
    *,
    db: Session = Depends(get_db),
    start_date: date,
    end_date: date,
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

    rules = weekly_holiday_rule.get_active(db)
    results: List[WeeklyHolidayOccurrence] = []

    delta = timedelta(days=1)
    day = start_date
    while day <= end_date:
        weekday = day.weekday()  # 0=Mon ... 6=Sun
        for r in rules:
            if r.weekday == weekday:
                bh = business_hours.get_by_weekday(db, weekday=weekday)
                results.append(
                    WeeklyHolidayOccurrence(
                        date=day,
                        weekday=weekday,
                        name=r.name,
                        open_time=bh.open_time if bh else None,
                        close_time=bh.close_time if bh else None,
                    )
                )
        day += delta

    return results
