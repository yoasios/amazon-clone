from pydantic import BaseModel

class ProductInput(BaseModel):
    product_name: str
    product_price: int
    product_description: str
    amount: int = 0
