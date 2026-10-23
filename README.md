# Amazon Clone - Full E-Commerce Platform

A production-ready e-commerce platform with FastAPI backend and browser frontend, featuring multi-user authentication, shop management, product inventory, order tracking, and comprehensive sales analytics.

## Author

**Username:** yoasios  
**Email:** vangoyt867@gmail.com

## Features

### Core Functionality
- **User Authentication**
  - User registration with phone and address
  - User login with JWT tokens
  - Cookie-based authentication (httponly, secure)
  - Bcrypt password hashing
  - Auto-login with valid cookies
  - Session persistence across requests

- **Shop Management**
  - Shop creation for authenticated users
  - Shop-specific JWT tokens
  - Shop switching between multiple shops
  - Ownership verification for all operations
  - Professional seller dashboard

- **Product Management**
  - Add products to shops
  - Product information updates (optional fields)
  - Atomic stock updates with ownership check
  - Product snapshot at purchase time (prevents data drift)
  - Separate stock update endpoint

- **Order Management**
  - Bulk purchases with atomic stock deduction
  - Order history per user
  - Product snapshots preserve purchase details
  - Transaction rollback on errors
  - Order status management (pending → working → completed)
  - Shopkeeper order viewing
  - Customer order completion

- **Sales Analytics**
  - Product sales tracking
  - Customer information display (name, email, phone, address)
  - Revenue tracking per product
  - Buyer count and unique buyer tracking
  - Detailed sales history per product

- **Search Functionality**
  - Search by shop ID
  - Search by product name
  - Global search across all products (max 20 results)

- **Frontend**
  - Browser-based UI served from same URL as API
  - Professional seller dashboard with tabs
  - Order status management interface
  - Sales analytics dashboard
  - Product catalog and shopping cart
  - Responsive design

### Advanced Features
- **Order Status Workflow**
  - Pending (new order)
  - Working (shop started processing)
  - Completed (customer confirmed receipt)
  - Shopkeeper can toggle pending ↔ working
  - Only customer can mark as completed

- **Data Isolation**
  - Complete user/shop isolation
  - Cross-user access control
  - Cross-shop access control
  - Ownership verification on all operations

- **Concurrency Support**
  - PostgreSQL for production concurrent writes
  - Connection pooling (pool_size=10, max_overflow=20)
  - Atomic stock operations
  - Transaction rollback on errors

## Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL (production) / SQLite (development)
- **ORM:** SQLAlchemy (async)
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** Bcrypt (passlib)
- **Async Driver:** asyncpg (PostgreSQL) / aiosqlite (SQLite)
- **Python:** 3.14

### Frontend
- **Technology:** HTML, CSS, Vanilla JavaScript
- **API Integration:** Fetch API with HTTP-only cookies
- **Styling:** Custom CSS with responsive design
- **No Frameworks:** Pure vanilla JS for maximum performance

## Project Structure

