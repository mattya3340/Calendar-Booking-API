from fastapi import APIRouter

from app.api.v1.endpoints import auth, events, holidays, users
from app.api.v1.endpoints import weekly_holidays, business_hours

api_router = APIRouter()

# tagsをmain.pyで定義した日本語のnameと一致させます
api_router.include_router(auth.router, prefix="/auth", tags=["認証 (利用不可)"])
api_router.include_router(users.router, prefix="/users", tags=["ユーザー"])
api_router.include_router(events.router, prefix="/events", tags=["予約・イベント"])
api_router.include_router(holidays.router, prefix="/holidays", tags=["休日設定"])
api_router.include_router(weekly_holidays.router, prefix="/weekly-holidays", tags=["定休日ルール"])
api_router.include_router(business_hours.router, prefix="/business-hours", tags=["営業時間"])