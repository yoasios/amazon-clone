from fastapi import APIRouter, HTTPException
from ..schemas.search_input import SearchInput
from ..services.database import get_db
from ..models.products import Products
from ..models.shop_data import Shop
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import Depends, Response
from ..auth.jwt import get_current_user

router = APIRouter()

@router.post("/search")
async def search_products(search: SearchInput, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Search for products across all shops with pagination.
    """
    # Fixed limit to prevent excessive queries
    limit = 20
    
    # Search for products that match the query in name or description
    search_pattern = f"%{search.query}%"
    
    # Query products with shop information
    query = (
        select(Products, Shop)
        .join(Shop, Products.shop_id == Shop.shop_id)
        .filter(
            or_(
                Products.product_name.ilike(search_pattern),
                Products.product_description.ilike(search_pattern)
            )
        )
        .limit(limit)
        .offset(search.offset)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Format the response with product and shop information
    products_with_shops = []
    for product, shop in rows:
        products_with_shops.append({
            "product_id": product.product_id,
            "product_name": product.product_name,
            "product_price": product.product_price,
            "product_description": product.product_description,
            "amount": product.amount,
            "shop": {
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "shop_description": shop.shop_description,
                "shop_address": shop.shop_address,
                "shop_phone": shop.shop_phone,
                "shop_email": shop.shop_email
            }
        })
    
    return {
        "results": products_with_shops,
        "count": len(products_with_shops),
        "limit": limit,
        "offset": search.offset
    }