```
amazon-clone/
├── backend/
│   ├── auth/
│   │   ├── jwt.py              # JWT token creation and validation
│   │   ├── passlib_setup.py    # Password hashing setup
│   │   └── shop_cookies.py     # Shop-specific token management
│   ├── main/
│   │   └── main.py             # FastAPI app entry point
│   ├── models/
│   │   ├── users_class.py      # User model (includes phone, address)
│   │   ├── shop_data.py        # Shop model
│   │   ├── products.py         # Product model
│   │   ├── cart_class.py       # Cart model (includes product snapshots)
│   │   └── orders.py           # Order model (includes status, shop_id)
│   ├── routes/
│   │   ├── signin.py           # User registration endpoint
│   │   ├── login.py            # User login endpoint
│   │   ├── logout.py           # User logout endpoint
│   │   ├── shop_login.py       # Shop creation endpoint
│   │   ├── user_shops.py       # Get user's shops
│   │   ├── switch_shop.py      # Switch between shops
│   │   ├── products.py         # Add products to shop
│   │   ├── product_change.py   # Update product information
│   │   ├── ProductStock.py     # Update product stock
│   │   ├── view_products.py    # View shop products
│   │   ├── search_products.py  # Search products
│   │   ├── buy_product.py      # Purchase products
│   │   ├── order_history.py    # Get user's order history
│   │   ├── order_status.py     # Get individual order status
│   │   ├── shop_orders.py      # Get shop's orders
│   │   ├── update_order_status.py  # Shopkeeper updates order status
│   │   ├── user_order_status.py     # Customer confirms order completion
│   │   └── product_sales.py    # Sales analytics endpoint
│   ├── schemas/
│   │   ├── signin_input.py     # User registration schema
│   │   ├── shop_input.py       # Shop creation schema
│   │   ├── product_input.py    # Product schema
│   │   ├── product_change_input.py  # Product update schema
│   │   ├── stock_update_input.py    # Stock update schema
│   │   ├── buy_input.py        # Purchase schema
│   │   ├── search_input.py     # Search schema
│   │   └── order_status_update.py   # Order status update schema
│   └── services/
│       ├── database.py         # Database connection (PostgreSQL/SQLite)
│       ├── settings.py         # Environment configuration
│       └── config.py           # Config settings
├── front_end/
│   ├── index.html             # Product catalog
│   ├── login.html             # User login
│   ├── register.html          # User registration
│   ├── cart.html              # Shopping cart
│   ├── orders.html            # Order history
│   ├── seller.html            # Seller dashboard
│   ├── shop.html              # Shop details
│   ├── product-details.html   # Product details
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       ├── config.js          # Configuration
│       ├── utils.js           # Utility functions
│       ├── api.js             # API methods
│       ├── auth.js            # Authentication
│       ├── cart.js            # Cart functionality
│       ├── products.js        # Product catalog
│       ├── orders.js          # Order management
│       ├── shop.js            # Shop page
│       └── seller.js          # Seller dashboard
├── load_test.py               # Comprehensive load test
├── .env                       # Environment variables (excluded from git)
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Setup

### Prerequisites
- Python 3.14+
- PostgreSQL (production) or SQLite (development)
- Git

### Installation

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
   pip install fastapi uvicorn sqlalchemy[asyncio] aiosqlite asyncpg passlib[bcrypt] pyjwt python-dotenv httpx
   ```

4. **Configure environment variables**
   Create a `.env` file:
   ```env
   ALGORITHM = "HS256"
   SECRET_KEY = "your-secret-key-here"
   DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost/database_name"
   scheme = "bcrypt"
   ```

5. **Create PostgreSQL database**
   ```bash
   python create_db.py
   ```

6. **Run the server**
   ```bash
   python -m uvicorn backend.main.main:app --reload
   ```

The application will be available at `http://127.0.0.1:8000`

## Usage

### Access the Application
- **Frontend:** http://127.0.0.1:8000/
- **API Documentation:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health

### Load Testing

Run comprehensive load test with 100 bots and 20 concurrent requests:
```bash
python load_test.py
```

**Load test coverage:**
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
- Order status management
- Cross-user and cross-shop access control
- Race condition handling
- Transaction rollback verification
- Sales analytics tracking

## API Endpoints

### Authentication
- `POST /signin` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /health` - Health check

### Shop Management
- `POST /shop_login` - Create shop
- `GET /my_shops` - Get user's shops
- `POST /switch_shop/{shop_id}` - Switch active shop

### Product Management
- `POST /products` - Add product to shop
- `PUT /product_change` - Update product information
- `PUT /product_stock` - Update product stock
- `POST /view/{shop_id}` - View shop products

### Search
- `POST /search` - Global search (max 20 results)
- `POST /search/shop` - Search by shop ID
- `POST /search/name` - Search by product name

### Orders
- `POST /buy_product` - Purchase products
- `GET /my_orders` - Get user's order history
- `GET /order/{order_id}` - Get individual order details
- `GET /shop_orders` - Get shop's orders (shopkeeper)
- `PUT /update_order_status` - Update order status (shopkeeper)
- `PUT /user_order_status` - Confirm order completion (customer)

### Sales Analytics
- `GET /product_sales` - Get sales summary
- `GET /product_sales/{product_id}` - Get detailed sales for a product

## Security

- Passwords are hashed using Bcrypt
- JWT tokens expire after 60 minutes
- Cookies are httponly to prevent XSS attacks
- Complete data isolation between users and shops
- Ownership verification on all operations
- `.env` file is excluded from version control
- Database files are excluded from version control

## Performance

- PostgreSQL with connection pooling (pool_size=10, max_overflow=20)
- Tested with 100 concurrent bots achieving 50+ requests/second
- Zero errors under heavy load with PostgreSQL
- Atomic stock operations prevent overselling
- Transaction rollback ensures data consistency

## License

This project is created and maintained by **yoasios** (vangoyt867@gmail.com). All rights reserved.
