from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from ..services.settings import settings
from datetime import datetime, timedelta
from fastapi import Response, Cookie, HTTPException
import json

def create_access_token(data: dict):
    expire = datetime.now() + timedelta(minutes=60)
    setco = encode({"sub": json.dumps(data), "exp": expire}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return setco

def read_access_token(token: str):
    try:
        token_data = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = token_data.get("sub")
        if sub:
            return json.loads(sub)
        return None
    except ExpiredSignatureError as e:
        print(f"Token expired: {e}")
        return None
    except InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None
    except Exception as e:
        print(f"Token decode error: {e}")
        return None

def access_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/"
    )

def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        token_data = decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = token_data.get("sub")
        if sub:
            return json.loads(sub)
        raise HTTPException(status_code=401, detail="Invalid token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Token decode error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

def get_current_user_optional(access_token: str = Cookie(None)):
    """Optional authentication - returns None if no valid token"""
    if not access_token:
        return None
    try:
        token_data = decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = token_data.get("sub")
        if sub:
            return json.loads(sub)
        return None
    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
        return None
    except Exception as e:
        print(f"Token decode error: {e}")
        return None
