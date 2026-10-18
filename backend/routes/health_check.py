from fastapi import APIRouter, Cookie
from ..auth.jwt import read_access_token

router = APIRouter()

@router.get("/health")
async def health_check(access_token: str = Cookie(None)):
    if not access_token:
        return {"status": "unauthorized", "message": "No cookie found"}
    user = read_access_token(access_token)
    if not user:
        return {"status": "unauthorized", "message": "Invalid token"}
    return {"status": user}
