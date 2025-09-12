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
    """有効な定休日ルールの一覧を取得します（公開）。"""
    return weekly_holiday_rule.get_active(db)

@router.post("/", response_model=WeeklyHolidayRuleSchema)
def create_rule(
    *,
    db: Session = Depends(get_db),
    rule_in: WeeklyHolidayRuleCreate,
):
    """新しい定休日ルールを作成します（公開）。"""
    return weekly_holiday_rule.create(db, obj_in=rule_in)

@router.delete("/{rule_id}", response_model=WeeklyHolidayRuleSchema)
def deactivate_rule(
    *,
    db: Session = Depends(get_db),
    rule_id: int,
):
    """定休日ルールを無効化します（公開）。"""
    rule = weekly_holiday_rule.deactivate(db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="ルールが見つかりません。")
    return rule

@router.get("/occurrences", response_model=List[WeeklyHolidayOccurrence])
def list_occurrences(
    *,
    db: Session = Depends(get_db),
    start_date: date,
    end_date: date,
):
    """指定した期間内に、定休日が実際に発生する日付の一覧を取得します。"""
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="開始日は終了日より前に設定してください。")

    rules = weekly_holiday_rule.get_active(db)
    results: List[WeeklyHolidayOccurrence] = []

    delta = timedelta(days=1)
    day = start_date
    while day <= end_date:
        weekday = day.weekday()  # 0=月 ... 6=日
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