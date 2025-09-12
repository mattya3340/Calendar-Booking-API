from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base_class import Base
from app.db.session import engine

# APIドキュメントの各セクション（タグ）の定義
# nameを日本語にすることで、ドキュメントのセクションタイトル自体が日本語になります。
tags_metadata = [
    {
        "name": "認証 (利用不可)",
        "description": "認証関連API。現在、認証機能は無効化されています。",
    },
    {
        "name": "ユーザー",
        "description": "ユーザー情報の参照・作成を行うAPI。現在は認証不要で利用できます。",
    },
    {
        "name": "予約・イベント",
        "description": "予約・予定（イベント）関連API。参照・作成・更新・削除が可能です。",
    },
    {
        "name": "休日設定",
        "description": "単発の休日（祝日など）を管理するAPI。",
    },
    {
        "name": "定休日ルール",
        "description": "毎週の定休日ルールを管理するAPI。",
    },
    {
        "name": "営業時間",
        "description": "曜日ごとの営業時間を管理するAPI。",
    },
]

app = FastAPI(
    title=f"{settings.PROJECT_NAME} (認証無効版)",
    description=(
        "カレンダー予約APIのデモバージョンです。\n\n"
        "**注意:** 本APIはデモ構成として認証機能が無効化されています。\n"
        "そのため、書き込みが可能なエンドポイントも全て公開状態です。\n"
        "本番環境で利用する場合は、APIキーやIP制限などで適切に保護してください。"
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS (Cross-Origin Resource Sharing) の設定
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.BACKEND_CORS_ORIGINS, # config.pyのリストを許可
    allow_origin_regex=r"http://localhost(:\d+)?",  # localhostの動的ポートを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの読み込み
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def _create_tables() -> None:
    """起動時にデータベースのテーブルを全て作成します。"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[startup] テーブル作成に失敗しました: {e}")

@app.get("/")
def root():
    return {"message": "カレンダー予約APIへようこそ (認証無効版)"}