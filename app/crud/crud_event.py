from datetime import datetime, date, time
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text, and_, not_, or_

from app.crud.base import CRUDBase
from app.models.event import CalendarEvent
from app.schemas.event import EventCreate, EventUpdate
from app.models.business import WeeklyHolidayRule, BusinessHours

class CRUDEvent(CRUDBase[CalendarEvent, EventCreate, EventUpdate]):
    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[CalendarEvent]:
        return (
            db.query(self.model)
            .filter(CalendarEvent.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_events_in_date_range(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100
    ) -> List[CalendarEvent]:
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        return (
            db.query(self.model)
            .filter(CalendarEvent.event_date.between(start_dt, end_dt))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_holidays_in_date_range(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date
    ) -> List[CalendarEvent]:
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        return (
            db.query(self.model)
            .filter(CalendarEvent.is_holiday == True)
            .filter(CalendarEvent.event_date.between(start_dt, end_dt))
            .all()
        )

    def _combine_dt(self, d: date, t: time) -> datetime:
        return datetime.combine(d, t)

    def create_with_overlap_check(
        self,
        db: Session,
        *,
        obj_in: EventCreate,
        lock_timeout_sec: int = 5,
        skip_business_rules: bool | None = None,
    ) -> CalendarEvent:
        
        # 予約日が過去の日付でないかチェック
        if obj_in.event_date < date.today():
            raise ValueError("過去の日付には予約できません。")

        lock_key = f"event:{obj_in.event_date.isoformat()}"
        db.execute(text("SELECT GET_LOCK(:k, :t)"), {"k": lock_key, "t": lock_timeout_sec})
        try:
            start_dt = self._combine_dt(obj_in.event_date, obj_in.start_time)
            end_dt = self._combine_dt(obj_in.event_date, obj_in.end_time)

            if end_dt <= start_dt:
                raise ValueError("終了時刻は開始時刻より後に設定してください。")

            if skip_business_rules is None:
                skip_business_rules = bool(getattr(obj_in, "is_holiday", False))

            if not skip_business_rules:
                weekday = start_dt.weekday()
                rule = (
                    db.query(WeeklyHolidayRule)
                    .filter(WeeklyHolidayRule.active == True, WeeklyHolidayRule.weekday == weekday)
                ).first()
                if rule:
                    raise ValueError("選択された日付は定休日です。")

                bh = db.query(BusinessHours).filter(BusinessHours.weekday == weekday).first()
                if bh:
                    if not (bh.open_time <= start_dt.time() and end_dt.time() <= bh.close_time):
                        raise ValueError("時間は営業時間外です。")
            
            day_start = datetime.combine(start_dt.date(), time.min)
            day_end = datetime.combine(start_dt.date(), time.max)

            conflict = (
                db.query(self.model)
                .filter(self.model.event_date.between(day_start, day_end))
                .filter(
                    not_(
                        or_(
                            self.model.end_time <= start_dt,
                            self.model.start_time >= end_dt,
                        )
                    )
                )
                .with_for_update()
                .first()
            )

            if conflict:
                if getattr(obj_in, "is_holiday", False) and getattr(conflict, "is_holiday", False):
                    conflict.holiday_name = obj_in.holiday_name or conflict.holiday_name
                    conflict.event_date = start_dt
                    conflict.start_time = start_dt
                    conflict.end_time = end_dt
                    db.add(conflict)
                    db.commit()
                    db.refresh(conflict)
                    return conflict
                raise ValueError("その時間枠はすでに予約されています。")

            db_obj = self.model(
                event_date=start_dt,
                start_time=start_dt,
                end_time=end_dt,
                representative_name=obj_in.representative_name,
                phone_number=obj_in.phone_number,
                num_adults=obj_in.num_adults,
                num_children=obj_in.num_children,
                notes=obj_in.notes,
                plan=obj_in.plan,
                is_holiday=obj_in.is_holiday,
                holiday_name=obj_in.holiday_name,
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        finally:
            db.execute(text("SELECT RELEASE_LOCK(:k)"), {"k": lock_key})

    def update_with_overlap_check(self, db: Session, *, event_id: int, obj_in: EventUpdate, lock_timeout_sec: int = 5) -> CalendarEvent:
        db_obj = db.query(self.model).get(event_id)
        if not db_obj:
            raise ValueError("Event not found")

        cur_date = db_obj.event_date.date()
        cur_start_dt = db_obj.start_time
        cur_end_dt = db_obj.end_time

        new_date = obj_in.event_date if obj_in.event_date is not None else cur_date
        
        # 更新後の日付が過去でないかチェック
        if new_date < date.today():
            raise ValueError("過去の日付には変更できません。")
        
        new_start_t = obj_in.start_time if obj_in.start_time is not None else cur_start_dt.time()
        new_end_t = obj_in.end_time if obj_in.end_time is not None else cur_end_dt.time()

        lock_key = f"event:{new_date.isoformat()}"
        db.execute(text("SELECT GET_LOCK(:k, :t)"), {"k": lock_key, "t": lock_timeout_sec})
        try:
            start_dt = datetime.combine(new_date, new_start_t)
            end_dt = datetime.combine(new_date, new_end_t)
            if end_dt <= start_dt:
                raise ValueError("終了時刻は開始時刻より後に設定してください。")

            weekday = start_dt.weekday()
            rule = (
                db.query(WeeklyHolidayRule)
                .filter(WeeklyHolidayRule.active == True, WeeklyHolidayRule.weekday == weekday)
            ).first()
            if rule:
                raise ValueError("選択された日付は定休日です。")

            bh = db.query(BusinessHours).filter(BusinessHours.weekday == weekday).first()
            if bh:
                if not (bh.open_time <= start_dt.time() and end_dt.time() <= bh.close_time):
                    raise ValueError("時間は営業時間外です。")

            day_start = datetime.combine(start_dt.date(), time.min)
            day_end = datetime.combine(start_dt.date(), time.max)
            conflict = (
                db.query(self.model)
                .filter(self.model.event_date.between(day_start, day_end))
                .filter(self.model.id != event_id)
                .filter(
                    not_(
                        or_(
                            self.model.end_time <= start_dt,
                            self.model.start_time >= end_dt,
                        )
                    )
                )
                .with_for_update()
                .first()
            )
            if conflict:
                raise ValueError("その時間枠はすでに予約されています。")

            db_obj.event_date = start_dt
            db_obj.start_time = start_dt
            db_obj.end_time = end_dt

            for field in [
                "representative_name", "phone_number", "num_adults", "num_children",
                "notes", "plan", "is_holiday", "holiday_name",
            ]:
                val = getattr(obj_in, field, None)
                if val is not None:
                    setattr(db_obj, field, val)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        finally:
            db.execute(text("SELECT RELEASE_LOCK(:k)"), {"k": lock_key})

event = CRUDEvent(CalendarEvent)