from fastapi import APIRouter, HTTPException
from ..services.database import get_db
from ..models.shop_data import Shop
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from ..auth.jwt import get_current_user

router = APIRouter()

@router.get("/my_shops")
async def get_user_shops(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get all shops owned by the current user.
    """
    user_id = current_user["id"]
    
    result = await db.execute(
        select(Shop).filter(Shop.user_id == user_id)
    )
    shops = result.scalars().all()
    
    return {
        "shops": [
            {
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "shop_description": shop.shop_description,
                "shop_address": shop.shop_address,
                "shop_phone": shop.shop_phone,
                "shop_email": shop.shop_email
            }
            for shop in shops
        ],
        "count": len(shops)
    }
