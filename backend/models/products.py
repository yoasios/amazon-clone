from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from ..services.database import Base
from .shop_data import Shop

class Products(Base):
    __tablename__ = "product"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    product_price = Column(Integer)
    product_description = Column(String)
    amount = Column(Integer, default=1)
    shop_id = Column(Integer, ForeignKey("shop.shop_id"), index=True)
