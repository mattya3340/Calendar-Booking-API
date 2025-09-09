from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.business import WeeklyHolidayRule, BusinessHours
from app.schemas.business import (
    WeeklyHolidayRuleCreate,
    WeeklyHolidayRuleUpdate,
    BusinessHoursCreate,
    BusinessHoursUpdate,
)

# ---------- WeeklyHolidayRule CRUD ----------
class CRUDWeeklyHolidayRule(CRUDBase[WeeklyHolidayRule, WeeklyHolidayRuleCreate, WeeklyHolidayRuleUpdate]):
    def get_active(self, db: Session) -> List[WeeklyHolidayRule]:
        return db.query(WeeklyHolidayRule).filter(WeeklyHolidayRule.active == True).all()

    def deactivate(self, db: Session, *, id: int) -> Optional[WeeklyHolidayRule]:
        rule = db.query(WeeklyHolidayRule).get(id)
        if not rule:
            return None
        rule.active = False
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

weekly_holiday_rule = CRUDWeeklyHolidayRule(WeeklyHolidayRule)

# ---------- BusinessHours CRUD ----------
class CRUDBusinessHours(CRUDBase[BusinessHours, BusinessHoursCreate, BusinessHoursUpdate]):
    def get_by_weekday(self, db: Session, *, weekday: int) -> Optional[BusinessHours]:
        return db.query(BusinessHours).filter(BusinessHours.weekday == weekday).first()

    def upsert_by_weekday(self, db: Session, *, weekday: int, open_time, close_time) -> BusinessHours:
        bh = self.get_by_weekday(db, weekday=weekday)
        if bh:
            bh.open_time = open_time
            bh.close_time = close_time
        else:
            bh = BusinessHours(weekday=weekday, open_time=open_time, close_time=close_time)
            db.add(bh)
        db.commit()
        db.refresh(bh)
        return bh

business_hours = CRUDBusinessHours(BusinessHours)
