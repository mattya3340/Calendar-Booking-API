from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.post("/login/access-token")
async def login_access_token():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")

@router.post("/login/test-token")
async def test_token():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")

@router.post("/refresh-token")
async def refresh_token():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is disabled")
