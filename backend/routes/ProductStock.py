from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.services.database import get_db
from backend.schemas.stock_update_input import ProductStockInput
from backend.auth.jwt import get_current_user
from backend.models.products import Products
from backend.models.shop_data import Shop

router = APIRouter()

@router.put("/product_stock")
async def product_stock(new: ProductStockInput, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    """
    Update product stock amount.
    Verifies that the product belongs to the current user's shop.
    Uses atomic update to prevent race conditions with purchases.
    Uses transaction rollback on errors to prevent partial updates.
    """
    user_id = user["id"]

    try:
        # Step 1: Check if product exists and get its shop_id
        product_result = await db.execute(
            select(Products).filter(Products.product_id == new.product_id)
        )
        product = product_result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Step 2: Verify ownership (check if the shop belongs to the user)
        shop_result = await db.execute(
            select(Shop).filter(Shop.shop_id == product.shop_id)
        )
        shop = shop_result.scalar_one_or_none()

        if not shop or shop.user_id != user_id:
            raise HTTPException(status_code=403, detail="You do not own this product")

        # Step 3: Atomic update of product amount (prevents race conditions)
        # This ensures that if a purchase happens at the same time,
        # the database will handle the concurrency correctly
        await db.execute(
            update(Products)
            .where(Products.product_id == new.product_id)
            .values(amount=new.amount)
        )

        await db.commit()

        # Refresh to get the updated value
        await db.refresh(product)

        return {
            "message": "Product stock updated successfully",
            "product_id": product.product_id,
            "new_amount": product.amount
        }

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403)
        await db.rollback()
        raise
    except Exception as e:
        # Rollback on any other error
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
