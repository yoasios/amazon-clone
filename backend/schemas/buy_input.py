from pydantic import BaseModel
from typing import List, Optional

class BuyItem(BaseModel):
    product_id: int
    quantity: Optional[int] = 1  # Default to 1 if not specified

class BuyInput(BaseModel):
    items: List[BuyItem]
