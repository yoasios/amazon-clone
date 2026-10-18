from fastapi import APIRouter, HTTPException
from ..schemas.shop_input import shop_input
from ..services.database import get_db
from ..models.shop_data import Shop
from ..models.products import Product
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import Depends, Response
from ..auth.jwt import get_current_user
from ..auth.products_cookie import get_current_shop
from ..services.database import get_db
from ..schemas.product_input import product_input

router = APIRouter()

@router.post("/products")
async def add_product(new_product : product_input  , response: Response,
db:AsyncSession = Depends(get_db), current_shop = Depends(get_current_shop)):
 shop_id, user_id = current_shop

 # Check if product with same name already exists in this shop
 result = await db.execute(
     select(Product).filter(
         Product.product_name == new_product.product_name,
         Product.shop_id == shop_id
     )
 )
 existing_product = result.scalar_one_or_none()

 if existing_product:
     raise HTTPException(status_code=400, detail="Product with this name already exists in your shop")

 # Add new product
 new_product_obj = Product(
     product_name=new_product.product_name,
     product_price=new_product.product_price,
     product_description=new_product.product_description,
     amount=new_product.amount,
     shop_id=shop_id
 )

 try:
     db.add(new_product_obj)
     await db.commit()
     await db.refresh(new_product_obj)
     return {"message": "Product added successfully", "product_id": new_product_obj.product_id}
 except Exception as e:
     await db.rollback()
     raise HTTPException(status_code=500, detail="Failed to add product")

