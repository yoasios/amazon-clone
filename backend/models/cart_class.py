
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func
from ..services.database import Base
from .users_class import User
from .products import Products
from .shop_data import Shop

class Cart(Base):
    __tablename__ = "cart"
    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), index=True)  # Links cart to order
    quantity = Column(Integer)
    total_price = Column(Integer)
    timestamp = Column(DateTime(timezone=True))
    shop_id = Column(Integer, ForeignKey("shop.shop_id"), index=True)
    # Snapshot fields - store product details at time of purchase
    product_name_snapshot = Column(String)  # Product name when purchased
    product_price_snapshot = Column(Integer)  # Price when purchased
    product_description_snapshot = Column(Text)  # Description when purchased

