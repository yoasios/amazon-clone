from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from ..routes.health_check import router as health_router
from ..routes.login import router as login_router
from ..routes.signin import router as signin_router
from ..routes.shop_login import router as shop_router
from ..routes.logout import router as logout_router
from ..services.database import engine, Base
from ..models.users_class import User
from ..models.cart_class import Cart
from ..models.products import Products
from ..models.shop_data import Shop
from ..models.orders import Order
from ..routes.products import router as products_router
from ..routes.view_products import router as view_products_router
from ..routes.search_products import router as search_products_router
from ..routes.user_shops import router as user_shops_router
from ..routes.switch_shop import router as switch_shop_router
from ..routes.buy_product import router as buy_product_router
from ..routes.order_status import router as order_status_router
from ..routes.order_history import router as order_history_router
from ..routes.product_change import router as product_change_router
from ..routes.ProductStock import router as product_stock_router
from ..routes.shop_orders import router as shop_orders_router
from ..routes.update_order_status import router as update_order_status_router
from ..routes.user_order_status import router as user_order_status_router
from ..routes.product_sales import router as product_sales_router
from ..routes.cancel_order import router as cancel_order_router

app = FastAPI()

# CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(health_router)
app.include_router(login_router)
app.include_router(signin_router)
app.include_router(shop_router)
app.include_router(logout_router)
app.include_router(products_router)
app.include_router(view_products_router)
app.include_router(search_products_router)
app.include_router(user_shops_router)
app.include_router(switch_shop_router)
app.include_router(buy_product_router)
app.include_router(order_status_router)
app.include_router(order_history_router)
app.include_router(product_change_router)
app.include_router(product_stock_router)
app.include_router(shop_orders_router)
app.include_router(update_order_status_router)
app.include_router(user_order_status_router)
app.include_router(product_sales_router)
app.include_router(cancel_order_router)

# Mount frontend static files AFTER API routes (API routes take precedence)
frontend_path = Path(__file__).parent.parent.parent / "front_end"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
