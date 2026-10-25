# Amazon Clone - Full Stack E-Commerce Platform

A complete full-stack e-commerce platform with FastAPI backend and browser frontend, featuring multi-user authentication, shop management, product inventory, order tracking, and sales analytics.

## Author

**Username:** yoasios  
**Email:** vangoyt867@gmail.com

## Features

## Features

### Backend (FastAPI)
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
  - **Order Status Management**
    - Status flow: pending → working → completed
    - Shopkeepers can update pending/working status
    - Customers can mark orders as completed
    - Timestamp tracking for status changes

- **Search Functionality**
  - Search by shop ID
  - Search by product name
  - Global search across all products (max 20 results)

- **Sales Analytics**
  - Product sales summary per shop
  - Detailed sales history with customer information
  - Revenue tracking
  - Customer contact details (name, email, phone, address)

- **Database**
  - Async SQLAlchemy with PostgreSQL support (production)
  - SQLite support for development
  - Models for Users, Shops, Products, Cart, and Orders
  - Automatic table creation on startup
  - Transaction handling and rollback
  - Connection pooling for PostgreSQL

### Frontend (Browser UI)
- **Customer Interface**
  - Product browsing and search
  - Shopping cart functionality
  - Bulk purchasing
  - Order history tracking
  - Order status viewing and completion

- **Seller Dashboard**
  - Professional tabbed interface (Products, Orders, Sales)
  - Shop management (create, view, switch)
  - Product management (add, update, stock)
  - Order management (view, update status)
  - Sales analytics (revenue, items sold, customer details)
  - Responsive design with modern UI

## Tech Stack

## Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL (asyncpg) / SQLite (aiosqlite) for development
- **ORM:** SQLAlchemy (async)
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** Bcrypt (passlib)
- **Python:** 3.14

### Frontend
- **Pure HTML/CSS/JavaScript** (no frameworks)
- **Modern CSS** with CSS Grid and Flexbox
- **HTTP-only Cookie Authentication**
- **Responsive Design**
- **Same-Origin Deployment** (served by FastAPI)

## Project Structure

```
backend/
├── auth/
│   ├── jwt.py              # JWT token creation and validation
│   ├── passlib_setup.py    # Password hashing setup
│   ├── shop_cookies.py     # Shop-specific token management
│   └── products_cookie.py  # Product cookie management
├── main/
│   └── main.py             # FastAPI app entry point
├── models/
│   ├── users_class.py      # User model (includes phone, address)
│   ├── shop_data.py        # Shop model
│   ├── products.py         # Product model
│   ├── cart_class.py       # Cart model (includes product snapshots)
│   ├── orders.py           # Order model
│   └── notifications.py    # Notification model
├── routes/
│   ├── signin.py           # User registration endpoint
│   ├── login.py            # User login endpoint
│   ├── logout.py           # User logout endpoint
│   ├── shop_login.py       # Shop creation endpoint
│   ├── switch_shop.py      # Switch between shops
│   ├── products.py         # Add products to shop
│   ├── product_change.py   # Update product information
│   ├── ProductStock.py     # Update product stock
│   ├── view_products.py    # View shop products
│   ├── search_products.py  # Search products
│   ├── buy_product.py      # Purchase products
│   ├── order_history.py    # Get user's order history
│   ├── order_status.py     # Get order status
│   ├── shop_orders.py      # Get shop's orders
│   ├── update_order_status.py  # Update order status (shopkeeper)
│   ├── user_order_status.py    # Update order status (customer)
│   └── product_sales.py   # Product sales analytics
├── schemas/
│   ├── signin_input.py     # User registration schema (includes phone, address)
│   ├── shop_input.py       # Shop creation schema
│   ├── product_input.py    # Product schema
│   ├── product_change_input.py  # Product update schema
│   ├── stock_update_input.py    # Stock update schema
│   ├── buy_input.py        # Purchase schema
│   ├── search_input.py     # Search schema
│   └── order_status_update.py  # Order status update schema
└── services/
    ├── database.py         # Database connection and session (PostgreSQL/SQLite)
    ├── settings.py         # Environment configuration
    └── config.py           # Config settings

front_end/
├── css/
│   └── style.css           # Main stylesheet
├── js/
│   ├── config.js           # API configuration
│   ├── utils.js            # Utility functions
│   ├── api.js              # API wrapper functions
│   ├── auth.js             # Authentication handling
│   ├── cart.js             # Shopping cart logic
│   ├── seller.js           # Seller dashboard logic
│   └── orders.js           # Order management logic
├── index.html              # Home page
├── login.html              # Login page
├── register.html           # Registration page
├── seller.html             # Seller dashboard
├── orders.html             # Customer orders page
├── product-details.html    # Product details page
├── cart.html               # Shopping cart page
└── shop.html               # Shop page
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
   pip install fastapi uvicorn sqlalchemy[asyncio] aiosqlite asyncpg passlib[bcrypt] pyjwt python-dotenv
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your database configuration:
   ```
   # For PostgreSQL (recommended for production):
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost/your_database_name

   # For SQLite (development only):
   # DATABASE_URL=sqlite+aiosqlite:///./test.db

   JWT_SECRET=your_jwt_secret_key_here
   SHOP_COOKIE_SECRET=your_shop_cookie_secret_here
   ```

5. **Create PostgreSQL database (if using PostgreSQL)**
   ```bash
   python create_db.py
   ```

6. **Run the server**
   ```bash
   uvicorn backend.main.main:app --reload
   ```

The application will be available at `http://127.0.0.1:8000` with both API and frontend served from the same origin.

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
      "created_at": "2026-10-23T13:28:51",
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

