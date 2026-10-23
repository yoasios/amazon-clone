from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..services.database import get_db
from ..models.orders import Order
from ..models.cart_class import Cart
from ..models.users_class import User
from ..auth.jwt import get_current_user
from ..auth.shop_cookies import get_current_shop

router = APIRouter()

@router.get("/product_sales")
async def get_product_sales(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    current_shop = Depends(get_current_shop)
):
    """Get sales history for shop's products with customer information"""
    shop_id = current_shop["shop_id"]
    
    # Query all orders for this shop with their items and user information
    result = await db.execute(
        select(Order, User)
        .join(User, Order.user_id == User.id)
        .filter(Order.shop_id == shop_id)
        .order_by(Order.created_at.desc())
    )
    orders = result.all()
    
    # Build product sales summary
    product_sales = {}
    
    for order, user in orders:
        result = await db.execute(
            select(Cart).filter(Cart.order_id == order.order_id)
        )
        cart_items = result.scalars().all()
        
        for item in cart_items:
            product_id = item.product_id
            product_name = item.product_name_snapshot
            quantity = item.quantity
            price = item.product_price_snapshot
            customer_email = user.email
            customer_name = user.name
            
            if product_id not in product_sales:
                product_sales[product_id] = {
                    "product_id": product_id,
                    "product_name": product_name,
                    "total_quantity": 0,
                    "total_revenue": 0,
                    "total_orders": 0,
                    "buyers": []
                }
            
            product_sales[product_id]["total_quantity"] += quantity
            product_sales[product_id]["total_revenue"] += price * quantity
            product_sales[product_id]["total_orders"] += 1
            
            # Track unique buyers
            if customer_email not in product_sales[product_id]["buyers"]:
                product_sales[product_id]["buyers"].append(customer_email)
    
    # Convert to list
    sales_list = list(product_sales.values())
    
    return {
        "product_sales": sales_list,
        "total_products": len(sales_list)
    }

@router.get("/product_sales/{product_id}")
async def get_product_sales_detail(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    current_shop = Depends(get_current_shop)
):
    """Get detailed sales history for a specific product"""
    shop_id = current_shop["shop_id"]
    
    # Query all orders for this shop with full user information
    result = await db.execute(
        select(Order, User)
        .join(User, Order.user_id == User.id)
        .filter(Order.shop_id == shop_id)
        .order_by(Order.created_at.desc())
    )
    orders = result.all()
    
    # Find all cart items for this product
    sales_details = []
    
    for order, user in orders:
        result = await db.execute(
            select(Cart).filter(
                Cart.order_id == order.order_id,
                Cart.product_id == product_id
            )
        )
        cart_items = result.scalars().all()
        
        for item in cart_items:
            sales_details.append({
                "order_id": order.order_id,
                "customer_name": user.name,
                "customer_email": user.email,
                "customer_phone": user.phone,
                "customer_address": user.address,
                "quantity": item.quantity,
                "price": item.product_price_snapshot,
                "total": item.product_price_snapshot * item.quantity,
                "purchase_date": order.created_at.isoformat(),
                "order_status": order.status
            })
    
    return {
        "product_id": product_id,
        "sales": sales_details,
        "total_sales": len(sales_details)
    }
