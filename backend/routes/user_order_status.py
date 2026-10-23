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
    - Only allowed: working -> completed (user confirms receipt)
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

    # Only allow user to set status to "completed" if current status is "working"
    if status_update.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Users can only mark orders as completed"
        )

    if order.status != "working":
        raise HTTPException(
            status_code=400,
            detail=f"Order must be in 'working' status to be marked as completed. Current status: {order.status}"
        )

    # Update the order status
    order.status = "completed"
    order.status_updated_at = datetime.now()

    await db.commit()

    return {
        "success": True,
        "message": "Order marked as completed",
        "order_id": order.order_id,
        "status": order.status,
        "status_updated_at": order.status_updated_at
    }
