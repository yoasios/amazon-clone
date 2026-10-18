from fastapi import APIRouter, HTTPException
from ..services.database import get_db
from ..models.shop_data import Shop
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, Response
from ..auth.jwt import get_current_user
from ..auth.shop_cookies import create_shop_token, shop_access_token_cookie

router = APIRouter()

@router.post("/switch_shop/{shop_id}")
async def switch_shop(shop_id: int, response: Response, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """
    """
    user_id = current_user["id"]
    
    # Verify the shop belongs to the user
    result = await db.execute(
        select(Shop).filter(
            Shop.shop_id == shop_id,
            Shop.user_id == user_id
        )
    )
    shop = result.scalar_one_or_none()
    
    if not shop:
        # Generic error message - don't reveal if shop exists or not
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create and set new shop token
    token = create_shop_token(shop.shop_id, user_id)
    shop_access_token_cookie(response, token)
    
    return {
        "message": "Switched to shop successfully",
        "shop_id": shop.shop_id,
        "shop_name": shop.shop_name
    }
