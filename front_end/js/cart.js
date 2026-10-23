// Client-side cart. Nothing is reserved or priced until POST /buy_product succeeds;
// the backend's total_cost and stock checks are authoritative.
const Cart = {
  items() {
    try { const a = JSON.parse(localStorage.getItem(CART_KEY)); return Array.isArray(a) ? a : []; }
    catch { return []; }
  },
  save(a) { localStorage.setItem(CART_KEY, JSON.stringify(a)); document.dispatchEvent(new Event("cart:changed")); },
  count() { return this.items().reduce((n, i) => n + i.quantity, 0); },
  add(p) {
    const a = this.items(), i = a.find((x) => x.product_id === p.product_id);
    if (i) {
      if (i.quantity >= p.stock) return { ok: false, message: "All " + p.stock + " in stock are already in your cart." };
      i.quantity++; i.stock = p.stock; i.product_price = p.product_price;
    } else a.push({ ...p, quantity: 1 });
    this.save(a);
    return { ok: true, message: "Added to cart" };
  },
  setQuantity(id, q) {
    const a = this.items(), i = a.find((x) => x.product_id === id);
    if (!i) return;
    i.quantity = Math.max(1, Math.min(q, i.stock));
    this.save(a);
  },
  remove(id) { this.save(this.items().filter((x) => x.product_id !== id)); },
  clear() { this.save([]); },
};
