from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from ..services.settings import settings
from datetime import datetime, timedelta
from fastapi import Response, Cookie, HTTPException
import json

def create_shop_token(shop_id: int, user_id: int):
    expire = datetime.now() + timedelta(minutes=60)
    token = encode({"sub": json.dumps({"shop_id": shop_id, "user_id": user_id}), "exp": expire}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def shop_access_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="shop_access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/"
    )

def get_current_shop(shop_access_token: str = Cookie(None)):
    if not shop_access_token:
        raise HTTPException(status_code=401, detail="No shop cookie found")
    try:
        token_data = decode(shop_access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = token_data.get("sub")
        if sub:
            return json.loads(sub)
        return None
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Shop token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid shop token")