from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

tags_metadata = [
    {
        "name": "authentication",
        "description": "認証は無効化されています。このタグのエンドポイントは 501 Not Implemented を返します。",
    },
    {
        "name": "users",
        "description": "ユーザーの参照・作成 API。現在は認証不要で利用できます。/me 系は 501 を返します。",
    },
    {
        "name": "events",
        "description": "予約・予定（イベント）API。参照・作成・更新・削除は公開で利用できます。",
    },
    {
        "name": "holidays",
        "description": "祝日（1日フラグ）として扱うイベントの参照・作成・削除。公開で利用できます。",
    },
    {
        "name": "weekly_holidays",
        "description": "毎週の定休日ルールの参照・作成・無効化、および期間内の発生日一覧（occurrences）。公開で利用できます。",
    },
    {
        "name": "business_hours",
        "description": "曜日別の営業時間の参照および設定。現在は公開で利用できます。",
    },
]

app = FastAPI(
    title=f"{settings.PROJECT_NAME} (Auth Disabled)",
    description=(
        "本APIはデモ構成として認証を無効化しています。\n\n"
        "・/api/v1/auth/* は 501 Not Implemented を返します\n"
        "・その他の書き込み系エンドポイントも公開です。必要に応じて API キーや IP 制限などで保護してください\n"
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to the Calendar Booking API (Authentication Disabled)"}
