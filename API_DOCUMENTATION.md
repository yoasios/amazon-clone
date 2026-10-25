# Amazon Clone API Documentation

Complete API reference for all endpoints including request/response formats, authentication requirements, and detailed explanations.

---

## Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
   - POST /signin
   - POST /login
   - POST /logout
2. [Shop Management Endpoints](#shop-management-endpoints)
   - POST /shop_login
   - GET /my_shops
   - POST /switch_shop/{shop_id}
3. [Product Management Endpoints](#product-management-endpoints)
   - POST /products
   - PUT /product_change
   - PUT /product_stock
   - POST /view/{shop_id}
4. [Search Endpoints](#search-endpoints)
   - POST /search
5. [Purchase Endpoints](#purchase-endpoints)
   - POST /buy_product
6. [Order Endpoints](#order-endpoints)
   - GET /my_orders
   - GET /order/{order_id}
   - GET /shop_orders
   - PUT /update_order_status
   - PUT /user_order_status
7. [Sales Analytics Endpoints](#sales-analytics-endpoints)
   - GET /product_sales
   - GET /product_sales/{product_id}
8. [Health Check](#health-check)
   - GET /health

---

## Authentication Endpoints

### POST /signin

**Description:** Registers a new user account with the system. The user provides their personal information including name, email, password, phone number, and address. The password is hashed using bcrypt before storage. Upon successful registration, a JWT access token is generated and stored in an HTTP-only cookie for authentication.

**Authentication:** Not required (this is the registration endpoint)

**Request Body (JSON):**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securePassword123",
  "phone": "1234567890",
  "address": "123 Main Street, New York, NY 10001"
}
```

**Field Descriptions:**
- `name` (string, required): Full name of the user
- `email` (string, required): Email address - must be unique across all users
- `password` (string, required): User's password - will be hashed with bcrypt
- `phone` (string, required): Contact phone number (10 digits recommended)
- `address` (string, required): Physical address for shipping/delivery

**Success Response (200 OK):**
```json
{
  "message": "User created successfully"
}
```

**Error Responses:**
- **400 Bad Request:** If user with this email already exists
  ```json
  {
    "detail": "User already exists pls login"
  }
  ```
- **500 Internal Server Error:** If database operation fails
  ```json
  {
    "detail": "Failed to create user"
  }
  ```

**Cookies Set:**
- `access_token` (HTTP-only): JWT token containing user ID and email, expires in 60 minutes

**Notes:**
- Password is automatically truncated to first 72 characters before hashing (bcrypt limitation)
- The access token cookie is HTTP-only to prevent XSS attacks
- User can immediately use the API after registration without needing to login separately

---

### POST /login

**Description:** Authenticates an existing user and returns their session information. If the user already has a valid access token cookie, the endpoint returns their data directly (auto-login). Otherwise, it validates the email and password credentials. The response includes the user's shops and shop count for convenience.

**Authentication:** Optional - If valid cookie exists, uses it; otherwise validates credentials

**Request Body (JSON):**
```json
{
  "email": "john.doe@example.com",
  "password": "securePassword123"
}
```

**Field Descriptions:**
- `email` (string, required): Email address of the user
- `password` (string, required): User's password for verification

**Success Response - Auto-login with Valid Cookie (200 OK):**
```json
{
  "message": "Already logged in",
  "user_id": 1,
  "email": "john.doe@example.com",
  "shops": [
    {
      "shop_id": 5,
      "shop_name": "Tech Store",
      "shop_description": "Electronics and gadgets",
      "shop_address": "456 Tech Avenue, San Francisco, CA 94102",
      "shop_phone": "9876543210",
      "shop_email": "techstore@example.com"
    }
  ],
  "shop_count": 1
}
```

**Success Response - Normal Login (200 OK):**
```json
{
  "message": "Logged in successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "shops": [
    {
      "shop_id": 5,
      "shop_name": "Tech Store",
      "shop_description": "Electronics and gadgets",
      "shop_address": "456 Tech Avenue, San Francisco, CA 94102",
      "shop_phone": "9876543210",
      "shop_email": "techstore@example.com"
    }
  ],
  "shop_count": 1
}
```

**Field Descriptions:**
- `message` (string): Status message indicating login state
- `user_id` (integer): Unique identifier of the user (only in auto-login response)
- `email` (string): User's email address (only in auto-login response)
- `token` (string): JWT access token (only in normal login response)
- `shops` (array): List of shops owned by the user
  - `shop_id` (integer): Unique shop identifier
  - `shop_name` (string): Name of the shop
  - `shop_description` (string): Description of the shop
  - `shop_address` (string): Physical address of the shop
  - `shop_phone` (string): Contact phone number of the shop
  - `shop_email` (string): Contact email of the shop
- `shop_count` (integer): Total number of shops owned by the user

**Error Responses:**
- **400 Bad Request:** If user not found
  ```json
  {
    "detail": "User not found"
  }
  ```
- **400 Bad Request:** If password is incorrect
  ```json
  {
    "detail": "Invalid password"
  }
  ```

**Cookies Set:**
- `access_token` (HTTP-only): JWT token containing user ID and email, expires in 60 minutes (only set on normal login)

**Notes:**
- Auto-login feature checks for valid cookie first, skipping credential validation if possible
- Password is automatically truncated to first 72 characters before verification
- The response includes all shops owned by the user to avoid additional API calls
- Token expires after 60 minutes - user must login again after expiration

---

## Shop Management Endpoints

### POST /shop_login

**Description:** Creates a new shop for the authenticated user. The user must provide shop details including name, description, address, phone, and email. The system prevents duplicate shops with the same name, email, or phone number for the same user. Upon successful creation, a shop-specific JWT token is generated and stored in an HTTP-only cookie for shop operations.

**Authentication:** Required (access_token cookie from user login)

**Request Body (JSON):**
```json
{
  "shop_name": "Electronics Emporium",
  "shop_description": "Premium electronics and gadgets store",
  "shop_address": "789 Commerce Street, Los Angeles, CA 90001",
  "shop_phone": "5551234567",
  "shop_email": "electronics@emporium.com"
}
```

**Field Descriptions:**
- `shop_name` (string, required): Name of the shop - must be unique per user
- `shop_description` (string, required): Description of what the shop sells
- `shop_address` (string, required): Physical location of the shop
- `shop_phone` (string, required): Contact phone number - must be unique per user
- `shop_email` (string, required): Contact email - must be unique per user

**Success Response (200 OK):**
```json
{
  "message": "Shop created successfully",
  "shop_id": 42
}
```

**Field Descriptions:**
- `message` (string): Confirmation message
- `shop_id` (integer): Unique identifier of the newly created shop

**Error Responses:**
- **400 Bad Request:** If user already has a shop with the same name, email, or phone
  ```json
  {
    "detail": "You already have a shop with this name, email, or phone number"
  }
  ```
- **500 Internal Server Error:** If database operation fails
  ```json
  {
    "detail": "Failed to create shop"
  }
  ```

**Cookies Set:**
- `shop_token` (HTTP-only): JWT token containing shop ID and user ID, used for shop-specific operations

**Notes:**
- The duplicate check is scoped to the current user only (different users can have shops with the same name)
- Shop token is separate from user token - user can have multiple shops and switch between them
- Shop token is required for adding products to the shop
- Transaction rollback ensures no partial shop creation on error

---

### GET /my_shops

**Description:** Retrieves all shops owned by the currently authenticated user. This endpoint returns a complete list of shops with their details including shop ID, name, description, address, phone, and email. Useful for displaying a user's shops in a dashboard or for shop selection.

**Authentication:** Required (access_token cookie from user login)

**Request Parameters:** None (body not required)

**Success Response (200 OK):**
```json
{
  "shops": [
    {
      "shop_id": 5,
      "shop_name": "Tech Store",
      "shop_description": "Electronics and gadgets",
      "shop_address": "456 Tech Avenue, San Francisco, CA 94102",
      "shop_phone": "9876543210",
      "shop_email": "techstore@example.com"
    },
    {
      "shop_id": 12,
      "shop_name": "Home Goods",
      "shop_description": "Household items and furniture",
      "shop_address": "123 Home Lane, Seattle, WA 98101",
      "shop_phone": "5559876543",
      "shop_email": "homegoods@example.com"
    }
  ],
  "count": 2
}
```

**Field Descriptions:**
- `shops` (array): List of shops owned by the user
  - `shop_id` (integer): Unique shop identifier
  - `shop_name` (string): Name of the shop
  - `shop_description` (string): Description of the shop
  - `shop_address` (string): Physical address of the shop
  - `shop_phone` (string): Contact phone number of the shop
  - `shop_email` (string): Contact email of the shop
- `count` (integer): Total number of shops owned by the user

**Success Response - No Shops (200 OK):**
```json
{
  "shops": [],
  "count": 0
}
```

**Error Responses:** None (if authenticated, always returns 200 even with empty list)

**Notes:**
- Only returns shops owned by the authenticated user (no access to other users' shops)
- Useful for building shop selection UI
- Count field eliminates need to manually count array length on client side

---

### POST /switch_shop/{shop_id}

**Description:** Switches the active shop for the authenticated user. The user must provide the shop ID as a URL path parameter. The system verifies that the shop belongs to the user before allowing the switch. Upon successful verification, a new shop-specific JWT token is generated and stored in an HTTP-only cookie. This allows users with multiple shops to manage different shops without logging out.

**Authentication:** Required (access_token cookie from user login)

**URL Parameters:**
- `shop_id` (integer, required, path parameter): The ID of the shop to switch to

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "message": "Switched to shop successfully",
  "shop_id": 12,
  "shop_name": "Home Goods"
}
```

**Field Descriptions:**
- `message` (string): Confirmation message
- `shop_id` (integer): ID of the shop that was switched to
- `shop_name` (string): Name of the shop that was switched to

**Error Responses:**
- **403 Forbidden:** If shop does not belong to the user (generic error message for security)
  ```json
  {
    "detail": "Access denied"
  }
  ```

**Cookies Set:**
- `shop_token` (HTTP-only): New JWT token containing the switched shop's ID and user ID

**Notes:**
- Generic error message ("Access denied") is used instead of revealing whether the shop exists or not (security best practice)
- Replaces any existing shop_token cookie with the new one
- Essential for users who own multiple shops - they must switch to the correct shop before adding products
- Ownership verification prevents users from accessing shops they don't own

---

## Product Management Endpoints

### POST /products

**Description:** Adds a new product to the currently active shop. The user must be authenticated and have a valid shop token (indicating which shop they're managing). The system checks if a product with the same name already exists in the shop to prevent duplicates. The product is created with the provided details including name, price, description, and stock amount.

**Authentication:** Required (shop_token cookie from shop creation or switch)

**Request Body (JSON):**
```json
{
  "product_name": "Wireless Bluetooth Headphones",
  "product_price": 7999,
  "product_description": "High-quality wireless headphones with noise cancellation, 30-hour battery life, and premium sound quality.",
  "amount": 50
}
```

**Field Descriptions:**
- `product_name` (string, required): Name of the product - must be unique within the shop
- `product_price` (integer, required): Price of the product in cents (e.g., 7999 = $79.99)
- `product_description` (string, required): Detailed description of the product
- `amount` (integer, required): Initial stock quantity available (defaults to 0 if not provided)

**Success Response (200 OK):**
```json
{
  "message": "Product added successfully",
  "product_id": 123
}
```

**Field Descriptions:**
- `message` (string): Confirmation message
- `product_id` (integer): Unique identifier of the newly created product

**Error Responses:**
- **400 Bad Request:** If product with same name already exists in the shop
  ```json
  {
    "detail": "Product with this name already exists in your shop"
  }
  ```
- **500 Internal Server Error:** If database operation fails
  ```json
  {
    "detail": "Failed to add product"
  }
  ```

**Notes:**
- Price is stored in cents to avoid floating-point precision issues (e.g., $79.99 = 7999 cents)
- Duplicate check is scoped to the current shop only (different shops can have products with the same name)
- Shop token must be valid and correspond to a shop owned by the authenticated user
- Transaction rollback ensures no partial product creation on error
- Product ID is auto-generated by the database

---

### PUT /product_change

**Description:** Updates specific fields of an existing product. The user must be authenticated and the product must belong to a shop owned by the user. This endpoint supports partial updates - only the fields provided in the request are updated, other fields remain unchanged. All fields are optional except for product_id. The system verifies ownership before allowing updates to prevent unauthorized modifications.

**Authentication:** Required (access_token cookie from user login)

**Request Body (JSON):**
```json
{
  "product_id": 123,
  "product_name": "Premium Wireless Headphones",
  "product_price": 8999,
  "product_description": "Upgraded version with improved noise cancellation and 40-hour battery life.",
  "amount": 45
}
```

**Field Descriptions:**
- `product_id` (integer, required): ID of the product to update
- `product_name` (string, optional): New name of the product
- `product_price` (integer, optional): New price in cents
- `product_description` (string, optional): New description of the product
- `amount` (integer, optional): New stock quantity

**Success Response (200 OK):**
```json
{
  "message": "Product updated successfully",
  "product_id": 123,
  "updated_fields": ["product_name", "product_price", "product_description", "amount"]
}
```

**Field Descriptions:**
- `message` (string): Confirmation message
- `product_id` (integer): ID of the updated product
- `updated_fields` (array): List of field names that were actually updated

**Error Responses:**
- **400 Bad Request:** If no fields provided to update
  ```json
  {
    "detail": "No fields provided to update"
  }
  ```
- **404 Not Found:** If product does not exist
  ```json
  {
    "detail": "Product not found"
  }
  ```
- **403 Forbidden:** If product belongs to a shop the user doesn't own
  ```json
  {
    "detail": "You do not own this product"
  }
  ```
- **500 Internal Server Error:** If database operation fails
  ```json
  {
    "detail": "Internal server error: [error details]"
  }
  ```

**Notes:**
- All fields except product_id are optional - include only fields you want to change
- Ownership verification checks that the product's shop belongs to the authenticated user
- Transaction rollback ensures no partial updates on error
- The updated_fields response tells client exactly what changed
- Useful for price changes, stock updates, or description updates without affecting other fields

---

### PUT /product_stock

**Description:** Updates the stock amount of an existing product. This is a specialized endpoint for stock management that uses atomic database operations to prevent race conditions with concurrent purchases. The user must be authenticated and the product must belong to a shop owned by the user. The unit field is currently ignored (included for future use).

**Authentication:** Required (access_token cookie from user login)

**Request Body (JSON):**
```json
{
  "product_id": 123,
  "amount": 100,
  "unit": "pieces"
}
```

**Field Descriptions:**
- `product_id` (integer, required): ID of the product to update
- `amount` (integer, required): New absolute stock quantity (sets to this value, not increments)
- `unit` (string, optional): Unit of measurement (currently ignored, reserved for future use)

**Success Response (200 OK):**
```json
{
  "message": "Product stock updated successfully",
  "product_id": 123,
  "new_amount": 100
}
```

**Field Descriptions:**
- `message` (string): Confirmation message
- `product_id` (integer): ID of the updated product
- `new_amount` (integer): The updated stock quantity after the change

**Error Responses:**
- **404 Not Found:** If product does not exist
  ```json
  {
    "detail": "Product not found"
  }
  ```
- **403 Forbidden:** If product belongs to a shop the user doesn't own
  ```json
  {
    "detail": "You do not own this product"
  }
  ```
- **500 Internal Server Error:** If database operation fails
  ```json
  {
    "detail": "Internal server error: [error details]"
  }
  ```

**Notes:**
- Uses atomic SQL UPDATE to prevent race conditions with concurrent purchases
- Sets absolute amount (e.g., setting to 100 means stock becomes 100, not increases by 100)
- Ownership verification ensures only shop owners can update stock
- Transaction rollback ensures no partial updates on error
- Unit field is reserved for future implementation (currently ignored)
- This endpoint is safer than product_change for stock updates because it uses atomic operations

---

### POST /view/{shop_id}

**Description:** Retrieves all products from a specific shop. The user must be authenticated but does not need to own the shop - this allows customers to browse products from any shop. The response returns the complete list of products with all their details.

**Authentication:** Required (access_token cookie from user login)

**URL Parameters:**
- `shop_id` (integer, required, path parameter): The ID of the shop to view products from

**Request Body:** None

**Success Response (200 OK):**
```json
[
  {
    "product_id": 123,
    "product_name": "Wireless Bluetooth Headphones",
    "product_price": 7999,
    "product_description": "High-quality wireless headphones with noise cancellation.",
    "amount": 50,
    "shop_id": 5,
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "product_id": 124,
    "product_name": "USB-C Charging Cable",
    "product_price": 1999,
    "product_description": "Fast charging cable for all USB-C devices.",
    "amount": 200,
    "shop_id": 5,
    "created_at": "2024-01-15T11:00:00"
  }
]
```

**Field Descriptions:**
- `product_id` (integer): Unique product identifier
- `product_name` (string): Name of the product
- `product_price` (integer): Price in cents
- `product_description` (string): Product description
- `amount` (integer): Current stock quantity
- `shop_id` (integer): ID of the shop that owns the product
- `created_at` (datetime): Timestamp when product was created

**Success Response - No Products (200 OK):**
```json
[]
```

**Error Responses:** None (if authenticated, always returns 200 even with empty list)

**Notes:**
- Returns raw product objects (not wrapped in a response object)
- Allows browsing any shop's products, not just owned shops
- Useful for product catalog display
- Authentication is still required to prevent unauthorized access
- Includes all product fields for complete information

---

## Search Endpoints

### POST /search

**Description:** Performs a global search across all products in all shops. The search matches products by name or description using case-insensitive pattern matching. Results are limited to 20 products per request to prevent excessive database load and pagination is supported via the offset parameter. Each result includes both product and shop information for complete context.

**Authentication:** Required (access_token cookie from user login)

**Request Body (JSON):**
```json
{
  "query": "wireless",
  "offset": 0
}
```

**Field Descriptions:**
- `query` (string, required): Search term to match against product names and descriptions
- `offset` (integer, optional): Number of results to skip for pagination (defaults to 0)

**Success Response (200 OK):**
```json
{
  "results": [
    {
      "product_id": 123,
      "product_name": "Wireless Bluetooth Headphones",
      "product_price": 7999,
      "product_description": "High-quality wireless headphones with noise cancellation.",
      "amount": 50,
      "shop": {
        "shop_id": 5,
        "shop_name": "Tech Store",
        "shop_description": "Electronics and gadgets",
        "shop_address": "456 Tech Avenue, San Francisco, CA 94102",
        "shop_phone": "9876543210",
        "shop_email": "techstore@example.com"
      }
    },
    {
      "product_id": 156,
      "product_name": "Wireless Mouse",
      "product_price": 2999,
      "product_description": "Ergonomic wireless mouse with precision tracking.",
      "amount": 75,
      "shop": {
        "shop_id": 12,
        "shop_name": "Computer Accessories",
        "shop_description": "All computer peripherals",
        "shop_address": "789 Tech Boulevard, Austin, TX 78701",
        "shop_phone": "5555551234",
        "shop_email": "accessories@example.com"
      }
    }
  ],
  "count": 2,
  "limit": 20,
  "offset": 0
}
```

**Field Descriptions:**
- `results` (array): List of matching products with shop information
  - `product_id` (integer): Unique product identifier
  - `product_name` (string): Name of the product
  - `product_price` (integer): Price in cents
  - `product_description` (string): Product description
  - `amount` (integer): Current stock quantity
  - `shop` (object): Shop information
    - `shop_id` (integer): Shop ID
    - `shop_name` (string): Shop name
    - `shop_description` (string): Shop description
    - `shop_address` (string): Shop address
    - `shop_phone` (string): Shop phone
    - `shop_email` (string): Shop email
- `count` (integer): Number of results returned in this batch
- `limit` (integer): Maximum results per batch (fixed at 20)
- `offset` (integer): Current offset used for pagination

**Success Response - No Results (200 OK):**
```json
{
  "results": [],
  "count": 0,
  "limit": 20,
  "offset": 0
}
```

**Error Responses:** None (if authenticated, always returns 200 even with empty results)

**Notes:**
- Search is case-insensitive (e.g., "wireless" matches "Wireless" and "WIRELESS")
- Matches against both product name and description
- Hard limit of 20 results per request prevents performance issues
- Use offset for pagination: offset=0 for first page, offset=20 for second page, etc.
- Includes shop information so users know which shop sells each product
- Authentication required to prevent unauthorized data access

---

## Purchase Endpoints

### POST /buy_product

**Description:** Processes a bulk purchase of multiple products. This endpoint uses atomic database operations to ensure stock deduction is safe under concurrent load. For each product, it checks if sufficient stock exists and deducts the requested quantity in a single atomic operation. If any product has insufficient stock or doesn't exist, the entire transaction is rolled back. Upon successful purchase, an order is created with order items that include product snapshots (name, price, description at time of purchase) to preserve purchase details even if the product is later modified by the shopkeeper.

**Authentication:** Required (access_token cookie from user login)

**Request Body (JSON):**
```json
{
  "items": [
    {
      "product_id": 123,
      "quantity": 2
    },
    {
      "product_id": 124,
      "quantity": 1
    }
  ]
}
```

**Field Descriptions:**
- `items` (array, required): List of products to purchase
  - `product_id` (integer, required): ID of the product to purchase
  - `quantity` (integer, optional): Quantity to purchase (defaults to 1 if not specified)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Purchase successful",
  "order_id": 789,
  "total_cost": 17997,
  "items_purchased": 2,
  "items": [
    {
      "product_id": 123,
      "product_name": "Wireless Bluetooth Headphones",
      "product_description": "High-quality wireless headphones with noise cancellation.",
      "quantity": 2,
      "price": 7999,
      "total": 15998
    },
    {
      "product_id": 124,
      "product_name": "USB-C Charging Cable",
      "product_description": "Fast charging cable for all USB-C devices.",
      "quantity": 1,
      "price": 1999,
      "total": 1999
    }
  ]
}
```

**Field Descriptions:**
- `success` (boolean): Indicates purchase was successful
- `message` (string): Confirmation message
- `order_id` (integer): Unique identifier of the created order
- `total_cost` (integer): Total cost in cents (sum of all item totals)
- `items_purchased` (integer): Number of different products purchased
- `items` (array): Details of purchased items
  - `product_id` (integer): Product ID
  - `product_name` (string): Product name at time of purchase (snapshot)
  - `product_description` (string): Product description at time of purchase (snapshot)
  - `quantity` (integer): Quantity purchased
  - `price` (integer): Price per unit in cents at time of purchase (snapshot)
  - `total` (integer): Total cost for this item (quantity × price)

**Error Responses:**
- **400 Bad Request:** If no items in cart
  ```json
  {
    "detail": "No items in cart"
  }
  ```
- **404 Not Found:** If a product doesn't exist
  ```json
  {
    "detail": "Product 123 not found"
  }
  ```
- **400 Bad Request:** If insufficient stock for a product
  ```json
  {
    "detail": "Not enough stock for product Wireless Bluetooth Headphones. Available: 45, Requested: 50"
  }
  ```
- **500 Internal Server Error:** If database operation fails
  ```json
  {
    "detail": "Purchase failed: [error details]"
  }
  ```

**Notes:**
- Atomic stock deduction prevents overselling under concurrent load
- Transaction rollback ensures all-or-nothing purchase (if one item fails, entire purchase fails)
- Product snapshots preserve purchase details even if product is later modified
- Stock is checked and deducted in a single SQL operation for concurrency safety
- Order and cart items are created after all stock validations pass
- Product snapshots include name, price, and description at time of purchase
- This solves the data drift problem: customers see what they paid for, not current product state
- Total cost is calculated based on prices at time of purchase (snapshot prices)

---

## Order Endpoints

### GET /my_orders

**Description:** Retrieves the complete order history for the authenticated user. Orders are returned in reverse chronological order (newest first). Each order includes its status, total cost, creation timestamp, and all items with their details. This endpoint allows users to view their past purchases and track order status.

**Authentication:** Required (access_token cookie from user login)

**Request Parameters:** None (body not required)

**Success Response (200 OK):**
```json
{
  "orders": [
    {
      "order_id": 789,
      "status": "completed",
      "total_cost": 17997,
      "created_at": "2024-01-20T14:30:00",
      "items": [
        {
          "product_id": 123,
          "product_name": "Wireless Bluetooth Headphones",
          "quantity": 2,
          "price": 7999,
          "total": 15998
        },
        {
          "product_id": 124,
          "product_name": "USB-C Charging Cable",
          "quantity": 1,
          "price": 1999,
          "total": 1999
        }
      ],
      "item_count": 2
    },
    {
      "order_id": 756,
      "status": "completed",
      "total_cost": 4999,
      "created_at": "2024-01-18T09:15:00",
      "items": [
        {
          "product_id": 145,
          "product_name": "Wireless Mouse",
          "quantity": 1,
          "price": 4999,
          "total": 4999
        }
      ],
      "item_count": 1
    }
  ],
  "total_orders": 2
}
```

**Field Descriptions:**
- `orders` (array): List of orders for the user
  - `order_id` (integer): Unique order identifier
  - `status` (string): Current status of the order (e.g., "completed", "pending")
  - `total_cost` (integer): Total cost in cents
  - `created_at` (datetime): Timestamp when order was created
  - `items` (array): Items in the order
    - `product_id` (integer): Product ID
    - `product_name` (string): Product name (from current product table, not snapshot)
    - `quantity` (integer): Quantity purchased
    - `price` (integer): Price per unit in cents (from current product table, not snapshot)
    - `total` (integer): Total cost for this item
  - `item_count` (integer): Number of items in this order
- `total_orders` (integer): Total number of orders for the user

**Success Response - No Orders (200 OK):**
```json
{
  "orders": [],
  "total_orders": 0,
  "message": "No orders found"
}
```

**Error Responses:** None (if authenticated, always returns 200 even with empty list)

**Notes:**
- Orders are sorted by creation date in descending order (newest first)
- Only returns orders for the authenticated user (no access to other users' orders)
- Product details in items are from the current product table (may differ from purchase-time snapshots)
- For purchase-time details, the cart table contains product_name_snapshot, product_price_snapshot, and product_description_snapshot fields
- Status field can be extended to support order tracking (pending, shipped, delivered, etc.)

---

### GET /order/{order_id}

**Description:** Retrieves detailed information about a specific order. The user must be authenticated and the order must belong to the user. This endpoint is useful for checking the status of a specific order or verifying purchase details if the user didn't receive a response during the purchase process.

**Authentication:** Required (access_token cookie from user login)

**URL Parameters:**
- `order_id` (integer, required, path parameter): The ID of the order to retrieve

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "order_id": 789,
  "status": "completed",
  "total_cost": 17997,
  "created_at": "2024-01-20T14:30:00",
  "items": [
    {
      "product_id": 123,
      "product_name": "Wireless Bluetooth Headphones",
      "quantity": 2,
      "price": 7999,
      "total": 15998
    },
    {
      "product_id": 124,
      "product_name": "USB-C Charging Cable",
      "quantity": 1,
      "price": 1999,
      "total": 1999
    }
  ],
  "item_count": 2
}
```

**Field Descriptions:**
- `order_id` (integer): Unique order identifier
- `status` (string): Current status of the order
- `total_cost` (integer): Total cost in cents
- `created_at` (datetime): Timestamp when order was created
- `items` (array): Items in the order
  - `product_id` (integer): Product ID
  - `product_name` (string): Product name (from current product table)
  - `quantity` (integer): Quantity purchased
  - `price` (integer): Price per unit in cents (from current product table)
  - `total` (integer): Total cost for this item
- `item_count` (integer): Number of items in this order

**Error Responses:**
- **404 Not Found:** If order doesn't exist or doesn't belong to the user
  ```json
  {
    "detail": "Order not found"
  }
  ```

**Notes:**
- Verifies ownership - users can only access their own orders
- Generic "Order not found" error doesn't reveal if order exists or belongs to another user (security)
- Useful for order tracking and verification
- Can be used to check order status after purchase if initial response was lost
- Product details are from current product table (may differ from purchase-time snapshots)

---

## Health Check

### GET /health

**Description:** Simple health check endpoint to verify the API server is running and responding. Returns a basic status message. Useful for monitoring, load balancer health checks, and deployment verification.

**Authentication:** Not required

**Request Parameters:** None

**Success Response (200 OK):**
```json
{
  "status": "healthy"
}
```

**Field Descriptions:**
- `status` (string): Health status of the API server

**Error Responses:** None (always returns 200 if server is running)

**Notes:**
- No authentication required
- Can be used by monitoring systems
- Fast and lightweight (no database queries)
- Useful for deployment verification and load balancer health checks

---

## Authentication Details

### User Authentication (access_token)

- **Token Type:** JWT (JSON Web Token)
- **Cookie Name:** `access_token`
- **Cookie Type:** HTTP-only (not accessible via JavaScript)
- **Secure:** `false` (can be transmitted over HTTP - set to `true` in production with HTTPS)
- **SameSite:** `lax` (allows cookies with top-level navigations, prevents CSRF on cross-site requests)
- **Expiration:** 60 minutes from creation
- **Payload Structure:**
  ```json
  {
    "sub": "{\"id\": 1, \"email\": \"user@example.com\"}",
    "exp": 1705567200
  }
  ```
  - `sub` (string): JSON string containing user data
    - `id` (integer): User's unique identifier
    - `email` (string): User's email address
  - `exp` (integer): Unix timestamp when token expires
- **Used For:** User-level operations (login, purchase, order history, shop creation, product updates, shop switching)
- **Set By Endpoints:**
  - POST /signin (after successful registration)
  - POST /login (after successful authentication)
- **Cleared By:** None (must wait for expiration or manually clear browser cookies)
- **Error Handling:**
  - Expired token: Returns `None` from `get_current_user`, user must login again
  - Invalid token: Returns `None` from `get_current_user`, user must login again
  - Missing token: Returns `None` from `get_current_user`, endpoint may require authentication

### Shop Authentication (shop_access_token)

- **Token Type:** JWT (JSON Web Token)
- **Cookie Name:** `shop_access_token`
- **Cookie Type:** HTTP-only (not accessible via JavaScript)
- **Secure:** `false` (can be transmitted over HTTP - set to `true` in production with HTTPS)
- **SameSite:** `lax` (allows cookies with top-level navigations, prevents CSRF on cross-site requests)
- **Expiration:** 60 minutes from creation
- **Payload Structure:**
  ```json
  {
    "sub": "{\"shop_id\": 5, \"user_id\": 1}",
    "exp": 1705567200
  }
  ```
  - `sub` (string): JSON string containing shop data
    - `shop_id` (integer): Shop's unique identifier
    - `user_id` (integer): User's unique identifier (owner of the shop)
  - `exp` (integer): Unix timestamp when token expires
- **Used For:** Shop-level operations (add products, view shop products)
- **Required:** User must switch to a shop before performing shop operations
- **Set By Endpoints:**
  - POST /shop_login (after successful shop creation)
  - POST /switch_shop/{shop_id} (after successful shop switch)
- **Cleared By:** None (must wait for expiration or manually clear browser cookies)
- **Error Handling:**
  - Expired token: Returns HTTP 401 with detail "Shop token expired"
  - Invalid token: Returns HTTP 401 with detail "Invalid shop token"
  - Missing token: Returns HTTP 401 with detail "No shop cookie found"

### Cookie Security Attributes

#### HTTP-Only
- Both cookies are HTTP-only, meaning they cannot be accessed via JavaScript
- Prevents Cross-Site Scripting (XSS) attacks from stealing authentication tokens
- Cookies are only sent to the server with HTTP requests

#### Secure Flag
- Currently set to `false` to allow HTTP connections (development mode)
- In production with HTTPS, this should be set to `true` to ensure cookies are only transmitted over encrypted connections
- Without HTTPS and secure=true, cookies won't be sent

#### SameSite Attribute
- Set to `lax` for both cookies
- `lax` mode allows cookies to be sent with top-level navigations (e.g., clicking a link)
- Prevents Cross-Site Request Forgery (CSRF) attacks on cross-site requests
- Other options:
  - `strict`: Cookies never sent on cross-site requests (may break legitimate cross-site navigation)
  - `none`: Cookies sent on all requests (requires secure flag, less secure)

### Token Refresh

- Tokens expire after 60 minutes from creation
- No automatic token refresh mechanism implemented
- User must login again after token expiration
- Auto-login feature in POST /login checks for valid cookie but doesn't extend expiration
- Future enhancement: Implement refresh token mechanism for seamless token renewal

### Cookie Management for Developers

#### Setting Cookies
```python
# User token
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=False,
    samesite="lax"
)

# Shop token
response.set_cookie(
    key="shop_access_token",
    value=token,
    httponly=True,
    secure=False,
    samesite="lax"
)
```

#### Reading Cookies
```python
# User token (from dependency)
current_user = Depends(get_current_user)
# Returns: {"id": 1, "email": "user@example.com"} or None

# Shop token (from dependency)
current_shop = Depends(get_current_shop)
# Returns: (shop_id, user_id) tuple or raises HTTPException
```

#### Clearing Cookies
```python
# To clear a cookie, set it with empty value and max_age=0
response.delete_cookie("access_token")
response.delete_cookie("shop_access_token")
```

### Cookie Expiration Behavior

- **Expiration Time:** 60 minutes from token creation (not from last activity)
- **After Expiration:**
  - User token: `get_current_user` returns `None`, endpoints requiring authentication will fail
  - Shop token: `get_current_shop` raises HTTP 401, shop operations will fail
- **No Sliding Expiration:** Token does not extend expiration on each request
- **No Session Refresh:** Activity doesn't extend token lifetime
- **Recommended:** Implement session refresh mechanism for better UX

### Multi-Shop Cookie Management

- User can own multiple shops but only one active shop at a time
- `shop_access_token` cookie represents the currently active shop
- Switching shops updates the `shop_access_token` cookie with new shop_id
- `access_token` cookie remains unchanged (represents user identity)
- Flow:
  1. User logs in → `access_token` set
  2. User creates shop → `shop_access_token` set for new shop
  3. User switches to different shop → `shop_access_token` updated to new shop
  4. Both cookies remain valid until expiration

### Cookie Security Best Practices

1. **Production Deployment:**
   - Set `secure=True` for both cookies when using HTTPS
   - Consider using `SameSite=strict` for enhanced CSRF protection
   - Use environment variables to configure cookie settings

2. **Token Storage:**
   - Never store tokens in localStorage or sessionStorage (vulnerable to XSS)
   - HTTP-only cookies are the most secure storage method
   - Consider implementing refresh tokens for better UX

3. **Token Validation:**
   - Always validate token expiration on server side
   - Verify token signature with secret key
   - Check token payload structure matches expected format

4. **Error Messages:**
   - Use generic error messages for authentication failures
   - Don't reveal whether user exists or password is incorrect (prevents user enumeration)
   - Log detailed errors server-side for debugging

### Cookie Testing

#### Testing with httpx (Load Test)
```python
# Store cookies in client
client = httpx.AsyncClient()
response = await client.post("http://localhost:8000/signin", json={...})
# Cookies are automatically stored in client.cookie_jar

# Subsequent requests use stored cookies
response = await client.post("http://localhost:8000/products", json={...})
```

#### Testing with Browser
1. Open browser DevTools (F12)
2. Go to Application → Cookies
3. View `access_token` and `shop_access_token` cookies
4. Manually clear cookies to test expiration behavior

### Cookie Troubleshooting

#### Common Issues

1. **Cookie Not Being Set:**
   - Check browser settings (cookies may be blocked)
   - Verify domain and path attributes
   - Check SameSite policy for cross-domain requests

2. **Cookie Expired Too Soon:**
   - Verify system time is correct
   - Check if token creation time is correct
   - Ensure expiration calculation is accurate

3. **Cookie Not Being Sent:**
   - Verify SameSite policy allows the request
   - Check if secure flag matches protocol (HTTP vs HTTPS)
   - Ensure domain matches the request domain

4. **Multiple Shop Issues:**
   - Verify `shop_access_token` is updated on shop switch
   - Check that old shop token is cleared
   - Ensure only one shop is active at a time

---

## Error Handling

### Common HTTP Status Codes

- **200 OK:** Request successful
- **400 Bad Request:** Invalid input or business logic violation
- **403 Forbidden:** Authentication valid but unauthorized for this resource
- **404 Not Found:** Resource doesn't exist
- **500 Internal Server Error:** Unexpected server error

### Error Response Format

All errors follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Transaction Rollback

- All write operations (create, update, delete) use transaction rollback on error
- Ensures no partial data changes on failure
- Maintains data integrity

---

## Security Notes

1. **Password Security:** Passwords are hashed using bcrypt before storage
2. **Cookie Security:** All authentication cookies are HTTP-only to prevent XSS attacks
3. **Ownership Verification:** All operations verify user owns the resource before allowing access
4. **Generic Error Messages:** Ownership errors use generic messages to prevent information leakage
5. **Atomic Operations:** Stock updates use atomic SQL operations to prevent race conditions
6. **Product Snapshots:** Purchase details are preserved at time of purchase to prevent data drift

---

## Data Integrity

### Product Snapshots

When a product is purchased, the following fields are snapshot in the cart table:
- `product_name_snapshot`: Product name at time of purchase
- `product_price_snapshot`: Price at time of purchase
- `product_description_snapshot`: Description at time of purchase

This ensures customers see what they paid for, even if the shopkeeper later modifies the product. For example:
- Customer purchases "Camera" at $100
- Shopkeeper changes product to "Telephone" at $120
- Customer's order history still shows "Camera" at $100 (correct)
- Shopkeeper's inventory shows "Telephone" at $120 (correct)

### Concurrency Control

- Stock deduction uses atomic SQL UPDATE with WHERE clause
- PostgreSQL row-level locking prevents concurrent modification conflicts
- SQLite may have locking issues under high concurrency (use PostgreSQL for production)

---

## Pagination

The search endpoint supports pagination:
- Fixed limit of 20 results per request
- Use `offset` parameter to skip results
- Example: offset=0 returns results 1-20, offset=20 returns results 21-40

---

### POST /logout

**Description:** Logs out the current user by clearing the access token cookie. This endpoint is typically called when a user explicitly logs out or when their session expires.

**Authentication:** Required (access_token cookie)

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

**Cookies Cleared:**
- `access_token` cookie is cleared

**Notes:**
- This endpoint clears the user's authentication cookie
- After logout, the user must login again to access protected endpoints
- Shop cookie remains unchanged (shop-specific session is separate)

---

## Order Status Management Endpoints

### GET /shop_orders

**Description:** Retrieves all orders for the currently selected shop. This endpoint is used by shopkeepers to view orders they need to fulfill. Requires both user authentication (to verify the user owns the shop) and shop authentication (to identify which shop's orders to retrieve).

**Authentication:** Required (both access_token and shop_token cookies)

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "orders": [
    {
      "order_id": 1,
      "shop_id": 1,
      "user_email": "customer@example.com",
      "total_cost": 20000,
      "status": "pending",
      "created_at": "2026-10-23T13:28:51",
      "status_updated_at": "2026-10-23T13:28:51",
      "items": [
        {
          "product_id": 1,
          "product_name_snapshot": "Camera",
          "product_price_snapshot": 10000,
          "quantity": 2,
          "total": 20000
        }
      ]
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized:** If user is not authenticated or shop cookie is missing
- **403 Forbidden:** If user does not own the shop
- **500 Internal Server Error:** If database operation fails

**Notes:**
- Only returns orders belonging to the shop identified by the shop_token cookie
- Orders are sorted by creation date (newest first)
- Includes complete order items with snapshot data
- Customer email is included for contact purposes

---

### PUT /update_order_status

**Description:** Updates the status of an order. This endpoint is used by shopkeepers to progress orders through the fulfillment process. Shopkeepers can only transition between "pending" and "working" statuses. They cannot mark orders as "completed" - only customers can do that.

**Authentication:** Required (both access_token and shop_token cookies)

**Request Body (JSON):**
```json
{
  "order_id": 1,
  "status": "working"
}
```

**Field Descriptions:**
- `order_id` (integer, required): ID of the order to update
- `status` (string, required): New status - must be "pending" or "working"

**Allowed Status Transitions for Shopkeepers:**
- `pending` → `working` (order is being processed)
- `working` → `pending` (order returned to pending state)

**Success Response (200 OK):**
```json
{
  "message": "Order status updated successfully",
  "order_id": 1,
  "new_status": "working"
}
```

**Error Responses:**
- **400 Bad Request:** If status transition is invalid or trying to set to "completed"
  ```json
  {
    "detail": "Shopkeepers can only update status to 'pending' or 'working'. Only users can mark orders as 'completed'."
  }
  ```
- **401 Unauthorized:** If user is not authenticated or shop cookie is missing
- **403 Forbidden:** If order does not belong to the shop
- **404 Not Found:** If order does not exist
- **500 Internal Server Error:** If database operation fails

**Notes:**
- Shopkeepers are explicitly blocked from marking orders as "completed"
- This is a security feature to ensure customers confirm receipt
- Status change is timestamped in the database
- Ownership verification ensures shopkeepers can only update their own orders

---

### PUT /user_order_status

**Description:** Updates the status of an order from the customer's perspective. This endpoint is used by customers to confirm that they have received their order. Customers can only mark orders as "completed" when the shop has already set the status to "working".

**Authentication:** Required (access_token cookie)

**Request Body (JSON):**
```json
{
  "order_id": 1,
  "status": "completed"
}
```

**Field Descriptions:**
- `order_id` (integer, required): ID of the order to update
- `status` (string, required): New status - must be "completed"

**Allowed Status Transitions for Customers:**
- `working` → `completed` (customer confirms receipt)

**Success Response (200 OK):**
```json
{
  "message": "Order status updated successfully",
  "order_id": 1,
  "new_status": "completed"
}
```

**Error Responses:**
- **400 Bad Request:** If status transition is invalid
  ```json
  {
    "detail": "Users can only mark orders as 'completed' when status is 'working'. Current status: pending"
  }
  ```
- **401 Unauthorized:** If user is not authenticated
- **403 Forbidden:** If order does not belong to the user
- **404 Not Found:** If order does not exist
- **500 Internal Server Error:** If database operation fails

**Notes:**
- Customers can only mark their own orders as completed
- Order must be in "working" status before customer can complete it
- This ensures the shop has started processing before customer confirms
- Status change is timestamped in the database

---

## Sales Analytics Endpoints

### GET /product_sales

**Description:** Retrieves a summary of sales data for all products in the currently selected shop. This provides shopkeepers with analytics on their sales performance, including total revenue, quantities sold, and buyer information.

**Authentication:** Required (both access_token and shop_token cookies)

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "product_sales": [
    {
      "product_id": 1,
      "product_name": "Camera",
      "total_quantity": 50,
      "total_revenue": 500000,
      "total_orders": 25,
      "buyers": ["customer1@example.com", "customer2@example.com", "customer3@example.com"]
    }
  ],
  "total_products": 1
}
```

**Field Descriptions:**
- `product_id` (integer): Unique identifier for the product
- `product_name` (string): Name of the product (from snapshot)
- `total_quantity` (integer): Total quantity sold across all orders
- `total_revenue` (integer): Total revenue in cents
- `total_orders` (integer): Number of orders containing this product
- `buyers` (array of strings): List of unique customer emails who purchased this product

**Error Responses:**
- **401 Unauthorized:** If user is not authenticated or shop cookie is missing
- **403 Forbidden:** If user does not own the shop
- **500 Internal Server Error:** If database operation fails

**Notes:**
- Only returns sales for products belonging to the shop identified by shop_token
- Revenue is in cents (divide by 100 for dollars)
- Buyers list includes unique customers (no duplicates)
- Uses product snapshots to preserve historical product names

---

### GET /product_sales/{product_id}

**Description:** Retrieves detailed sales history for a specific product. This includes complete customer information (name, email, phone, address) for each sale, enabling shopkeepers to contact customers or analyze purchase patterns.

**Authentication:** Required (both access_token and shop_token cookies)

**URL Parameters:**
- `product_id` (integer, required): ID of the product to get sales details for

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "product_id": 1,
  "sales": [
    {
      "order_id": 1,
      "customer_name": "John Doe",
      "customer_email": "john.doe@example.com",
      "customer_phone": "1234567890",
      "customer_address": "123 Main Street, New York, NY 10001",
      "quantity": 2,
      "price": 10000,
      "total": 20000,
      "purchase_date": "2026-10-23T13:28:51",
      "order_status": "completed"
    }
  ],
  "total_sales": 1
}
```

**Field Descriptions:**
- `order_id` (integer): ID of the order
- `customer_name` (string): Full name of the customer
- `customer_email` (string): Email address of the customer
- `customer_phone` (string): Phone number of the customer
- `customer_address` (string): Physical address of the customer
- `quantity` (integer): Quantity purchased in this order
- `price` (integer): Price per unit in cents (from snapshot)
- `total` (integer): Total cost for this item in cents
- `purchase_date` (string): ISO 8601 timestamp of purchase
- `order_status` (string): Current status of the order

**Error Responses:**
- **401 Unauthorized:** If user is not authenticated or shop cookie is missing
- **403 Forbidden:** If user does not own the shop or product
- **404 Not Found:** If product does not exist
- **500 Internal Server Error:** If database operation fails

**Notes:**
- Only returns sales for products belonging to the shop identified by shop_token
- All customer contact information is included (name, email, phone, address)
- Prices are from purchase-time snapshots (not current product prices)
- Sales are sorted by purchase date (newest first)
- Useful for customer service, shipping, and analytics

---

## Pricing Convention

All prices are stored and transmitted in **cents** (integer) to avoid floating-point precision issues:
- $79.99 is stored as 7999
- $100.00 is stored as 10000
- Client must divide by 100 to display in dollars

---

## Database Schema Notes

### User Model
- Includes `phone` and `address` fields for customer contact information
- Password is hashed with bcrypt (not stored in plain text)

### Cart Model
- Includes snapshot fields to preserve purchase details
- Links to both user and shop for tracking
- Links to order for order history

### Product Model
- Linked to shop for ownership verification
- Amount field represents current stock quantity

### Order Model
- Links to user for ownership
- Status field for order tracking
- Total cost calculated from cart items

---

## Rate Limiting

Not currently implemented (deferred per user request). Recommended for production to prevent abuse.

---

## Notes for Developers

- All write operations should use try/except with rollback
- Ownership verification should be performed before any modification
- Use atomic operations for stock updates to prevent race conditions
- Always snapshot product details at purchase time
- Test with PostgreSQL for production-level concurrency
- SQLite is suitable for development but has locking limitations
