from fastapi import APIRouter, HTTPException
from ..schemas.shop_input import ShopInput
from ..services.database import get_db
from ..models.shop_data import Shop
from ..models.products import Products
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import Depends, Response
from ..auth.jwt import get_current_user


router = APIRouter()

@router.post("/view/{shop_id}")
async def view(shop_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(Products).filter(Products.shop_id == shop_id))
    return result.scalars().all()