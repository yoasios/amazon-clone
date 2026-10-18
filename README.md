# Amazon Clone Backend

A FastAPI-based backend for an e-commerce platform with user authentication and shop management features.

## Features

- **User Authentication**
  - User registration (signin)
  - User login with JWT tokens
  - Cookie-based authentication (httponly, secure)
  - Bcrypt password hashing

- **Shop Management**
  - Shop creation for authenticated users
  - Shop-specific JWT tokens
  - Shop details retrieval on login

- **Database**
  - Async SQLAlchemy with SQLite
  - Models for Users, Shops, Products, and Cart
  - Automatic table creation on startup

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite with async support (aiosqlite)
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
│   └── shop_cookies.py     # Shop-specific token management
├── main/
│   └── main.py             # FastAPI app entry point
├── models/
│   ├── users_class.py      # User model
│   ├── shop_data.py        # Shop model
│   ├── products.py         # Product model
│   └── cart_class.py       # Cart model
├── routes/
│   ├── signin.py           # User registration endpoint
│   ├── login.py            # User login endpoint
│   ├── shop_login.py       # Shop creation endpoint
│   └── health_check.py     # Health check endpoint
├── schemas/
│   ├── signin_input.py     # User registration schema
│   ├── shop_input.py       # Shop creation schema
│   └── product_input.py    # Product schema
└── services/
    ├── database.py         # Database connection and session
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

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```
   ALGORITHM = "HS256"
   SECRET_KEY = "your-secret-key-minimum-32-characters"
   DATABASE_URL = "sqlite:///./test.db"
   scheme = "bcrypt"
   paas_for_cookies = "your-cookie-secret"
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
  "password": "yourpassword123"
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

The project includes comprehensive pytest tests for all endpoints.

**Install test dependencies:**
```bash
pip install pytest pytest-asyncio httpx
```

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test:**
```bash
pytest tests/test_main.py::test_health_check -v
```

**Test coverage includes:**
- Health check endpoint
- User registration (signin)
- User login with valid/invalid credentials
- Shop creation with authentication
- Duplicate shop prevention
- Product creation with shop token
- Duplicate product prevention
- Complete user flow (signin → shop_login → add_product)

Tests use an in-memory SQLite database and do not affect your main database.

## Security

- Passwords are hashed using Bcrypt
- JWT tokens expire after 60 minutes
- Cookies are httponly to prevent XSS attacks
- `.env` file is excluded from version control
- Database files are excluded from version control

## License

This project is private and confidential.
