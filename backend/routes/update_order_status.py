from fastapi import APIRouter, HTTPException
from ..services.database import get_db
from ..models.orders import Order
from ..models.cart_class import Cart
from ..models.products import Products
from ..models.shop_data import Shop
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from ..auth.jwt import get_current_user
from ..auth.shop_cookies import get_current_shop
from ..schemas.order_status_update import OrderStatusUpdate
from datetime import datetime

router = APIRouter()

@router.put("/update_order_status")
async def update_order_status(
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    current_shop = Depends(get_current_shop)
):
    """
    Update order status.
    - Shopkeeper can change: pending -> working, working -> pending
    - User can change: working -> completed (only when shop sets to working)
    - Only user can set status to "completed"
    """
    shop_id = current_shop["shop_id"]
    user_id = current_user["id"]

    # Get the order
    order_result = await db.execute(
        select(Order).filter(Order.order_id == status_update.order_id)
    )
    order = order_result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify this order belongs to the current shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="This order does not belong to your shop")

    # Validate status transitions for shopkeepers (this route is for shopkeepers only)
    # Shopkeepers can ONLY change: pending <-> working
    # Shopkeepers CANNOT mark as completed (user-only operation)
    allowed_transitions = {
        "pending": ["working"],
        "working": ["pending"],
        "completed": [],  # Cannot change from completed
        "cancelled": []  # Cannot change from cancelled
    }

    if status_update.status not in allowed_transitions.get(order.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from '{order.status}' to '{status_update.status}'. "
                   f"Shopkeepers can only toggle between pending and working. "
                   f"Allowed transitions: {allowed_transitions.get(order.status, [])}"
        )

    # Shopkeepers can NEVER mark orders as completed (use user_order_status endpoint for that)
    if status_update.status == "completed":
        raise HTTPException(
            status_code=403,
            detail="Shopkeepers cannot mark orders as completed. Only customers can confirm completion."
        )

    # Update the order status
    order.status = status_update.status
    order.status_updated_at = datetime.now()

    await db.commit()

    return {
        "success": True,
        "message": f"Order status updated to {status_update.status}",
        "order_id": order.order_id,
        "status": order.status,
        "status_updated_at": order.status_updated_at
    }
