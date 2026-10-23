# Bazaar frontend (vanilla HTML/CSS/JS)

## Run locally in VS Code
1. Start your backend (default `http://localhost:8000`). Apply `BACKEND_CHANGES.md` (401 handling, CORS with credentials, search ordering).
2. Open the `frontend/` folder in VS Code and serve it at **http://localhost:5500** (not 127.0.0.1):
   - Live Server: set `"liveServer.settings.host": "localhost"` and port 5500, then "Go Live"; or
   - terminal: `cd frontend && python -m http.server 5500`
3. Visit http://localhost:5500/register.html.

Backend URL: change `API_BASE_URL` in `js/config.js` (the only place).

## Files
index.html (catalog/search) · product-details.html · shop.html · cart.html (cart + checkout) · orders.html · seller.html · login.html · register.html
js/: config, utils, api, auth, cart, products, details, shop, checkout, orders, seller · css/style.css

## Syntax check (only check I could run without your backend)
`for f in js/*.js; do node --check "$f"; done`

## Known limits (from the API itself)
no catalog/shop-list/get-product endpoints · no images, categories, ratings, payment, address or profile endpoints ·
shop names unavailable on /view, so shop pages say "Shop #id" · order item names are current listings (line totals are the recorded ones) ·
`Next` on the catalog appears whenever a page is full (the API returns no total).
