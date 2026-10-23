from pydantic import BaseModel

class OrderStatusUpdate(BaseModel):
    order_id: int
    status: str  # "pending" or "working" (shopkeeper) or "completed" (user)
