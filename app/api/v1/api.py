from fastapi import APIRouter

from app.api.v1.endpoints import auth, events, holidays, users
from app.api.v1.endpoints import weekly_holidays, business_hours

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(holidays.router, prefix="/holidays", tags=["holidays"])
api_router.include_router(weekly_holidays.router, prefix="/weekly-holidays", tags=["weekly_holidays"])
api_router.include_router(business_hours.router, prefix="/business-hours", tags=["business_hours"])
