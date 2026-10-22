# Amazon Clone Backend

A FastAPI-based backend for an e-commerce platform with multi-user authentication, shop management, product inventory, and order tracking.

## Features

- **User Authentication**
  - User registration with phone and address
  - User login with JWT tokens
  - Cookie-based authentication (httponly, secure)
  - Bcrypt password hashing
  - Auto-login with valid cookies

- **Shop Management**
  - Shop creation for authenticated users
  - Shop-specific JWT tokens
  - Shop switching between multiple shops
  - Ownership verification for all operations

- **Product Management**
  - Add products to shops
  - Product information updates (optional fields)
  - Atomic stock updates with ownership check
  - Product snapshot at purchase time (prevents data drift)

- **Order Management**
  - Bulk purchases with atomic stock deduction
  - Order history per user
  - Product snapshots preserve purchase details
  - Transaction rollback on errors

- **Search Functionality**
  - Search by shop ID
  - Search by product name
  - Global search across all products (max 20 results)

- **Database**
  - Async SQLAlchemy with SQLite/PostgreSQL support
  - Models for Users, Shops, Products, Cart, and Orders
  - Automatic table creation on startup
  - Transaction handling and rollback

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite with async support (aiosqlite) / PostgreSQL (asyncpg)
- **ORM:** SQLAlchemy (async)
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** Bcrypt (passlib)
- **Python:** 3.14

## Project Structure

```
backend/
├── auth/
│   ├── jwt.py              # JWT token creation and validation
│   ├── passlib_setup.py    # Password hashing setup
│   └── products_cookie.py # Shop-specific token management
├── main/
│   └── main.py             # FastAPI app entry point
├── models/
│   ├── users_class.py      # User model (includes phone, address)
│   ├── shop_data.py        # Shop model
│   ├── products.py         # Product model
│   ├── cart_class.py       # Cart model (includes product snapshots)
│   └── orders.py           # Order model
├── routes/
│   ├── signin.py           # User registration endpoint
│   ├── login.py            # User login endpoint
│   ├── shop_login.py       # Shop creation endpoint
│   ├── user_shops.py       # Get user's shops
│   ├── switch_shop.py      # Switch between shops
│   ├── products.py         # Add products to shop
│   ├── product_change.py   # Update product information
│   ├── ProductStock.py     # Update product stock
│   ├── view_products.py    # View shop products
│   ├── search_products.py  # Search products
│   ├── buy_product.py      # Purchase products
│   ├── order_history.py    # Get user's order history
│   └── order_status.py     # Get order status
├── schemas/
│   ├── signin_input.py     # User registration schema (includes phone, address)
│   ├── shop_input.py       # Shop creation schema
│   ├── product_input.py    # Product schema
│   ├── product_change_input.py  # Product update schema
│   ├── stock_update_input.py    # Stock update schema
│   ├── buy_input.py        # Purchase schema
│   └── search_input.py     # Search schema
└── services/
    ├── database.py         # Database connection and session (SQLite/PostgreSQL)
    ├── settings.py         # Environment configuration
    └── config.py           # Config settings
```

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yoasios/amazon-clone.git
   cd amazon-clone
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn sqlalchemy[asyncio] aiosqlite passlib[bcrypt] pyjwt python-dotenv
   ```



5. **Run the server**
   ```bash
   uvicorn backend.main.main:app --reload
   ```

The API will be available at `http://127.0.0.1:8000`

## API Endpoints

### User Registration
**POST** `/signin`

