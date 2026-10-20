from fastapi import APIRouter
from ..schemas.signin_input import SigninInput
from ..schemas.login_input import LoginInput
from ..services.database import get_db
from ..models.users_class import User
from ..models.shop_data import Shop
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException
from ..auth.passlib_setup import pwd_context
from ..auth.jwt import create_access_token, access_token_cookie, get_current_user
from fastapi import Response

router = APIRouter()

@router.post("/login")
async def login(
    response: Response,
    new: LoginInput,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # If user is already logged in (has valid cookie), return their data directly
    if current_user:
        # Get all shops for this user
        shop_result = await db.execute(select(Shop).filter(Shop.user_id == current_user["id"]))
        user_shops = shop_result.scalars().all()
        
        shops_data = [
            {
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "shop_description": shop.shop_description,
                "shop_address": shop.shop_address,
                "shop_phone": shop.shop_phone,
                "shop_email": shop.shop_email
            }
            for shop in user_shops
        ]
        
        return {
            "message": "Already logged in",
            "user_id": current_user["id"],
            "email": current_user["email"],
            "shops": shops_data,
            "shop_count": len(shops_data)
        }
    
    # Normal login flow if no valid cookie
    result = await db.execute(select(User).filter(User.email == new.email))
    same_user = result.scalar_one_or_none()
    if not same_user:
        raise HTTPException(status_code=400, detail="User not found")
    if not pwd_context.verify(new.password[:72], same_user.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    token = create_access_token(data={"id": same_user.id, "email": same_user.email})
    access_token_cookie(response, token)
    
    # Get all shops for this user
    shop_result = await db.execute(select(Shop).filter(Shop.user_id == same_user.id))
    user_shops = shop_result.scalars().all()
    
    shops_data = [
        {
            "shop_id": shop.shop_id,
            "shop_name": shop.shop_name,
            "shop_description": shop.shop_description,
            "shop_address": shop.shop_address,
            "shop_phone": shop.shop_phone,
            "shop_email": shop.shop_email
        }
        for shop in user_shops
    ]
    
    return {
        "message": "Logged in successfully",
        "token": token,
        "shops": shops_data,
        "shop_count": len(shops_data)
    }

   