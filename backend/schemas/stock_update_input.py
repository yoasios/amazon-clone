from pydantic import BaseModel
from typing import Optional

class ProductStockInput(BaseModel):
    product_id: int
    amount: int
    unit: Optional[str] = None