from pydantic import BaseModel

class ShopInput(BaseModel):
    shop_name: str
    shop_description: str
    shop_address: str
    shop_phone: str
    shop_email: str
