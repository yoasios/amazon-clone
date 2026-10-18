from fastapi import APIRouter
from ..schemas.signin_input import signin_input
from ..schemas.login_input import login_input
from ..services.database import get_db
from ..models.users_class import User
from ..models.shop_data import Shop
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException
from ..auth.passlib_setup import pwd_context
from ..auth.jwt import create_access_token, access_token_cookie
from fastapi import Response

router = APIRouter()

@router.post("/login")
async def login(response: Response, new: login_input, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == new.email))
    same_user = result.scalar_one_or_none()
    if not same_user:
        raise HTTPException(status_code=400, detail="User not found")
    if not pwd_context.verify(new.password[:72], same_user.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    token = create_access_token(data={"id": same_user.id, "email": same_user.email})
    access_token_cookie(response, token)
    
    shop_result = await db.execute(select(Shop).filter(Shop.user_id == same_user.id))
    user_shop = shop_result.scalar_one_or_none()
    
    if user_shop:
        return {
            "message": "Logged in successfully",
            "token": token,
            "shop": {
                "shop_id": user_shop.shop_id,
                "shop_name": user_shop.shop_name,
                "shop_description": user_shop.shop_description,
                "shop_address": user_shop.shop_address,
                "shop_phone": user_shop.shop_phone,
                "shop_email": user_shop.shop_email
            }
        }
    else:
        return {"message": "Logged in successfully", "token": token}

   