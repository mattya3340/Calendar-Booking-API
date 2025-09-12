from datetime import date, timedelta, time
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

def batch_upsert(self, db: Session, *, items: List[BusinessHoursCreate]) -> List[BusinessHours]:
        """
        営業時間設定を一括で入れ替えます。
        既存の全設定を削除し、新しい設定を挿入します。
        """
        try:
            # 既存のデータをすべて削除
            db.query(BusinessHours).delete()
            
            # 新しいデータをリストから作成
            new_hours_list = [
                BusinessHours(
                    weekday=item.weekday, 
                    open_time=item.open_time, 
                    close_time=item.close_time
                ) 
                for item in items
            ]
            
            db.add_all(new_hours_list)
            db.commit()

            # 挿入したデータを返却
            return new_hours_list
        except Exception as e:
            db.rollback() # エラーが発生した場合は処理を元に戻す
            raise e

def set_unified_hours(self, db: Session, *, open_time: time, close_time: time) -> List[BusinessHours]:
        """
        全曜日の営業時間設定を、指定された単一の時間で統一します。
        既存の全設定を削除し、月曜から日曜までの新しい設定を挿入します。
        """
        try:
            # 既存のデータをすべて削除
            db.query(BusinessHours).delete()

            # 月曜(0)から日曜(6)までの7日分のデータを作成
            unified_hours_list = [
                BusinessHours(weekday=i, open_time=open_time, close_time=close_time)
                for i in range(7)
            ]
            
            db.add_all(unified_hours_list)
            db.commit()

            return unified_hours_list
        except Exception as e:
            db.rollback()
            raise e

business_hours = CRUDBusinessHours(BusinessHours)
