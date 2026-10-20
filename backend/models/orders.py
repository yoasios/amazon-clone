from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from ..services.database import Base

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    total_cost = Column(Integer)
    status = Column(String, default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.now)
