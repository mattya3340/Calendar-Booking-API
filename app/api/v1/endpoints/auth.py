from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.post("/login/access-token")
async def login_access_token():
    """（利用不可）アクセストークンを取得します。認証が無効化されているため使用できません。"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")

@router.post("/login/test-token")
async def test_token():
    """（利用不可）テストトークンを検証します。認証が無効化されているため使用できません。"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")

@router.post("/refresh-token")
async def refresh_token():
    """（利用不可）アクセストークンを更新します。認証が無効化されているため使用できません。"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")