### Get Shop Orders
**GET** `/shop_orders`

Requires both user authentication (access_token cookie) and shop authentication (shop_token cookie).

Response:
```json
{
  "orders": [
    {
      "order_id": 1,
      "shop_id": 1,
      "user_email": "customer@example.com",
      "total_cost": 200,
      "status": "pending",
      "created_at": "2026-10-23T13:28:51",
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

### Update Order Status (Shopkeeper)
**PUT** `/update_order_status`

Requires both user authentication (access_token cookie) and shop authentication (shop_token cookie).

Request body:
```json
{
  "order_id": 1,
  "status": "working"
}
```

Allowed status transitions for shopkeepers:
- `pending` → `working`
- `working` → `pending`

**Note:** Shopkeepers cannot mark orders as `completed` (only customers can do that).

Response:
```json
{
  "message": "Order status updated successfully",
  "order_id": 1,
  "new_status": "working"
}
```

### Update Order Status (Customer)
**PUT** `/user_order_status`

Requires authentication (access_token cookie).

Request body:
```json
{
  "order_id": 1,
  "status": "completed"
}
```

Allowed status transitions for customers:
- `working` → `completed`

**Note:** Customers can only mark orders as completed when the shop has set status to `working`.

Response:
```json
{
  "message": "Order status updated successfully",
  "order_id": 1,
  "new_status": "completed"
}
```

### Get Product Sales Summary
**GET** `/product_sales`

Requires both user authentication (access_token cookie) and shop authentication (shop_token cookie).

Response:
```json
{
  "product_sales": [
    {
      "product_id": 1,
      "product_name": "Camera",
      "total_quantity": 50,
      "total_revenue": 5000,
      "total_orders": 25,
      "buyers": ["customer1@example.com", "customer2@example.com"]
    }
  ],
  "total_products": 1
}
```

### Get Product Sales Details
**GET** `/product_sales/{product_id}`

Requires both user authentication (access_token cookie) and shop authentication (shop_token cookie).

Response:
```json
{
  "product_id": 1,
  "sales": [
    {
      "order_id": 1,
      "customer_name": "John Doe",
      "customer_email": "john@example.com",
      "customer_phone": "1234567890",
      "customer_address": "123 Main St",
      "quantity": 2,
      "price": 100,
      "total": 200,
      "purchase_date": "2026-10-23T13:28:51",
      "order_status": "completed"
    }
  ],
  "total_sales": 1
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
- Order status management (shopkeeper and customer)
- Cross-user access control
- Cross-shop access control
- Order status sequence verification
- Stock deduction verification
- Multi-shop purchase blocking
- Concurrent stock testing
- Price snapshot verification
- Multiple shop management
- Race condition testing
- Transaction rollback testing
- Session persistence testing
- Duplicate prevention testing

**Load test results (PostgreSQL):**
- 100% success rate on all core operations
- 50+ requests per second
- Zero database locking errors
- Complete security enforcement verified

## Security

- Passwords are hashed using Bcrypt
- JWT tokens expire after 60 minutes
- Cookies are httponly to prevent XSS attacks
- `.env` file is excluded from version control
- Database files are excluded from version control

## License

This project is private and confidential.
