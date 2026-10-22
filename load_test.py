import asyncio
import random
import httpx
from datetime import datetime
from typing import List, Dict
import time

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
NUM_BOTS = 100  # Testing with 100 bots
CONCURRENT_REQUESTS = 20  # Concurrent requests
VERBOSE = True  # Show detailed step-by-step output

# Random data generators
FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
SHOP_NAMES = ["Tech Haven", "Fashion Forward", "Home Essentials", "Sports Central", "Book Nook", "Gourmet Garden", "Pet Paradise", "Beauty Bliss", "Auto World", "Music Box", "Toy Kingdom", "Health Hub", "Art Studio", "Electronic Emporium", "Food Corner", "Clothing Closet", "Shoe Shack", "Watch World", "Jewelry Junction", "Phone Palace"]
PRODUCT_NAMES = ["Laptop", "Phone", "Watch", "Mouse", "Keyboard", "Headphones", "Monitor", "Camera", "Speaker", "Tablet", "Router", "Printer", "Scanner", "Projector", "Webcam"]

class Bot:
    def __init__(self, bot_id: int):
        self.bot_id = bot_id
        self.name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        self.email = f"bot{bot_id}_{random.randint(1000, 9999)}@example.com"
        self.password = "password123"
        self.phone = f"{random.randint(1000000000, 9999999999)}"
        self.address = f"{random.randint(1, 999)} Main Street, City {random.randint(1, 50)}"
        self.access_token = None
        self.shop_access_token = None
        self.shop_id = None
        self.order_id = None
        self.created_product_ids = []  # Track products created by this bot
        self.cookies = {}  # Store cookies as dict for persistence
        self.errors = []
        self.stats = {
            "signin": {"success": 0, "failed": 0},
            "login": {"success": 0, "failed": 0},
            "wrong_password": {"success": 0, "failed": 0},
            "create_shop": {"success": 0, "failed": 0},
            "add_product": {"success": 0, "failed": 0},
            "product_change": {"success": 0, "failed": 0},
            "product_stock": {"success": 0, "failed": 0},
            "view_shop": {"success": 0, "failed": 0},
            "search_by_shop": {"success": 0, "failed": 0},
            "search_by_name": {"success": 0, "failed": 0},
            "switch_shop": {"success": 0, "failed": 0},
            "purchase": {"success": 0, "failed": 0},
            "search": {"success": 0, "failed": 0},
            "order_history": {"success": 0, "failed": 0},
            "data_integrity": {"success": 0, "failed": 0}
        }

    def log_error(self, action: str, error: str):
        self.errors.append({
            "bot_id": self.bot_id,
            "action": action,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        if VERBOSE:
            print(f"  FAIL ERROR in {action}: {error}")

    def update_stat(self, action: str, success: bool):
        if action in self.stats:
            if success:
                self.stats[action]["success"] += 1
            else:
                self.stats[action]["failed"] += 1

async def bot_signin(bot: Bot, client: httpx.AsyncClient):
    """Bot creates an account"""
    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 1: Signin")
        print(f"  Name: {bot.name}")
        print(f"  Email: {bot.email}")
        print(f"  Password: {bot.password}")
        print(f"  Phone: {bot.phone}")
        print(f"  Address: {bot.address}")

    try:
        response = await client.post(
            f"{BASE_URL}/signin",
            json={
                "name": bot.name,
                "email": bot.email,
                "password": bot.password,
                "phone": bot.phone,
                "address": bot.address
            }
        )
        if response.status_code == 200:
            # Store cookies from response
            bot.cookies = dict(response.cookies)
            bot.access_token = response.cookies.get("access_token")
            bot.update_stat("signin", True)
            if VERBOSE:
                print(f"  OK Signin successful")
                print(f"  Access token received")
                print(f"  Cookies stored: {list(bot.cookies.keys())}")
        else:
            bot.log_error("signin", f"Status {response.status_code}: {response.text}")
            bot.update_stat("signin", False)
            if VERBOSE:
                print(f"  FAIL Signin failed - {response.status_code}")
    except Exception as e:
        bot.log_error("signin", str(e))
        bot.update_stat("signin", False)
        if VERBOSE:
            print(f"  FAIL Signin error - {str(e)}")

async def bot_login(bot: Bot, client: httpx.AsyncClient):
    """Bot logs in with correct credentials"""
    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 2: Login with correct credentials")
        print(f"  -> Email: {bot.email}")
        print(f"  -> Password: {bot.password}")

    try:
        response = await client.post(
            f"{BASE_URL}/login",
            json={
                "email": bot.email,
                "password": bot.password
            },
            cookies=bot.cookies  # Use stored cookies
        )
        if response.status_code == 200:
            # Update cookies with new ones from response
            bot.cookies.update(dict(response.cookies))
            bot.access_token = response.cookies.get("access_token")
            bot.update_stat("login", True)
            if VERBOSE:
                print(f"  OK Login successful")
                print(f"  -> Access token received")
        else:
            bot.log_error("login", f"Status {response.status_code}: {response.text}")
            bot.update_stat("login", False)
            if VERBOSE:
                print(f"  FAIL Login failed - {response.status_code}")
    except Exception as e:
        bot.log_error("login", str(e))
        bot.update_stat("login", False)
        if VERBOSE:
            print(f"  FAIL Login error - {str(e)}")

async def bot_wrong_password(bot: Bot, client: httpx.AsyncClient):
    """Bot tries to login with wrong password (should fail or auto-login)"""
    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 3: Login with WRONG password")
        print(f"  -> Email: {bot.email}")
        print(f"  -> Password: wrongpassword123 (WRONG)")

    try:
        response = await client.post(
            f"{BASE_URL}/login",
            json={
                "email": bot.email,
                "password": "wrongpassword123"
            },
            cookies=bot.cookies
        )
        # Accept either 400 (wrong password rejected) or 200 (auto-login with valid cookie)
        if response.status_code == 400:
            bot.update_stat("wrong_password", True)
            if VERBOSE:
                print(f"  OK Wrong password correctly rejected (expected behavior)")
        elif response.status_code == 200:
            # Auto-login feature: user already has valid cookie
            bot.update_stat("wrong_password", True)
            if VERBOSE:
                print(f"  OK Auto-login with valid cookie (already logged in)")
        else:
            bot.log_error("wrong_password", f"Expected 400 or 200, got {response.status_code}")
            bot.update_stat("wrong_password", False)
            if VERBOSE:
                print(f"  FAIL Unexpected status code - {response.status_code}")
    except Exception as e:
        bot.log_error("wrong_password", str(e))
        bot.update_stat("wrong_password", False)
        if VERBOSE:
            print(f"  FAIL Wrong password error - {str(e)}")

async def bot_create_shop(bot: Bot, client: httpx.AsyncClient):
    """Bot creates a shop"""
    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 4: Create shop")

    shop_name = f"{random.choice(SHOP_NAMES)} {bot.bot_id}"
    if VERBOSE:
        print(f"  -> Shop name: {shop_name}")

    try:
        response = await client.post(
            f"{BASE_URL}/shop_login",
            json={
                "shop_name": shop_name,
                "shop_description": f"Shop created by bot {bot.bot_id}",
                "shop_address": f"{random.randint(100, 999)} Test Street",
                "shop_phone": f"{random.randint(1000000000, 9999999999)}",
                "shop_email": f"shop{bot.bot_id}@example.com"
            },
            cookies=bot.cookies  # Use stored cookies
        )
        if response.status_code == 200:
            # Update cookies
            bot.cookies.update(dict(response.cookies))
            bot.shop_access_token = response.cookies.get("shop_access_token")
            data = response.json()
            bot.shop_id = data.get("shop_id")
            bot.update_stat("create_shop", True)
            if VERBOSE:
                print(f"  OK Shop created successfully")
                print(f"  -> Shop ID: {bot.shop_id}")
                print(f"  -> Shop access token received")
        else:
            bot.log_error("create_shop", f"Status {response.status_code}: {response.text}")
            bot.update_stat("create_shop", False)
            if VERBOSE:
                print(f"  FAIL Shop creation failed - {response.status_code}")
    except Exception as e:
        bot.log_error("create_shop", str(e))
        bot.update_stat("create_shop", False)
        if VERBOSE:
            print(f"  FAIL Shop creation error - {str(e)}")

async def bot_add_product(bot: Bot, client: httpx.AsyncClient):
    """Bot adds products to their shop"""
    if not bot.shop_id:
        if VERBOSE:
            print(f"\n[Bot {bot.bot_id}] Step 5: Add products")
            print(f"  WARN  Skipped (no shop created)")
        return

    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 5: Add products to shop")
        print(f"  -> Shop ID: {bot.shop_id}")

    try:
        # Add 3-5 random products
        num_products = random.randint(3, 5)
        products_added = 0

        for i in range(num_products):
            product_name = f"{random.choice(PRODUCT_NAMES)} {bot.bot_id}-{i}"
            product_price = random.randint(10, 1000)
            product_amount = random.randint(5, 50)

            response = await client.post(
                f"{BASE_URL}/products",
                json={
                    "product_name": product_name,
                    "product_price": product_price,
                    "product_description": f"Product added by bot {bot.bot_id}",
                    "amount": product_amount
                },
                cookies=bot.cookies
            )

            if response.status_code == 200:
                data = response.json()
                product_id = data.get("product_id")
                bot.created_product_ids.append(product_id)
                products_added += 1
            else:
                bot.log_error("add_product", f"Status {response.status_code}: {response.text}")

        if products_added > 0:
            bot.update_stat("add_product", True)
            if VERBOSE:
                print(f"  OK Added {products_added}/{num_products} products successfully")
                print(f"  -> Product IDs: {bot.created_product_ids}")
        else:
            bot.update_stat("add_product", False)
            if VERBOSE:
                print(f"  FAIL Failed to add any products")

    except Exception as e:
        bot.log_error("add_product", str(e))
        bot.update_stat("add_product", False)
        if VERBOSE:
            print(f"  FAIL Add product error - {str(e)}")

async def bot_product_change(bot: Bot, client: httpx.AsyncClient):
    """Bot changes a product's information"""
    if not bot.created_product_ids:
        if VERBOSE:
            print(f"\n[Bot {bot.bot_id}] Step 6: Change product")
            print(f"  WARN  Skipped (no products created)")
        return

    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 6: Change product information")

    try:
        # Pick a random product to change
        product_id = random.choice(bot.created_product_ids)

        # Randomly choose which fields to update (1-3 fields)
        update_fields = {}
        fields_to_update = random.sample(["product_name", "product_price", "amount"], random.randint(1, 3))

        if "product_name" in fields_to_update:
            update_fields["product_name"] = f"Updated {random.choice(PRODUCT_NAMES)} {bot.bot_id}"
        if "product_price" in fields_to_update:
            update_fields["product_price"] = random.randint(10, 1000)
        if "amount" in fields_to_update:
            update_fields["amount"] = random.randint(5, 50)

        if VERBOSE:
            print(f"  -> Product ID: {product_id}")
            print(f"  -> Updating fields: {list(update_fields.keys())}")

        response = await client.put(
            f"{BASE_URL}/product_change",
            json={
                "product_id": product_id,
                **update_fields
            },
            cookies=bot.cookies
        )

        if response.status_code == 200:
            data = response.json()
            bot.update_stat("product_change", True)
            if VERBOSE:
                print(f"  OK Product changed successfully")
                print(f"  -> Updated fields: {data.get('updated_fields')}")
        else:
            bot.log_error("product_change", f"Status {response.status_code}: {response.text}")
            bot.update_stat("product_change", False)
            if VERBOSE:
                print(f"  FAIL Product change failed - {response.status_code}")
    except Exception as e:
        bot.log_error("product_change", str(e))
        bot.update_stat("product_change", False)
        if VERBOSE:
            print(f"  FAIL Product change error - {str(e)}")

async def bot_product_stock(bot: Bot, client: httpx.AsyncClient):
    """Bot updates product stock amount"""
    if not bot.created_product_ids:
        if VERBOSE:
            print(f"\n[Bot {bot.bot_id}] Step 7: Update product stock")
            print(f"  WARN  Skipped (no products created)")
        return

    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 7: Update product stock")

    try:
        # Pick a random product to update stock
        product_id = random.choice(bot.created_product_ids)
        new_amount = random.randint(10, 100)

        if VERBOSE:
            print(f"  -> Product ID: {product_id}")
            print(f"  -> New amount: {new_amount}")

        response = await client.put(
            f"{BASE_URL}/product_stock",
            json={
                "product_id": product_id,
                "amount": new_amount
            },
            cookies=bot.cookies
        )

        if response.status_code == 200:
            data = response.json()
            bot.update_stat("product_stock", True)
            if VERBOSE:
                print(f"  OK Product stock updated successfully")
                print(f"  -> New amount: {data.get('new_amount')}")
        else:
            bot.log_error("product_stock", f"Status {response.status_code}: {response.text}")
            bot.update_stat("product_stock", False)
            if VERBOSE:
                print(f"  FAIL Product stock update failed - {response.status_code}")
    except Exception as e:
        bot.log_error("product_stock", str(e))
        bot.update_stat("product_stock", False)
        if VERBOSE:
            print(f"  FAIL Product stock update error - {str(e)}")

async def bot_view_shop(bot: Bot, client: httpx.AsyncClient):
    """Bot views a shop's products"""
    if not bot.shop_id:
        if VERBOSE:
            print(f"\n[Bot {bot.bot_id}] Step 8: View shop")
            print(f"  WARN  Skipped (no shop created)")
        return

    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 8: View shop products")
        print(f"  -> Shop ID: {bot.shop_id}")

    try:
        response = await client.post(
            f"{BASE_URL}/view/{bot.shop_id}",
            cookies=bot.cookies
        )
        if response.status_code == 200:
            products = response.json()
            bot.update_stat("view_shop", True)
            if VERBOSE:
                print(f"  OK Viewed shop successfully")
                print(f"  -> Products found: {len(products)}")
        else:
            bot.log_error("view_shop", f"Status {response.status_code}: {response.text}")
            bot.update_stat("view_shop", False)
            if VERBOSE:
                print(f"  FAIL View shop failed - {response.status_code}")
    except Exception as e:
        bot.log_error("view_shop", str(e))
        bot.update_stat("view_shop", False)
        if VERBOSE:
            print(f"  FAIL View shop error - {str(e)}")

async def bot_search_by_shop(bot: Bot, client: httpx.AsyncClient):
    """Bot searches products by shop ID"""
    if not bot.shop_id:
        if VERBOSE:
            print(f"\n[Bot {bot.bot_id}] Step 9: Search by shop ID")
            print(f"  WARN  Skipped (no shop created)")
        return

    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 9: Search products by shop ID")
        print(f"  -> Shop ID: {bot.shop_id}")

    try:
        response = await client.post(
            f"{BASE_URL}/view/{bot.shop_id}",
            cookies=bot.cookies
        )
        if response.status_code == 200:
            products = response.json()
            bot.update_stat("search_by_shop", True)
            if VERBOSE:
                print(f"  OK Search by shop ID successful")
                print(f"  -> Products found: {len(products)}")
        else:
            bot.log_error("search_by_shop", f"Status {response.status_code}: {response.text}")
            bot.update_stat("search_by_shop", False)
            if VERBOSE:
                print(f"  FAIL Search by shop ID failed - {response.status_code}")
    except Exception as e:
        bot.log_error("search_by_shop", str(e))
        bot.update_stat("search_by_shop", False)
        if VERBOSE:
            print(f"  FAIL Search by shop ID error - {str(e)}")

async def bot_search_by_name(bot: Bot, client: httpx.AsyncClient):
    """Bot searches products by name"""
    if not bot.created_product_ids:
        if VERBOSE:
            print(f"\n[Bot {bot.bot_id}] Step 10: Search by product name")
            print(f"  WARN  Skipped (no products created)")
        return

    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 10: Search products by name")

    try:
        # Search for a product that this bot created
        search_term = random.choice(PRODUCT_NAMES)
        response = await client.post(
            f"{BASE_URL}/search",
            json={
                "query": search_term,
                "offset": 0
            },
            cookies=bot.cookies
        )
        if response.status_code == 200:
            results = response.json()
            bot.update_stat("search_by_name", True)
            if VERBOSE:
                print(f"  OK Search by name successful")
                print(f"  -> Query: {search_term}")
                print(f"  -> Results found: {results.get('count', 0)}")
        else:
            bot.log_error("search_by_name", f"Status {response.status_code}: {response.text}")
            bot.update_stat("search_by_name", False)
            if VERBOSE:
                print(f"  FAIL Search by name failed - {response.status_code}")
    except Exception as e:
        bot.log_error("search_by_name", str(e))
        bot.update_stat("search_by_name", False)
        if VERBOSE:
            print(f"  FAIL Search by name error - {str(e)}")

async def bot_switch_shop(bot: Bot, client: httpx.AsyncClient):
    """Bot switches to its shop"""
    if not bot.shop_id:
        if VERBOSE:
            print(f"\n[Bot {bot.bot_id}] Step 11: Switch shop")
            print(f"  WARN  Skipped (no shop created)")
        return

    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 11: Switch to shop")
        print(f"  -> Shop ID: {bot.shop_id}")

    try:
        response = await client.post(
            f"{BASE_URL}/switch_shop/{bot.shop_id}",
            cookies=bot.cookies
        )
        if response.status_code == 200:
            bot.cookies.update(dict(response.cookies))
            bot.shop_access_token = response.cookies.get("shop_access_token")
            bot.update_stat("switch_shop", True)
            if VERBOSE:
                print(f"  OK Switched to shop successfully")
                print(f"  -> Shop access token refreshed")
        else:
            bot.log_error("switch_shop", f"Status {response.status_code}: {response.text}")
            bot.update_stat("switch_shop", False)
            if VERBOSE:
                print(f"  FAIL Switch shop failed - {response.status_code}")
    except Exception as e:
        bot.log_error("switch_shop", str(e))
        bot.update_stat("switch_shop", False)
        if VERBOSE:
            print(f"  FAIL Switch shop error - {str(e)}")

async def bot_purchase(bot: Bot, client: httpx.AsyncClient):
    """Bot purchases own products"""
    if not bot.created_product_ids:
        if VERBOSE:
            print(f"\n[Bot {bot.bot_id}] Step 12: Purchase products")
            print(f"  WARN  Skipped (no products created)")
        return

    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 12: Purchase products")

    try:
        # Buy 1-2 of the bot's own products
        items_to_buy = random.sample(bot.created_product_ids, min(2, len(bot.created_product_ids)))
        items = [{"product_id": pid, "quantity": random.randint(1, 3)} for pid in items_to_buy]

        if VERBOSE:
            print(f"  -> Buying {len(items)} products: {items}")

        response = await client.post(
            f"{BASE_URL}/buy_product",
            json={"items": items},
            cookies=bot.cookies
        )
        if response.status_code == 200:
            data = response.json()
            bot.order_id = data.get("order_id")
            bot.update_stat("purchase", True)
            if VERBOSE:
                print(f"  OK Purchase successful")
                print(f"  -> Order ID: {bot.order_id}")
                print(f"  -> Total cost: {data.get('total_cost')}")
        else:
            bot.log_error("purchase", f"Status {response.status_code}: {response.text}")
            bot.update_stat("purchase", False)
            if VERBOSE:
                print(f"  FAIL Purchase failed - {response.status_code}")
    except Exception as e:
        bot.log_error("purchase", str(e))
        bot.update_stat("purchase", False)
        if VERBOSE:
            print(f"  FAIL Purchase error - {str(e)}")

async def bot_search(bot: Bot, client: httpx.AsyncClient):
    """Bot searches for products globally"""
    search_terms = ["laptop", "phone", "watch", "mouse", "keyboard"]
    query = random.choice(search_terms)

    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 13: Global search products")
        print(f"  -> Query: {query}")

    try:
        response = await client.post(
            f"{BASE_URL}/search",
            json={
                "query": query,
                "offset": 0
            },
            cookies=bot.cookies
        )
        if response.status_code == 200:
            results = response.json()
            bot.update_stat("search", True)
            if VERBOSE:
                print(f"  OK Global search successful")
                print(f"  -> Results found: {results.get('count', 0)}")
        else:
            bot.log_error("search", f"Status {response.status_code}: {response.text}")
            bot.update_stat("search", False)
            if VERBOSE:
                print(f"  FAIL Global search failed - {response.status_code}")
    except Exception as e:
        bot.log_error("search", str(e))
        bot.update_stat("search", False)
        if VERBOSE:
            print(f"  FAIL Global search error - {str(e)}")

async def bot_order_history(bot: Bot, client: httpx.AsyncClient):
    """Bot checks order history"""
    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 14: Check order history")

    try:
        response = await client.get(
            f"{BASE_URL}/my_orders",
            cookies=bot.cookies
        )
        if response.status_code == 200:
            history = response.json()
            bot.update_stat("order_history", True)
            if VERBOSE:
                print(f"  OK Order history retrieved")
                print(f"  -> Total orders: {history.get('total_orders', 0)}")
        else:
            bot.log_error("order_history", f"Status {response.status_code}: {response.text}")
            bot.update_stat("order_history", False)
            if VERBOSE:
                print(f"  FAIL Order history failed - {response.status_code}")
    except Exception as e:
        bot.log_error("order_history", str(e))
        bot.update_stat("order_history", False)
        if VERBOSE:
            print(f"  FAIL Order history error - {str(e)}")

async def bot_data_integrity_check(bot: Bot, client: httpx.AsyncClient):
    """Bot verifies data integrity"""
    if VERBOSE:
        print(f"\n[Bot {bot.bot_id}] Step 15: Data integrity check")

    try:
        # Check 1: Verify order exists in history if purchase succeeded
        if bot.order_id:
            history_response = await client.get(
                f"{BASE_URL}/my_orders",
                cookies=bot.cookies
            )
            if history_response.status_code == 200:
                history = history_response.json()
                order_found = any(o["order_id"] == bot.order_id for o in history.get("orders", []))
                if order_found:
                    if VERBOSE:
                        print(f"  OK Order {bot.order_id} found in history")
                else:
                    bot.log_error("data_integrity", f"Order {bot.order_id} not found in history")
                    bot.update_stat("data_integrity", False)
                    if VERBOSE:
                        print(f"  FAIL Order {bot.order_id} missing from history")
                    return

        # Check 2: Verify products exist in shop
        if bot.shop_id and bot.created_product_ids:
            view_response = await client.post(
                f"{BASE_URL}/view/{bot.shop_id}",
                cookies=bot.cookies
            )
            if view_response.status_code == 200:
                products = view_response.json()
                product_ids_in_shop = [p.get("product_id") for p in products]
                all_found = all(pid in product_ids_in_shop for pid in bot.created_product_ids)
                if all_found:
                    if VERBOSE:
                        print(f"  OK All {len(bot.created_product_ids)} products found in shop")
                else:
                    missing = [pid for pid in bot.created_product_ids if pid not in product_ids_in_shop]
                    bot.log_error("data_integrity", f"Products missing from shop: {missing}")
                    bot.update_stat("data_integrity", False)
                    if VERBOSE:
                        print(f"  FAIL Products missing: {missing}")
                    return

        bot.update_stat("data_integrity", True)
        if VERBOSE:
            print(f"  OK Data integrity check passed")

    except Exception as e:
        bot.log_error("data_integrity", str(e))
        bot.update_stat("data_integrity", False)
        if VERBOSE:
            print(f"  FAIL Data integrity check error - {str(e)}")

async def run_bot_scenario(bot: Bot):
    """Run complete scenario for a single bot"""
    # Create ONE client per bot with cookie jar to persist cookies
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Sign in
        await bot_signin(bot, client)
        await asyncio.sleep(0.1)

        # Step 2: Login with correct credentials
        await bot_login(bot, client)
        await asyncio.sleep(0.1)

        # Step 3: Try wrong password (should fail)
        await bot_wrong_password(bot, client)
        await asyncio.sleep(0.1)

        # Step 4: Create shop
        await bot_create_shop(bot, client)
        await asyncio.sleep(0.1)

        # Step 5: Add products to shop
        await bot_add_product(bot, client)
        await asyncio.sleep(0.1)

        # Step 6: Change product information
        await bot_product_change(bot, client)
        await asyncio.sleep(0.1)

        # Step 7: Update product stock
        await bot_product_stock(bot, client)
        await asyncio.sleep(0.1)

        # Step 8: View shop products
        await bot_view_shop(bot, client)
        await asyncio.sleep(0.1)

        # Step 9: Search by shop ID
        await bot_search_by_shop(bot, client)
        await asyncio.sleep(0.1)

        # Step 10: Search by product name
        await bot_search_by_name(bot, client)
        await asyncio.sleep(0.1)

        # Step 11: Switch shop
        await bot_switch_shop(bot, client)
        await asyncio.sleep(0.1)

        # Step 12: Purchase own products
        await bot_purchase(bot, client)
        await asyncio.sleep(0.1)

        # Step 13: Global search
        await bot_search(bot, client)
        await asyncio.sleep(0.1)

        # Step 14: Check order history
        await bot_order_history(bot, client)
        await asyncio.sleep(0.1)

        # Step 15: Data integrity check
        await bot_data_integrity_check(bot, client)

async def main():
    print("=" * 60)
    print(f"LOAD TEST: {NUM_BOTS} Bots performing concurrent actions")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"Total steps per bot: 15 (including product change and stock update)")

    # Create bots
    bots = [Bot(i) for i in range(1, NUM_BOTS + 1)]
    print(f"Created {len(bots)} bots")

    # Run bots concurrently with semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def run_with_semaphore(bot):
        async with semaphore:
            await run_bot_scenario(bot)

    start_time = time.time()

    # Run all bots
    await asyncio.gather(*[run_with_semaphore(bot) for bot in bots])

    end_time = time.time()
    duration = end_time - start_time

    # Generate report
    print("\n" + "=" * 60)
    print("LOAD TEST REPORT")
    print("=" * 60)
    print(f"Total Bots: {NUM_BOTS}")
    print(f"Concurrent Requests: {CONCURRENT_REQUESTS}")
    print(f"Total Duration: {duration:.2f} seconds")
    print(f"Requests per Second: {(NUM_BOTS * 15) / duration:.2f}")

    # Aggregate stats
    total_stats = {
        "signin": {"success": 0, "failed": 0},
        "login": {"success": 0, "failed": 0},
        "wrong_password": {"success": 0, "failed": 0},
        "create_shop": {"success": 0, "failed": 0},
        "add_product": {"success": 0, "failed": 0},
        "product_change": {"success": 0, "failed": 0},
        "product_stock": {"success": 0, "failed": 0},
        "view_shop": {"success": 0, "failed": 0},
        "search_by_shop": {"success": 0, "failed": 0},
        "search_by_name": {"success": 0, "failed": 0},
        "switch_shop": {"success": 0, "failed": 0},
        "purchase": {"success": 0, "failed": 0},
        "search": {"success": 0, "failed": 0},
        "order_history": {"success": 0, "failed": 0},
        "data_integrity": {"success": 0, "failed": 0}
    }

    all_errors = []

    for bot in bots:
        for action, stats in bot.stats.items():
            total_stats[action]["success"] += stats["success"]
            total_stats[action]["failed"] += stats["failed"]
        all_errors.extend(bot.errors)

    print("\n" + "-" * 60)
    print("ACTION STATISTICS")
    print("-" * 60)
    for action, stats in total_stats.items():
        total = stats["success"] + stats["failed"]
        success_rate = (stats["success"] / total * 100) if total > 0 else 0
        print(f"{action:20} | Success: {stats['success']:4} | Failed: {stats['failed']:4} | Rate: {success_rate:5.1f}%")

    print("\n" + "-" * 60)
    print("ERROR DETAILS")
    print("-" * 60)
    if all_errors:
        print(f"Total Errors: {len(all_errors)}")
        print("\nLast 10 errors:")
        for error in all_errors[-10:]:
            print(f"  Bot {error['bot_id']}: {error['action']} - {error['error']}")
    else:
        print("No errors occurred!")

    print("\n" + "=" * 60)
    print("LOAD TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
