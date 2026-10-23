// Change the backend URL here only. Open the frontend at http://localhost:<port> (not 127.0.0.1)
// so the SameSite=lax cookies are treated as same-site as http://localhost:8000.
const API_BASE_URL = "http://127.0.0.1:8000";
const APP_NAME = "Bazaar";
const SESSION_KEY = "bazaar_session"; // non-secret UI marker; the real token is an HTTP-only cookie
const CART_KEY = "bazaar_cart";       // client-side cart (the backend has no cart endpoints)
const SESSION_MS = 60 * 60 * 1000;    // access_token lifetime documented as 60 minutes
