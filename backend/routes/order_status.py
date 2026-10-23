from fastapi import APIRouter, HTTPException
from ..services.database import get_db
from ..models.orders import Order
from ..models.cart_class import Cart
from ..models.products import Products
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from ..auth.jwt import get_current_user

router = APIRouter()

@router.get("/order/{order_id}")
async def get_order_status(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Check the status of an order and get all items in it.
    This allows users to verify if their purchase succeeded even if they didn't get a response.
    """
    user_id = current_user["id"]
    
    # Get order
    result = await db.execute(
        select(Order).filter(
            Order.order_id == order_id,
            Order.user_id == user_id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get all cart items for this order
    cart_result = await db.execute(
        select(Cart, Products)
        .join(Products, Cart.product_id == Products.product_id)
        .filter(Cart.order_id == order_id)
    )
    cart_items = cart_result.all()
    
    items = []
    for cart, product in cart_items:
        items.append({
            "product_id": product.product_id,
            "product_name": product.product_name,
            "quantity": cart.quantity,
            "price": cart.product_price_snapshot,  # Use snapshot price
            "total": cart.total_price
        })

    return {
        "order_id": order.order_id,
        "shop_id": order.shop_id,
        "status": order.status,
        "total_cost": order.total_cost,
        "created_at": order.created_at,
        "status_updated_at": order.status_updated_at,
        "items": items,
        "item_count": len(items)
    }
