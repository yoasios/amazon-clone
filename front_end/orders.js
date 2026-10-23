(function () {
  if (!Auth.requireLogin()) return;
  renderHeader();
  const app = $("#app");
  const id = new URLSearchParams(location.search).get("id");
  const note = el("p", { class: "note" }, "Item names show the current listing and can differ from what you bought. Line totals and the order total are what was recorded at purchase.");

  function orderCard(o, linked) {
    return el("article", { class: "order" },
      el("div", { class: "ohead" },
        linked ? el("a", { href: "orders.html?id=" + encodeURIComponent(o.order_id) }, "Order #" + o.order_id) : el("strong", {}, "Order #" + o.order_id),
        el("span", { class: "badge" }, o.status)),
      el("p", { class: "note" }, fmtDate(o.created_at) + " · " + o.item_count + (o.item_count === 1 ? " item" : " items")),
      el("ul", {}, (o.items || []).map((i) => el("li", {}, i.product_name + " × " + i.quantity + ": " + money(i.total)))),
      el("strong", {}, "Total " + money(o.total_cost)));
  }

  async function load() {
    app.replaceChildren(el("h1", {}, id ? "Order #" + id : "Your orders"), el("div", { class: "state" }, "Loading…"));
    try {
      if (id) {
        const o = await Api.order(id);
        app.replaceChildren(el("h1", {}, "Order #" + o.order_id), orderCard(o, false), note, el("p", {}, el("a", { href: "orders.html" }, "All orders")));
      } else {
        const d = await Api.myOrders();
        const list = Array.isArray(d.orders) ? d.orders : [];
        app.replaceChildren(el("h1", {}, "Your orders"),
          list.length ? [list.map((o) => orderCard(o, true)), note]
            : el("div", { class: "state" }, "No orders yet. ", el("a", { href: "index.html" }, "Browse products")));
      }
    } catch (e) {
      app.replaceChildren(el("h1", {}, id ? "Order #" + id : "Your orders"),
        e.status === 404 ? el("div", { class: "state" }, "Order not found. ", el("a", { href: "orders.html" }, "See all orders")) : errorState(e, load));
    }
  }
  load();
})();
