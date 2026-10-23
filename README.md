# Amazon Clone - Full Stack E-Commerce Platform

A full-stack e-commerce platform with a FastAPI backend and browser frontend, featuring multi-user authentication, shop management, product inventory, order tracking, and sales analytics.

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
  - Order status workflow (pending → working → completed)
  - Shopkeeper can view and update shop orders
  - Customer can confirm order completion

- **Sales Analytics**
  - Product sales history with customer details
  - Revenue tracking per product
  - Customer information (name, email, phone, address)
  - Order status tracking

- **Search Functionality**
  - Search by shop ID
  - Search by product name
  - Global search across all products (max 20 results)

- **Database**
  - Async SQLAlchemy with PostgreSQL support
  - Models for Users, Shops, Products, Cart, and Orders
  - Automatic table creation on startup
  - Transaction handling and rollback
  - Connection pooling for high concurrency

### Frontend (Browser)
- Professional seller dashboard with tabbed navigation
- Products management (add, update, stock)
- Orders management with status updates
- Sales analytics with customer details
- Customer order tracking
- Responsive design with modern UI
- Same-origin deployment with backend

## Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL (asyncpg)
- **ORM:** SQLAlchemy (async)
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** Bcrypt (passlib)
- **Python:** 3.14

### Frontend
- **Core:** Vanilla JavaScript (ES6+)
- **Styling:** Custom CSS with CSS Variables
- **API:** Fetch API with credentials
- **Deployment:** Served via FastAPI StaticFiles
- **State Management:** SessionStorage for UI state

## Project Structure

```
backend/
├── auth/
│   ├── jwt.py              # JWT token creation and validation
│   ├── passlib_setup.py    # Password hashing setup
│   ├── shop_cookies.py     # Shop-specific token management
│   └── products_cookie.py # Product-specific token management
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
│   ├── user_shops.py       # Get user's shops
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
│   ├── update_order_status.py # Update order status (shopkeeper)
│   ├── user_order_status.py    # Update order status (customer)
│   ├── product_sales.py    # Get product sales analytics
│   └── notifications.py    # Notification endpoints
├── schemas/
│   ├── signin_input.py     # User registration schema (includes phone, address)
│   ├── shop_input.py       # Shop creation schema
│   ├── product_input.py    # Product schema
│   ├── product_change_input.py  # Product update schema
│   ├── stock_update_input.py    # Stock update schema
│   ├── buy_input.py        # Purchase schema
│   ├── search_input.py     # Search schema
│   └── order_status_update.py # Order status update schema
└── services/
    ├── database.py         # Database connection and session (PostgreSQL)
    ├── settings.py         # Environment configuration
    └── config.py           # Config settings

front_end/
├── css/
│   └── style.css           # Main stylesheet
├── js/
│   ├── api.js              # API wrapper functions
│   ├── auth.js             # Authentication logic
│   ├── cart.js             # Shopping cart logic
│   ├── config.js           # Configuration
│   ├── orders.js           # Order history UI
│   ├── seller.js           # Seller dashboard
│   └── utils.js            # Utility functions
├── cart.html               # Shopping cart page
├── index.html              # Product listing page
├── login.html              # Login page
├── orders.html             # Order history page
├── product-details.html    # Product details page
├── register.html           # Registration page
├── seller.html             # Seller dashboard
└── shop.html               # Shop page

.env                       # Environment variables (not in git)
.gitignore                 # Git ignore rules
load_test.py               # Load testing script
README.md                  # This file
API_DOCUMENTATION.md       # Detailed API documentation
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
   pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg passlib[bcrypt] pyjwt python-dotenv
   ```

4. **Configure PostgreSQL database**
   - Create a PostgreSQL database named `amazon_clone`
   - Copy `.env.example` to `.env` (if it exists) or create `.env` with:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost/amazon_clone
   JWT_SECRET_KEY=your_secret_key_here
   ```
   - Update the database URL with your PostgreSQL credentials

5. **Run the server**
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
