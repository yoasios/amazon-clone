from sqlalchemy import Column, Integer, String, ForeignKey
from ..services.database import Base

class Shop(Base):
    __tablename__ = "shop"
    shop_id = Column(Integer, primary_key=True, index=True)
    shop_name = Column(String, index=True)
    shop_description = Column(String)
    shop_address = Column(String)
    shop_phone = Column(String)
    shop_email = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
