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

@router.get("/my_orders")
async def get_order_history(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get complete order history for the current user.
    Returns all orders with their items, dates, and status.
    """
    user_id = current_user["id"]
    
    # Get all orders for this user
    orders_result = await db.execute(
        select(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    orders = orders_result.scalars().all()
    
    if not orders:
        return {
            "orders": [],
            "total_orders": 0,
            "message": "No orders found"
        }
    
    orders_with_items = []
    
    # For each order, get its items
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
                "price": product.product_price,
                "total": cart.total_price
            })
        
        orders_with_items.append({
            "order_id": order.order_id,
            "status": order.status,
            "total_cost": order.total_cost,
            "created_at": order.created_at,
            "items": items,
            "item_count": len(items)
        })
    
    return {
        "orders": orders_with_items,
        "total_orders": len(orders_with_items)
    }
