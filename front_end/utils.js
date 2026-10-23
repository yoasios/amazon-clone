const $ = (s, r = document) => r.querySelector(s);

// Safe DOM builder: strings become text nodes, so backend content is never parsed as HTML.
function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat()) if (c != null) n.append(c);
  return n;
}

const money = (cents) => (Number(cents) / 100).toLocaleString("en-US", { style: "currency", currency: "USD" });

function toast(msg, type = "info") {
  let box = $("#toasts");
  if (!box) { box = el("div", { id: "toasts", "aria-live": "polite" }); document.body.append(box); }
  const t = el("div", { class: "toast " + type, role: type === "error" ? "alert" : "status" }, msg);
  box.append(t);
  setTimeout(() => t.remove(), 4500);
}

function setBusy(btn, busy, label) {
  if (busy) { btn.dataset.label = btn.textContent; btn.textContent = label || "Working…"; }
  else if (btn.dataset.label) btn.textContent = btn.dataset.label;
  btn.disabled = busy;
}

// The API has no product images, so each product gets a lettered tile.
function tile(name) {
  let h = 0;
  for (const ch of String(name)) h = (h * 31 + ch.charCodeAt(0)) % 360;
  const t = el("div", { class: "tile", "aria-hidden": "true" }, (String(name).trim()[0] || "?").toUpperCase());
  t.style.setProperty("--h", h);
  return t;
}

function renderHeader() {
  const s = Auth.get();
  const q = new URLSearchParams(location.search).get("q") || "";
  const cart = el("a", { href: "cart.html", id: "cart-link" }, "Cart (" + Cart.count() + ")");
  $("#site-header").replaceChildren(el("div", { class: "bar" },
    el("a", { class: "brand", href: "index.html" }, APP_NAME),
    el("form", { class: "search", role: "search", action: "index.html" },
      el("label", { class: "sr", for: "q" }, "Search products"),
      el("input", { id: "q", name: "q", type: "search", value: q, placeholder: "Search all shops" }),
      el("button", { type: "submit" }, "Search")),
    el("nav", {}, s
      ? [el("a", { href: "orders.html" }, "Orders"), el("a", { href: "seller.html" }, "Sell"),
         cart,
         el("button", { class: "link", type: "button", onclick: () => Auth.logout() }, "Sign out")]
      : [el("a", { href: "login.html" }, "Sign in"), el("a", { href: "register.html" }, "Create account"), cart])));
}
document.addEventListener("cart:changed", () => {
  const a = $("#cart-link"); if (a) a.textContent = "Cart (" + Cart.count() + ")";
});

// ---- added in Part 2 ----
function fmtDate(s) { const d = new Date(s); return isNaN(d) ? String(s) : d.toLocaleString(); }
function errorState(e, retry) {
  return el("div", { class: "state error", role: "alert" }, e.message, " ",
    retry ? el("button", { class: "btn alt", type: "button", onclick: retry }, "Try again") : null);
}
