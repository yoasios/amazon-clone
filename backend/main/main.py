from fastapi import FastAPI
from ..routes.health_check import router as health_router
from ..routes.login import router as login_router
from ..routes.signin import router as signin_router
from ..routes.shop_login import router as shop_router
from ..services.database import engine, Base
from ..models.users_class import User
from ..models.cart_class import Cart
from ..models.products import Product
from ..models.shop_data import Shop

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(health_router)
app.include_router(login_router)
app.include_router(signin_router)
app.include_router(shop_router)
