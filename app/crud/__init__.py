# app/crud/__init__.py
# Expose CRUD singletons for convenient imports like: from app import crud; crud.user...
from .crud_user import user
from .crud_event import event
from .crud_business import weekly_holiday_rule, business_hours

__all__ = [
    "user",
    "event",
    "weekly_holiday_rule",
    "business_hours",
]
