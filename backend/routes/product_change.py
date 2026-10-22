from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.services.database import get_db
from backend.auth.jwt import get_current_user
from backend.schemas.product_change_input import ProductChangeInput
from backend.models.products import Products
from backend.models.shop_data import Shop

router = APIRouter()

@router.put("/product_change")
async def product_change(new: ProductChangeInput, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):

    user_id = user["id"]

    try:
        # Step 1: Check if product exists
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

        # Step 3: Check if any fields were provided
        update_data = {}
        if new.product_name is not None:
            update_data["product_name"] = new.product_name
        if new.product_price is not None:
            update_data["product_price"] = new.product_price
        if new.product_description is not None:
            update_data["product_description"] = new.product_description
        if new.amount is not None:
            update_data["amount"] = new.amount

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided to update")

        # Step 4: Update only the provided fields
        for field, value in update_data.items():
            setattr(product, field, value)    

        await db.commit()
        await db.refresh(product)

        return {
            "message": "Product updated successfully",
            "product_id": product.product_id,
            "updated_fields": list(update_data.keys())
        }

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403, 400)
        await db.rollback()
        raise
    except Exception as e:
        # Rollback on any other error
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")