Request body:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "yourpassword123",
  "phone": "1234567890",
  "address": "123 Main Street, City"
}
```

Response:
```json
{
  "message": "User created successfully"
}
```

### User Login
**POST** `/login`

Request body:
```json
{
  "email": "john@example.com",
  "password": "yourpassword123"
}
```

Response (without shop):
```json
{
  "message": "Logged in successfully",
  "token": "jwt-token"
}
```

Response (with shop):
```json
{
  "message": "Logged in successfully",
  "token": "jwt-token",
  "shop": {
    "shop_name": "My Shop",
    "shop_description": "Shop description",
    "shop_address": "123 Main St",
    "shop_phone": "1234567890",
    "shop_email": "shop@example.com"
  }
}
```

### Shop Creation
**POST** `/shop_login`

Requires authentication (access_token cookie).

Request body:
```json
{
  "shop_name": "My Awesome Shop",
  "shop_description": "A great place to shop",
  "shop_address": "123 Main Street, City",
  "shop_phone": "1234567890",
  "shop_email": "shop@example.com"
}
```

Response:
```json
{
  "message": "Shop created successfully",
  "shop_id": 1
}
```

### Get User's Shops
**GET** `/user_shops`

Requires authentication (access_token cookie).

Response:
```json
{
  "shops": [
    {
      "shop_id": 1,
      "shop_name": "My Shop",
      "shop_description": "Shop description"
    }
  ]
}
```

### Switch Shop
**POST** `/switch_shop/{shop_id}`

Requires authentication (access_token cookie). Verifies shop ownership.

Response:
```json
{
  "message": "Switched to shop successfully"
}
```

### Add Product
**POST** `/products`

Requires shop authentication (shop_token cookie).

Request body:
```json
{
  "product_name": "Camera",
  "product_price": 100,
  "amount": 50,
  "unit": "pieces",
  "product_description": "Digital camera"
}
```

Response:
```json
{
  "message": "Product added successfully",
  "product_id": 1
}
```

### Update Product Information
**PUT** `/product_change`

Requires authentication (access_token cookie). Verifies product ownership.

Request body (all fields optional):
```json
{
  "product_id": 1,
  "product_name": "Updated Camera",
  "product_price": 150,
  "amount": 30
}
```

Response:
```json
{
  "message": "Product updated successfully",
  "updated_fields": ["product_name", "product_price", "amount"]
}
```

### Update Product Stock
**PUT** `/product_stock`

Requires authentication (access_token cookie). Verifies product ownership.

Request body:
```json
{
  "product_id": 1,
  "amount": 100,
  "unit": "pieces"
}
```

Response:
```json
{
  "message": "Product stock updated successfully",
  "product_id": 1,
  "new_amount": 100
}
```

### View Shop Products
**POST** `/view/{shop_id}`

Requires shop authentication (shop_token cookie).

Response:
```json
{
  "products": [
    {
      "product_id": 1,
      "product_name": "Camera",
      "product_price": 100,
      "amount": 50
    }
  ]
}
```

### Search Products by Shop ID
**POST** `/search/shop`

Request body:
```json
{
  "shop_id": 1
}
```

Response:
```json
{
  "products": [...]
}
```

### Search Products by Name
**POST** `/search/name`

Request body:
```json
{
  "query": "camera"
}
```

Response:
```json
{
  "products": [...]
}
```

### Global Search
**POST** `/search`

Request body:
```json
{
  "query": "camera"
}
```

Response (max 20 results):
```json
{
  "products": [...]
}
```

### Purchase Products
**POST** `/buy_product`

Requires authentication (access_token cookie). Atomic stock deduction.

Request body:
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

Response:
```json
{
  "message": "Purchase successful",
  "order_id": 1,
  "total_cost": 200
}
```

### Order History
**GET** `/my_orders`

Requires authentication (access_token cookie).

Response:
```json
{
  "orders": [
    {
      "order_id": 1,
      "total_cost": 200,
      "status": "completed",
      "items": [
        {
          "product_name_snapshot": "Camera",
          "product_price_snapshot": 100,
          "quantity": 2
        }
      ]
    }
  ]
}
```

### Health Check
**GET** `/health`

Response:
```json
{
  "status": "healthy"
}
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Testing

The project includes comprehensive pytest tests and a load test script.

**Install test dependencies:**
```bash
pip install pytest pytest-asyncio httpx
```

**Run unit tests:**
```bash
pytest tests/ -v
```

**Run load test (100 bots, 20 concurrent requests):**
```bash
python load_test.py
```

**Load test coverage includes:**
- User registration with phone and address
- Login and wrong password verification
- Shop creation and ownership verification
- Product addition and stock management
- Product information updates
- Product stock updates
- Shop viewing and product search
- Shop switching
- Bulk purchases with atomic stock deduction
- Order history with product snapshots
- Global search functionality
- Data integrity checks

**Note:** Load test with SQLite may show database locking errors due to SQLite's file-based locking. Use PostgreSQL for production concurrency.

## Security

- Passwords are hashed using Bcrypt
- JWT tokens expire after 60 minutes
- Cookies are httponly to prevent XSS attacks
- `.env` file is excluded from version control
- Database files are excluded from version control

## License

This project is private and confidential.
