from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from ..services.database import get_db
from ..models.orders import Order
from ..models.cart_class import Cart
from ..models.products import Products
from ..auth.jwt import get_current_user

router = APIRouter()

@router.post("/cancel_order/{order_id}")
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel an order with refund based on time elapsed since order creation"""
    
    # Get the order
    result = await db.execute(
        select(Order).filter(Order.order_id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify ownership
    if order.user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="You can only cancel your own orders")
    
    # Check if order can be cancelled
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Order is already cancelled")
    
    if order.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed orders")
    
    if order.status == "delivered":
        raise HTTPException(status_code=400, detail="Cannot cancel orders that have been delivered")
    
    # Calculate cancellation fee based on time elapsed
    time_elapsed = datetime.now() - order.created_at
    total_cost = order.total_cost
    cancellation_fee = 0
    
    # Refund policy:
    # Within 5 minutes: ₹0
    # Before seller starts processing (pending): ₹0
    # Processing started (working), but not packed: ₹0–₹20
    # Product packed and ready to dispatch: ₹20–₹50
    # Already handed to courier: Actual, reasonable cancellation-related logistics cost
    
    if time_elapsed <= timedelta(minutes=5):
        cancellation_fee = 0
    elif order.status == "pending":
        cancellation_fee = 0
    elif order.status == "working":
        # Check if more than 1 hour elapsed (packed/ready for dispatch)
        if time_elapsed >= timedelta(hours=1):
            cancellation_fee = int(total_cost * 0.20)  # 20% fee
        else:
            cancellation_fee = int(total_cost * 0.10)  # 10% fee (not packed yet)
    else:
        # If somehow in another state, use maximum fee
        cancellation_fee = int(total_cost * 0.50)  # 50% fee
    
    # Refund amount
    refund_amount = total_cost - cancellation_fee
    
    # Begin transaction
    try:
        # Get all cart items for this order
        cart_result = await db.execute(
            select(Cart).filter(Cart.order_id == order_id)
        )
        cart_items = cart_result.scalars().all()
        
        # Restore stock atomically for each product
        for item in cart_items:
            await db.execute(
                update(Products)
                .where(Products.product_id == item.product_id)
                .values(amount=Products.amount + item.quantity)
            )
        
        # Update order status and cancellation fee
        await db.execute(
            update(Order)
            .where(Order.order_id == order_id)
            .values(
                status="cancelled",
                cancellation_fee=cancellation_fee,
                status_updated_at=datetime.now()
            )
        )
        
        await db.commit()
        
        return {
            "message": "Order cancelled successfully",
            "order_id": order_id,
            "refund_amount": refund_amount,
            "cancellation_fee": cancellation_fee,
            "total_cost": total_cost,
            "time_elapsed_minutes": time_elapsed.total_seconds() / 60,
            "order_status_at_cancellation": order.status
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")
