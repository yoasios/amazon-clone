from fastapi import APIRouter, HTTPException
from ..services.database import get_db
from ..models.orders import Order
from ..models.cart_class import Cart
from ..models.products import Products
from ..models.shop_data import Shop
from ..models.users_class import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from ..auth.jwt import get_current_user
from ..auth.shop_cookies import get_current_shop

router = APIRouter()

@router.get("/shop_orders")
async def get_shop_orders(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    current_shop = Depends(get_current_shop)
):
    """
    Get all orders for the current shop (shopkeeper view).
    Returns orders with their items, status, and timestamps.
    """
    shop_id = current_shop["shop_id"]

    # Get all orders for this shop (only orders with valid shop_id)
    orders_result = await db.execute(
        select(Order).filter(
            Order.shop_id == shop_id,
            Order.shop_id.isnot(None)  # Ensure shop_id is not NULL
        ).order_by(Order.created_at.desc())
    )
    orders = orders_result.scalars().all()

    if not orders:
        return {
            "orders": [],
            "total_orders": 0,
            "message": "No orders found for this shop"
        }

    orders_with_items = []

    # For each order, get its items and user info
    for order in orders:
        # Get cart items for this order
        cart_result = await db.execute(
            select(Cart, Products)
            .join(Products, Cart.product_id == Products.product_id)
            .filter(Cart.order_id == order.order_id)
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

        # Get user info
        user_result = await db.execute(
            select(User).filter(User.id == order.user_id)
        )
        user = user_result.scalar_one_or_none()

        orders_with_items.append({
            "order_id": order.order_id,
            "shop_id": order.shop_id,
            "user_id": order.user_id,
            "user_email": user.email if user else "Unknown",
            "status": order.status,
            "total_cost": order.total_cost,
            "created_at": order.created_at,
            "status_updated_at": order.status_updated_at,
            "items": items,
            "item_count": len(items)
        })

    return {
        "orders": orders_with_items,
        "total_orders": len(orders_with_items)
    }
