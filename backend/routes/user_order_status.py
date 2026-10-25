from fastapi import APIRouter, HTTPException
from ..services.database import get_db
from ..models.orders import Order
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from ..auth.jwt import get_current_user
from ..schemas.order_status_update import OrderStatusUpdate
from datetime import datetime

router = APIRouter()

@router.put("/user_order_status")
async def update_user_order_status(
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    User can update their own order status.
    - Allowed: working -> delivered (customer confirms delivery)
    - Allowed: delivered -> completed (customer confirms receipt)
    - User cannot change to pending or working
    """
    user_id = current_user["id"]

    # Get the order
    order_result = await db.execute(
        select(Order).filter(Order.order_id == status_update.order_id)
    )
    order = order_result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify this order belongs to the current user
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="This order does not belong to you")

    # Validate status transitions for customers
    allowed_transitions = {
        "working": ["delivered"],
        "delivered": ["completed"],
        "pending": [],  # Cannot change from pending
        "completed": [],  # Cannot change from completed
        "cancelled": []  # Cannot change from cancelled
    }

    if status_update.status not in allowed_transitions.get(order.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from '{order.status}' to '{status_update.status}'. "
                   f"Customers can only change: working -> delivered -> completed. "
                   f"Allowed transitions: {allowed_transitions.get(order.status, [])}"
        )

    # Update the order status
    order.status = status_update.status
    order.status_updated_at = datetime.now()

    await db.commit()

    return {
        "success": True,
        "message": "Order marked as completed",
        "order_id": order.order_id,
        "status": order.status,
        "status_updated_at": order.status_updated_at
    }
