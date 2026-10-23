(function () {
  if (!Auth.requireLogin()) return;
  renderHeader();
  const app = $("#app");
  const id = new URLSearchParams(location.search).get("id");
  const note = el("p", { class: "note" }, "Item names and prices show the current listing, so they can differ from what you paid. The order total is what was recorded.");

  function statusBadge(status) {
    const colors = { pending: "warn", working: "info", completed: "ok", cancelled: "error" };
    return el("span", { class: "badge " + (colors[status] || "neutral") }, status.toUpperCase());
  }

  function orderCard(o, linked) {
    const card = el("article", { class: "order" },
      el("div", { class: "ohead" },
        linked ? el("a", { href: "orders.html?id=" + encodeURIComponent(o.order_id) }, "Order #" + o.order_id) : el("strong", {}, "Order #" + o.order_id),
        statusBadge(o.status)),
      el("p", { class: "note" }, fmtDate(o.created_at) + " · " + o.item_count + (o.item_count === 1 ? " item" : " items")),
      el("ul", {}, (o.items || []).map((i) => el("li", {}, i.product_name + " × " + i.quantity + " at " + money(i.price) + " = " + money(i.total)))),
      el("strong", {}, "Total " + money(o.total_cost)));

    // Add "Mark as completed" button for working orders
    if (o.status === "working" && !linked) {
      const completeBtn = el("button", { class: "btn sm", type: "button" }, "Mark as completed");
      completeBtn.addEventListener("click", async () => {
        setBusy(completeBtn, true, "Updating…");
        try {
          await Api.userOrderStatus({ order_id: o.order_id, status: "completed" });
          toast("Order marked as completed", "ok");
          load();
        } catch (e) { toast(e.message, "error"); } finally { setBusy(completeBtn, false); }
      });
      card.appendChild(el("div", { class: "order-actions" }, completeBtn));
    }

    return card;
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
        if (list.length) {
          app.replaceChildren(el("h1", {}, "Your orders"), ...list.map((o) => orderCard(o, true)), note);
        } else {
          app.replaceChildren(el("h1", {}, "Your orders"),
            el("div", { class: "state" }, "No orders yet. ", el("a", { href: "index.html" }, "Browse products")));
        }
      }
    } catch (e) {
      app.replaceChildren(el("h1", {}, id ? "Order #" + id : "Your orders"),
        e.status === 404 ? el("div", { class: "state" }, "Order not found. ", el("a", { href: "orders.html" }, "See all orders")) : errorState(e, load));
    }
  }
  load();
})();
