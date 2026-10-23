// Cart page + checkout. The cart is local; POST /buy_product is the only thing that creates an order.
(function () {
  if (!Auth.requireLogin()) return;
  renderHeader();
  const app = $("#app");
  let placing = false;

  function done(r) {
    app.replaceChildren(el("h1", {}, "Order placed"),
      el("div", { class: "order" },
        el("div", { class: "ohead" }, el("strong", {}, "Order #" + r.order_id), el("span", {}, "Total " + money(r.total_cost))),
        el("ul", {}, (r.items || []).map((i) => el("li", {}, i.product_name + " × " + i.quantity + " at " + money(i.price) + " = " + money(i.total)))),
        el("p", {}, el("a", { href: "orders.html?id=" + encodeURIComponent(r.order_id) }, "View order"), " · ", el("a", { href: "index.html" }, "Keep shopping"))));
  }

  async function place(btn, err) {
    if (placing) return;
    placing = true; err.textContent = ""; setBusy(btn, true, "Placing order…");
    try {
      const r = await Api.buy(Cart.items().map((i) => ({ product_id: i.product_id, quantity: i.quantity })));
      if (!r || r.success !== true) throw new Error((r && r.message) || "The order was not confirmed.");
      Cart.clear();
      done(r);
    } catch (e) {
      err.textContent = e.message + (e.status === 0 ? " Check Orders before trying again, in case the order went through." : " Your cart is unchanged.");
    } finally { placing = false; setBusy(btn, false); }
  }

  function draw() {
    const items = Cart.items();
    if (!items.length) {
      app.replaceChildren(el("h1", {}, "Your cart"), el("div", { class: "state" }, "Your cart is empty. ", el("a", { href: "index.html" }, "Browse products")));
      return;
    }
    const est = items.reduce((n, i) => n + i.product_price * i.quantity, 0);
    const rows = items.map((i) => el("li", { class: "line" }, tile(i.product_name),
      el("div", {}, el("a", { href: "product-details.html?id=" + encodeURIComponent(i.product_id) + "&shop=" + encodeURIComponent(i.shop_id) }, i.product_name),
        el("div", { class: "shop" }, i.shop_name)),
      el("div", { class: "unit" }, money(i.product_price)),
      el("input", { class: "qty", type: "number", min: 1, max: i.stock, value: i.quantity, "aria-label": "Quantity for " + i.product_name,
        onchange: (e) => { Cart.setQuantity(i.product_id, parseInt(e.target.value, 10) || 1); draw(); } }),
      el("div", { class: "lt" }, money(i.product_price * i.quantity)),
      el("button", { class: "rm", type: "button", onclick: () => { Cart.remove(i.product_id); draw(); } }, "Remove")));
    const err = el("p", { class: "form-error", role: "alert" });
    const btn = el("button", { class: "btn", type: "button" }, "Place order");
    btn.addEventListener("click", () => place(btn, err));
    app.replaceChildren(el("h1", {}, "Your cart"), el("ul", { class: "lines" }, rows),
      el("div", { class: "summary" },
        el("p", { class: "total" }, "Estimated total " + money(est)),
        el("p", { class: "note" }, "Prices and stock are confirmed by the store when you place the order. There is no payment step in this store."),
        err, btn));
  }
  draw();
})();
