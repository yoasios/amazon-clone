from pydantic import BaseModel

class product_input(BaseModel):
    product_name: str
    product_price: int
    product_description: str
    amount: int
