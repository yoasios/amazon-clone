# Backend findings and suggested changes (checked against your uploaded source; nothing here was applied)

I did not see `auth/jwt.py`, `auth/products_cookie.py`, `auth/shop_cookies.py`, or any `schemas/` or `models/` file.
Items marked (assumes) depend on what you said about `get_current_user` returning `None`.

## 1. Protected routes return 500 when there is no cookie (assumes get_current_user returns None)
`buy_product`, `order_history`, `order_status`, `product_change`, `ProductStock`, `shop_login`, `switch_shop` and `user_shops`
all do `current_user["id"]` / `user["id"]`, which raises TypeError on `None`. Add to `auth/jwt.py`:
```python
from fastapi import Depends, HTTPException

async def require_user(current_user=Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user
```
and use `Depends(require_user)` instead of `Depends(get_current_user)` in those files. The frontend already
sends the user to the login page on a 401 and shows the message.

## 2. /search and /view currently work without login (assumes get_current_user returns None)
Neither handler reads `current_user`, so anonymous visitors can browse. The frontend now allows browsing without
signing in (checkout, orders and seller pages still require it). If you want them protected, use `require_user`
there too; the frontend will then redirect to login automatically.

## 3. /search has no ORDER BY, so pages can repeat or skip products
In `search_products.py`, add `.order_by(Products.product_id)` before `.limit(limit)`.

## 4. /buy_product accepts bad quantities (needs the BuyInput schema to confirm)
With a negative `quantity`, `Products.amount >= quantity` is true and `amount - quantity` increases stock; the order total goes negative.
Require `quantity` > 0 in `BuyInput` (for example `quantity: int = Field(default=1, gt=0)`). The frontend only sends 1 or more.

## 5. CORS with cookies
```python
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5500"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
```
Serve the frontend at http://localhost:5500 (VS Code Live Server defaults to 127.0.0.1; use `localhost`).

## 6. Documentation mismatches
- Shop cookie is `shop_access_token` in code (docs also say `shop_token` in places).
- /view and /search are documented as authenticated but do not enforce it.
- /my_orders and /order/{id} return the current `price` but the recorded `total`; the frontend shows only quantity and recorded total.
- /login returns the JWT in the response body; the frontend ignores it and relies on the cookie.

## Already fine
`POST /logout` exists in `logout.py` and deletes both cookies; no change needed.
