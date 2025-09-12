from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """ユーザー情報の一覧を取得します（認証不要）。"""
    return crud.user.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
):
    """新しいユーザーを作成します（認証不要）。"""
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に使用されています。")
    return crud.user.create(db, obj_in=user_in)

@router.get("/me")
def read_user_me():
    """（利用不可）認証が無効化されているため、このエンドポイントは使用できません。"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")

@router.put("/me")
def update_user_me():
    """（利用不可）認証が無効化されているため、このエンドポイントは使用できません。"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")

@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
):
    """IDを指定して特定のユーザー情報を取得します（認証不要）。"""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません。")
    return user

@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
):
    """
    IDを指定してユーザーを削除します（公開API）。
    注意：実際のアプリケーションでは管理者権限で保護すべきです。
    """
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません。")
    deleted_user = crud.user.remove(db=db, id=user_id)
    return deleted_user