from datetime import date, datetime, time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.event import Event, EventCreate, EventUpdate
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[Event])
def read_events(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """
    予約・予定（イベント）の一覧を取得します（公開）。
    日付範囲を指定してフィルタリングすることも可能です。
    """
    if start_date and end_date:
        events = crud.event.get_events_in_date_range(
            db, start_date=start_date, end_date=end_date, skip=skip, limit=limit
        )
    else:
        events = crud.event.get_multi(db, skip=skip, limit=limit)
    return events

@router.post("/", response_model=Event)
def create_event(
    *,
    db: Session = Depends(get_db),
    event_in: EventCreate,
):
    """
    新しい予約・予定（イベント）を作成します（公開）。
    作成されたイベントは特定のユーザーには紐付きません。
    """
    try:
        event = crud.event.create_with_overlap_check(db=db, obj_in=event_in)
        return event
    except ValueError as e:
        # 時間の重複、または不正な時間範囲が指定された場合
        raise HTTPException(status_code=409, detail=str(e))

@router.put("/{event_id}", response_model=Event)
def update_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    event_in: EventUpdate,
):
    """
    既存の予約・予定を更新します（公開）。
    更新時にも重複チェックや営業時間チェックが行われます。
    """
    try:
        event = crud.event.update_with_overlap_check(db=db, event_id=event_id, obj_in=event_in)
        return event
    except ValueError as e:
        detail = str(e)
        if detail == "Event not found":
            raise HTTPException(status_code=404, detail="イベントが見つかりません。")
        raise HTTPException(status_code=409, detail=detail)

@router.get("/{event_id}", response_model=Event)
def read_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
):
    """IDを指定して特定の予約・予定を取得します（公開）。"""
    event = crud.event.get(db=db, id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません。")
    return event

@router.delete("/{event_id}", response_model=Event)
def delete_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
):
    """予約・予定を削除します（公開）。"""
    event = crud.event.get(db=db, id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません。")
    event = crud.event.remove(db=db, id=event_id)
    return event