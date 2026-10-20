from fastapi import APIRouter, HTTPException
from ..services.database import get_db
from ..models.products import Products
from ..models.cart_class import Cart
from ..models.orders import Order
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import Depends, Response
from ..auth.jwt import get_current_user
from ..schemas.buy_input import BuyInput
from datetime import datetime

router = APIRouter()

@router.post("/buy_product")
async def buy_product(
    buy_input: BuyInput,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user["id"]
    
    if not buy_input.items:
        raise HTTPException(status_code=400, detail="No items in cart")
    
    purchased_items = []
    shop_ids = []  # Store shop_ids separately
    total_cost = 0
    
    try:
        # Process each item in the cart with atomic operations
        for item in buy_input.items:
            # ATOMIC: Check stock and deduct in one operation
            result = await db.execute(
                update(Products)
                .where(Products.product_id == item.product_id)
                .where(Products.amount >= item.quantity)
                .values(amount=Products.amount - item.quantity)
                .returning(Products.product_name, Products.product_price, Products.shop_id)
            )
            
            product_data = result.fetchone()
            
            if product_data is None:
                # Product doesn't exist OR not enough stock
                product_check = await db.execute(
                    select(Products).filter(Products.product_id == item.product_id)
                )
                product = product_check.scalar_one_or_none()
                
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Not enough stock for product {product.product_name}. Available: {product.amount}, Requested: {item.quantity}"
                    )
            
            product_name, product_price, shop_id = product_data
            
            purchased_items.append({
                "product_id": item.product_id,
                "product_name": product_name,
                "quantity": item.quantity,
                "price": product_price,
                "total": item.quantity * product_price
            })
            shop_ids.append(shop_id)
            
            total_cost += item.quantity * product_price
        
        # All items validated and stock deducted successfully
        # Now create order and cart items
        order = Order(
            user_id=user_id,
            total_cost=total_cost,
            status="completed"
        )
        db.add(order)
        await db.flush()  # Get order_id
        
        # Add all items to cart with order_id
        for i, item in enumerate(buy_input.items):
            cart_item = Cart(
                user_id=user_id,
                product_id=item.product_id,
                shop_id=shop_ids[i],
                order_id=order.order_id,
                quantity=item.quantity,
                total_price=item.quantity * purchased_items[i]["price"],
                timestamp=datetime.now()
            )
            db.add(cart_item)
        
        # Commit all changes
        await db.commit()
        
        return {
            "success": True,
            "message": "Purchase successful",
            "order_id": order.order_id,
            "total_cost": total_cost,
            "items_purchased": len(purchased_items),
            "items": purchased_items
        }
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")
