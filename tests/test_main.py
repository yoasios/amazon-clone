import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from backend.main.main import app
from backend.models.users_class import User
from backend.models.shop_data import Shop
from backend.models.products import Product
from backend.services.database import Base

# Test database URL (separate from main database)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database for each test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    """Create a test client with database override"""
    from backend.services.database import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# Test Health Check
@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# Test User Signin
@pytest.mark.asyncio
async def test_signin_success(client: AsyncClient):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    response = await client.post("/signin", json=user_data)
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"
    assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_signin_duplicate_email(client: AsyncClient):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    # First signin
    await client.post("/signin", json=user_data)
    # Second signin with same email
    response = await client.post("/signin", json=user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# Test User Login
@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # First create a user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    await client.post("/signin", json=user_data)

    # Now login
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = await client.post("/login", json=login_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Logged in successfully"
    assert "token" in response.json()
    assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = await client.post("/login", json=login_data)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    # Create user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    await client.post("/signin", json=user_data)

    # Try login with wrong password
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    response = await client.post("/login", json=login_data)
    assert response.status_code == 400
    assert "Invalid password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_with_shop(client: AsyncClient, db_session: AsyncSession):
    # Create user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    await client.post("/signin", json=user_data)

    # Create shop manually in database
    result = await db_session.execute(text("SELECT id FROM users WHERE email = 'test@example.com'"))
    user = result.fetchone()
    user_id = user[0]

    shop = Shop(
        shop_name="Test Shop",
        shop_description="Test Description",
        shop_address="123 Main St",
        shop_phone="1234567890",
        shop_email="shop@example.com",
        user_id=user_id
    )
    db_session.add(shop)
    await db_session.commit()

    # Login - should return shop details
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = await client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "shop" in response.json()
    assert response.json()["shop"]["shop_name"] == "Test Shop"


# Test Shop Creation
@pytest.mark.asyncio
async def test_shop_login_success(client: AsyncClient):
    # Create and login user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    await client.post("/signin", json=user_data)

    # Create shop
    shop_data = {
        "shop_name": "Test Shop",
        "shop_description": "Test Description",
        "shop_address": "123 Main St",
        "shop_phone": "1234567890",
        "shop_email": "shop@example.com"
    }
    response = await client.post("/shop_login", json=shop_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Shop created successfully"
    assert "shop_id" in response.json()
    assert "shop_access_token" in response.cookies


@pytest.mark.asyncio
async def test_shop_login_without_auth(client: AsyncClient):
    # Try to create shop without logging in
    shop_data = {
        "shop_name": "Test Shop",
        "shop_description": "Test Description",
        "shop_address": "123 Main St",
        "shop_phone": "1234567890",
        "shop_email": "shop@example.com"
    }
    response = await client.post("/shop_login", json=shop_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_shop_login_duplicate(client: AsyncClient):
    # Create and login user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    await client.post("/signin", json=user_data)

    # Create first shop
    shop_data = {
        "shop_name": "Test Shop",
        "shop_description": "Test Description",
        "shop_address": "123 Main St",
        "shop_phone": "1234567890",
        "shop_email": "shop@example.com"
    }
    await client.post("/shop_login", json=shop_data)

    # Try to create duplicate shop
    response = await client.post("/shop_login", json=shop_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# Test Product Creation
@pytest.mark.asyncio
async def test_add_product_success(client: AsyncClient):
    # Create and login user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    await client.post("/signin", json=user_data)

    # Create shop
    shop_data = {
        "shop_name": "Test Shop",
        "shop_description": "Test Description",
        "shop_address": "123 Main St",
        "shop_phone": "1234567890",
        "shop_email": "shop@example.com"
    }
    await client.post("/shop_login", json=shop_data)

    # Add product
    product_data = {
        "product_name": "Laptop",
        "product_price": 999,
        "product_description": "High-performance laptop",
        "amount": 10
    }
    response = await client.post("/products", json=product_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Product added successfully"
    assert "product_id" in response.json()


@pytest.mark.asyncio
async def test_add_product_without_shop_token(client: AsyncClient):
    # Create and login user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    await client.post("/signin", json=user_data)

    # Try to add product without shop token
    product_data = {
        "product_name": "Laptop",
        "product_price": 999,
        "product_description": "High-performance laptop",
        "amount": 10
    }
    response = await client.post("/products", json=product_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_product_duplicate(client: AsyncClient):
    # Create and login user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    await client.post("/signin", json=user_data)

    # Create shop
    shop_data = {
        "shop_name": "Test Shop",
        "shop_description": "Test Description",
        "shop_address": "123 Main St",
        "shop_phone": "1234567890",
        "shop_email": "shop@example.com"
    }
    await client.post("/shop_login", json=shop_data)

    # Add first product
    product_data = {
        "product_name": "Laptop",
        "product_price": 999,
        "product_description": "High-performance laptop",
        "amount": 10
    }
    await client.post("/products", json=product_data)

    # Try to add duplicate product
    response = await client.post("/products", json=product_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# Test Complete Flow
@pytest.mark.asyncio
async def test_complete_flow(client: AsyncClient):
    """Test the complete user flow: signin -> shop_login -> add_product"""
    # Step 1: Signin
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    response = await client.post("/signin", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.cookies

    # Step 2: Create Shop
    shop_data = {
        "shop_name": "Test Shop",
        "shop_description": "Test Description",
        "shop_address": "123 Main St",
        "shop_phone": "1234567890",
        "shop_email": "shop@example.com"
    }
    response = await client.post("/shop_login", json=shop_data)
    assert response.status_code == 200
    assert "shop_access_token" in response.cookies
    shop_id = response.json()["shop_id"]

    # Step 3: Add Product
    product_data = {
        "product_name": "Laptop",
        "product_price": 999,
        "product_description": "High-performance laptop",
        "amount": 10
    }
    response = await client.post("/products", json=product_data)
    assert response.status_code == 200
    assert "product_id" in response.json()

    # Step 4: Login again to verify shop is returned
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = await client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "shop" in response.json()
    assert response.json()["shop"]["shop_id"] == shop_id
