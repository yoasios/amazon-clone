from fastapi import APIRouter, HTTPException
from ..schemas.shop_input import ShopInput
from ..services.database import get_db
from ..models.shop_data import Shop
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import Depends, Response
from ..auth.jwt import get_current_user
from ..auth.shop_cookies import create_shop_token, shop_access_token_cookie

router = APIRouter()

@router.post("/shop_login")
async def shop_login(response: Response, new_shop: ShopInput, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # Check if this user already has a shop with the same name, email, or phone
    result = await db.execute(
        select(Shop).filter(
            Shop.user_id == user_id,
            or_(
                Shop.shop_name == new_shop.shop_name,
                Shop.shop_email == new_shop.shop_email,
                Shop.shop_phone == new_shop.shop_phone
            )
        )
    )
    shop = result.scalar_one_or_none()
    if shop:
        raise HTTPException(status_code=400, detail="You already have a shop with this name, email, or phone number")

    new_shop_obj = Shop(
        shop_name=new_shop.shop_name,
        shop_description=new_shop.shop_description,
        shop_address=new_shop.shop_address,
        shop_email=new_shop.shop_email,
        shop_phone=new_shop.shop_phone,
        user_id=user_id
    )
    try:
        db.add(new_shop_obj)
        await db.commit()
        await db.refresh(new_shop_obj)
        token = create_shop_token(new_shop_obj.shop_id, user_id)
        shop_access_token_cookie(response, token)
        return {"message": "Shop created successfully", "shop_id": new_shop_obj.shop_id}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create shop")
