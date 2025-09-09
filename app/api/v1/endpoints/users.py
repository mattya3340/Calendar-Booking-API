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
    """Retrieve users (no authentication required)."""
    return crud.user.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
):
    """Create new user (no authentication required)."""
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    return crud.user.create(db, obj_in=user_in)

@router.get("/me")
def read_user_me():
    """Disabled because authentication is turned off."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")

@router.put("/me")
def update_user_me():
    """Disabled because authentication is turned off."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")

@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
):
    """Get a specific user by id (no authentication required)."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
