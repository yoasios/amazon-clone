from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..services.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    phone = Column(String)
    address = Column(String)




