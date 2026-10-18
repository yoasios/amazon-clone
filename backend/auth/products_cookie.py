from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from ..services.settings import settings
from datetime import datetime, timedelta
from fastapi import Response, Cookie, HTTPException
import json

def get_current_shop(shop_access_token: str = Cookie(None)):
    if not shop_access_token:
        raise HTTPException(status_code=401, detail="No shop cookie found")
    try:
        token_data = decode(shop_access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = token_data.get("sub")
        if sub:
            data = json.loads(sub)
            return data.get("shop_id"), data.get("user_id")
        return None
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Shop token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid shop token")

