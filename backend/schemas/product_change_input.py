from pydantic import BaseModel
from typing import Optional

class ProductChangeInput(BaseModel):
    product_id: int
    product_name: Optional[str] = None
    product_price: Optional[int] = None
    product_description: Optional[str] = None
    amount: Optional[int] = None
