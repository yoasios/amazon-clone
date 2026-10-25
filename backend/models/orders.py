from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from ..services.database import Base

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    shop_id = Column(Integer, ForeignKey("shop.shop_id"), index=True)  # Which shop received the order
    total_cost = Column(Integer)
    status = Column(String, default="pending")  # pending, working, completed, cancelled
    status_updated_at = Column(DateTime, default=datetime.now)  # When status last changed
    created_at = Column(DateTime, default=datetime.now)
    cancellation_fee = Column(Integer, default=0)  # Refund cancellation fee in cents
