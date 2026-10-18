import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.services.database import AsyncSessionLocal, engine, Base
from backend.models.users_class import User
from backend.models.shop_data import Shop
from backend.models.products import Products
from backend.models.cart_class import Cart

# Sample data for realistic generation
FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
SHOP_NAMES = ["Tech Haven", "Fashion Forward", "Home Essentials", "Sports Central", "Book Nook", "Gourmet Garden", "Pet Paradise", "Beauty Bliss", "Auto World", "Music Box", "Toy Kingdom", "Health Hub", "Art Studio", "Electronic Emporium", "Food Corner", "Clothing Closet", "Shoe Shack", "Watch World", "Jewelry Junction", "Phone Palace"]
PRODUCT_PREFIXES = ["Super", "Ultra", "Pro", "Mega", "Max", "Smart", "Digital", "Wireless", "Portable", "Compact"]
PRODUCT_TYPES = ["Laptop", "Phone", "Tablet", "Watch", "Headphones", "Camera", "Speaker", "Monitor", "Keyboard", "Mouse", "Charger", "Case", "Stand", "Cable", "Adapter"]
PRODUCT_ADJECTIVES = ["Black", "White", "Silver", "Blue", "Red", "Green", "Gold", "Rose", "Space Gray", "Midnight"]

def generate_random_email(first_name: str, last_name: str, num: int) -> str:
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
    return f"{first_name.lower()}.{last_name.lower()}{num}@{random.choice(domains)}"

def generate_random_phone() -> str:
    return f"{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"

def generate_random_address() -> str:
    streets = ["Main St", "Oak Ave", "Elm Blvd", "Pine Ln", "Maple Dr", "Cedar Rd", "Washington Ave", "Jefferson St", "Lincoln Blvd", "Madison Ln"]
    return f"{random.randint(100, 9999)} {random.choice(streets)}"

def generate_random_product_name() -> str:
    return f"{random.choice(PRODUCT_PREFIXES)} {random.choice(PRODUCT_ADJECTIVES)} {random.choice(PRODUCT_TYPES)}"

def generate_random_description() -> str:
    descriptions = [
        "High quality product with excellent features",
        "Premium item with amazing performance",
        "Top-rated product with great value",
        "Best-in-class features and durability",
        "Innovative design with superior quality",
        "Reliable product with outstanding performance",
        "Excellent choice for everyday use",
        "Professional grade with exceptional quality"
    ]
    return random.choice(descriptions)

async def seed_users(session: AsyncSession, count: int = 2000):
    print(f"Seeding {count} users...")
    users = []
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        email = generate_random_email(first_name, last_name, i)
        password = "hashed_password_" + str(i)  # Simple placeholder hash
        
        user = User(name=name, email=email, password=password)
        users.append(user)
        
        if len(users) >= 100:  # Batch insert
            session.add_all(users)
            await session.commit()
            print(f"  Progress: {i + 1}/{count}")
            users = []
    
    if users:
        session.add_all(users)
        await session.commit()
    
    print(f"[OK] Completed seeding {count} users")

async def seed_shops(session: AsyncSession, count: int = 2000):
    print(f"Seeding {count} shops...")
    
    # Get all user IDs
    result = await session.execute(select(User.id))
    user_ids = result.scalars().all()
    
    if not user_ids:
        print("Warning: No users found. Please seed users first.")
        return
    
    shops = []
    for i in range(count):
        user_id = random.choice(user_ids)
        shop_name = f"{random.choice(SHOP_NAMES)} {i}"
        shop_description = f"{shop_name} - Your one-stop shop for quality products"
        shop_address = generate_random_address()
        shop_phone = generate_random_phone()
        shop_email = f"shop{i}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}"
        
        shop = Shop(
            shop_name=shop_name,
            shop_description=shop_description,
            shop_address=shop_address,
            shop_phone=shop_phone,
            shop_email=shop_email,
            user_id=user_id
        )
        shops.append(shop)
        
        if len(shops) >= 100:
            session.add_all(shops)
            await session.commit()
            print(f"  Progress: {i + 1}/{count}")
            shops = []
    
    if shops:
        session.add_all(shops)
        await session.commit()
    
    print(f"[OK] Completed seeding {count} shops")

async def seed_products(session: AsyncSession, count: int = 2000):
    print(f"Seeding {count} products...")
    
    # Get all shop IDs
    result = await session.execute(select(Shop.shop_id))
    shop_ids = result.scalars().all()
    
    if not shop_ids:
        print("Warning: No shops found. Please seed shops first.")
        return
    
    products = []
    for i in range(count):
        shop_id = random.choice(shop_ids)
        product_name = generate_random_product_name()
        product_price = random.randint(10, 5000)
        product_description = generate_random_description()
        amount = random.randint(0, 100)
        
        product = Products(
            product_name=product_name,
            product_price=product_price,
            product_description=product_description,
            amount=amount,
            shop_id=shop_id
        )
        products.append(product)
        
        if len(products) >= 100:
            session.add_all(products)
            await session.commit()
            print(f"  Progress: {i + 1}/{count}")
            products = []
    
    if products:
        session.add_all(products)
        await session.commit()
    
    print(f"[OK] Completed seeding {count} products")

async def seed_cart(session: AsyncSession, count: int = 2000):
    print(f"Seeding {count} cart items...")
    
    # Get all user IDs, product IDs, and shop IDs
    result = await session.execute(select(User.id))
    user_ids = result.scalars().all()
    
    result = await session.execute(select(Products.product_id))
    product_ids = result.scalars().all()
    
    result = await session.execute(select(Shop.shop_id))
    shop_ids = result.scalars().all()
    
    if not user_ids or not product_ids or not shop_ids:
        print("Warning: Missing required data. Please seed users, shops, and products first.")
        return
    
    carts = []
    for i in range(count):
        user_id = random.choice(user_ids)
        product_id = random.choice(product_ids)
        shop_id = random.choice(shop_ids)
        quantity = random.randint(1, 10)
        total_price = quantity * random.randint(10, 500)
        timestamp = datetime.now() - timedelta(days=random.randint(0, 365))
        
        cart = Cart(
            user_id=user_id,
            product_id=product_id,
            shop_id=shop_id,
            quantity=quantity,
            total_price=total_price,
            timestamp=timestamp
        )
        carts.append(cart)
        
        if len(carts) >= 100:
            session.add_all(carts)
            await session.commit()
            print(f"  Progress: {i + 1}/{count}")
            carts = []
    
    if carts:
        session.add_all(carts)
        await session.commit()
    
    print(f"[OK] Completed seeding {count} cart items")

async def main():
    print("Starting database seeding...")
    print("=" * 50)
    
    # Create tables first
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Tables created successfully")
    
    async with AsyncSessionLocal() as session:
        try:
            # Seed in order to respect foreign key constraints
            await seed_users(session, 2000)
            await seed_shops(session, 2000)
            await seed_products(session, 2000)
            await seed_cart(session, 2000)
            
            print("=" * 50)
            print("[OK] Database seeding completed successfully!")
            
        except Exception as e:
            print(f"Error during seeding: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())
