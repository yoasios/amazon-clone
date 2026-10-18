from sqlalchemy import Column, Integer, String, ForeignKey
from ..services.database import Base
from .shop_data import Shop

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, unique=True, index=True)
    product_price = Column(Integer)
    product_description = Column(String)
    amount = Column(Integer)
    shop_id = Column(Integer, ForeignKey("shop.shop_id"), index=True)