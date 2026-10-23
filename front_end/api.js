class ApiError extends Error {
  constructor(status, message, data) { super(message); this.status = status; this.data = data; }
}

function detailText(d, status) {
  if (d && typeof d === "object" && d.detail !== undefined) {
    if (typeof d.detail === "string") return d.detail;
    if (Array.isArray(d.detail)) // FastAPI 422 validation errors
      return d.detail.map((e) => (e.loc ? e.loc.slice(1).join(".") + ": " : "") + e.msg).join("; ");
  }
  return status === 500
    ? "The server hit an error. If your session expired, sign in again."
    : "Request failed (" + status + ").";
}

async function request(method, path, body) {
  let res;
  try {
    res = await fetch(API_BASE_URL + path, {
      method,
      credentials: "include", // required: auth lives in HTTP-only cookies
      headers: { Accept: "application/json", ...(body !== undefined ? { "Content-Type": "application/json" } : {}) },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, "Cannot reach the server. Check that the backend is running, API_BASE_URL is correct, and CORS allows credentials.");
  }
  const text = await res.text();
  let data = null;
  if (text) { try { data = JSON.parse(text); } catch { data = text; } }
  if (!res.ok) {
    const msg = detailText(data, res.status);
    // 401 about the *shop* token must not end the user session.
    if (res.status === 401 && !/shop/i.test(msg)) {
      Auth.clear();
      if (!/(login|register)\.html$/.test(location.pathname)) Auth.requireLogin();
    }
    throw new ApiError(res.status, msg, data);
  }
  return data;
}

// One wrapper per backend route (verified against the backend source files; /logout exists in logout.py).
const Api = {
  signin: (b) => request("POST", "/signin", b),
  login: (b) => request("POST", "/login", b),
  logout: () => request("POST", "/logout"),
  shopLogin: (b) => request("POST", "/shop_login", b),
  myShops: () => request("GET", "/my_shops"),
  switchShop: (id) => request("POST", "/switch_shop/" + encodeURIComponent(id)),
  addProduct: (b) => request("POST", "/products", b),
  changeProduct: (b) => request("PUT", "/product_change", b),
  setStock: (b) => request("PUT", "/product_stock", b),
  viewShop: (id) => request("POST", "/view/" + encodeURIComponent(id)),
  search: (query, offset = 0) => request("POST", "/search", { query, offset }),
  buy: (items) => request("POST", "/buy_product", { items }),
  myOrders: () => request("GET", "/my_orders"),
  order: (id) => request("GET", "/order/" + encodeURIComponent(id)),
  shopOrders: () => request("GET", "/shop_orders"),
  updateOrderStatus: (b) => request("PUT", "/update_order_status", b),
  userOrderStatus: (b) => request("PUT", "/user_order_status", b),
  productSales: () => request("GET", "/product_sales"),
  productSalesDetail: (id) => request("GET", "/product_sales/" + encodeURIComponent(id)),
  health: () => request("GET", "/health"),
};
