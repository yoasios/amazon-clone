(function () {
  if (!Auth.requireLogin()) return;
  renderHeader();
  const app = $("#app");
  const id = new URLSearchParams(location.search).get("id");
  const note = el("p", { class: "note" }, "Item names and prices show the current listing, so they can differ from what you paid. The order total is what was recorded.");

  function statusBadge(status) {
    const colors = { pending: "warn", working: "info", delivered: "info", completed: "ok", cancelled: "error" };
    return el("span", { class: "badge " + (colors[status] || "neutral") }, status.toUpperCase());
  }

  function orderCard(o, linked) {
    const card = el("article", { class: "order order-customer" },
      el("div", { class: "order-header" },
        el("div", { class: "order-id-section" },
          el("span", { class: "order-icon" }, "🛒"),
          linked ? el("a", { href: "orders.html?id=" + encodeURIComponent(o.order_id) }, "Order #" + o.order_id) : el("strong", {}, "Order #" + o.order_id)
        ),
        statusBadge(o.status)
      ),
      el("div", { class: "order-meta" },
        el("span", { class: "order-date" }, "📅 " + fmtDate(o.created_at)),
        el("span", { class: "order-items-count" }, "📦 " + o.item_count + (o.item_count === 1 ? " item" : " items"))
      ),
      el("div", { class: "order-items" },
        el("h4", {}, "Items you purchased"),
        el("ul", {}, (o.items || []).map((i) => el("li", {}, 
          el("span", { class: "item-name" }, i.product_name),
          el("span", { class: "item-qty" }, "× " + i.quantity),
          el("span", { class: "item-price" }, money(i.price)),
          el("span", { class: "item-total" }, money(i.total))
        )))
      ),
      el("div", { class: "order-footer" },
        el("span", { class: "order-total-label" }, "Total paid"),
        el("span", { class: "order-total-amount" }, money(o.total_cost))
      )
    );

    // Add action buttons based on order status
    const actionsDiv = el("div", { class: "order-actions" });
    
    // "Mark as Delivered" button for working orders (customer confirms delivery)
    if (o.status === "working") {
      const deliveredBtn = el("button", { class: "btn btn-primary", type: "button" }, "🚚 Mark as Delivered");
      deliveredBtn.addEventListener("click", async () => {
        if (!confirm("Have you received the product? This will mark it as delivered.")) return;
        setBusy(deliveredBtn, true, "Updating…");
        try {
          await Api.userOrderStatus({ order_id: o.order_id, status: "delivered" });
          toast("Order marked as delivered", "ok");
          load();
        } catch (e) { toast(e.message, "error"); } finally { setBusy(deliveredBtn, false); }
      });
      actionsDiv.appendChild(deliveredBtn);
    }
    
    // "Confirm Receipt" button for delivered orders (customer confirms completion)
    if (o.status === "delivered") {
      const completeBtn = el("button", { class: "btn btn-success", type: "button" }, "✓ Confirm Receipt");
      completeBtn.addEventListener("click", async () => {
        if (!confirm("Confirm you have received and checked the product? This will complete the order.")) return;
        setBusy(completeBtn, true, "Updating…");
        try {
          await Api.userOrderStatus({ order_id: o.order_id, status: "completed" });
          toast("Order marked as completed", "ok");
          load();
        } catch (e) { toast(e.message, "error"); } finally { setBusy(completeBtn, false); }
      });
      actionsDiv.appendChild(completeBtn);
    }
    
    // "Cancel Order" button for pending and working orders
    if ((o.status === "pending" || o.status === "working")) {
      const cancelBtn = el("button", { class: "btn btn-danger", type: "button" }, "✕ Cancel Order");
      cancelBtn.addEventListener("click", async () => {
        if (!confirm("Are you sure you want to cancel this order? Refund amount will depend on order status and time elapsed.")) return;
        setBusy(cancelBtn, true, "Cancelling…");
        try {
          const result = await Api.cancelOrder(o.order_id);
          toast("Order cancelled. Refund: " + money(result.refund_amount), "ok");
          load();
        } catch (e) { toast(e.message, "error"); } finally { setBusy(cancelBtn, false); }
      });
      actionsDiv.appendChild(cancelBtn);
    }
    
    if (actionsDiv.children.length > 0) {
      card.appendChild(actionsDiv);
    }

    return card;
  }

  async function load() {
    app.replaceChildren(
      el("div", { class: "page-header page-header-customer" },
        el("h1", {}, id ? "🛒 Order #" + id : "🛒 My Orders"),
        el("p", { class: "page-subtitle" }, id ? "Your order details" : "View and manage your purchase history")
      ),
      el("div", { class: "state" }, "Loading…")
    );
    try {
      if (id) {
        const o = await Api.order(id);
        app.replaceChildren(
          el("div", { class: "page-header page-header-customer" },
            el("h1", {}, "🛒 Order #" + o.order_id),
            el("p", { class: "page-subtitle" }, "Your order details"),
            el("a", { class: "back-link", href: "orders.html" }, "← Back to all orders")
          ),
          orderCard(o, false),
          note
        );
      } else {
        const d = await Api.myOrders();
        const list = Array.isArray(d.orders) ? d.orders : [];
        if (list.length) {
          app.replaceChildren(
            el("div", { class: "page-header page-header-customer" },
              el("h1", {}, "🛒 My Orders"),
              el("p", { class: "page-subtitle" }, "View and manage your purchase history")
            ),
            ...list.map((o) => orderCard(o, true)),
            note
          );
        } else {
          app.replaceChildren(
            el("div", { class: "page-header page-header-customer" },
              el("h1", {}, "🛒 My Orders"),
              el("p", { class: "page-subtitle" }, "View and manage your purchase history")
            ),
            el("div", { class: "empty-state" },
              el("div", { class: "empty-state-icon" }, "🛒"),
              el("h3", { class: "empty-state-title" }, "No orders yet"),
              el("p", { class: "empty-state-text" }, "Start shopping to see your orders here. ", el("a", { href: "index.html" }, "Browse products"))
            )
          );
        }
      }
    } catch (e) {
      app.replaceChildren(
        el("div", { class: "page-header page-header-customer" },
          el("h1", {}, id ? "🛒 Order #" + id : "🛒 My Orders"),
          el("p", { class: "page-subtitle" }, id ? "Your order details" : "View and manage your purchase history")
        ),
        e.status === 404 
          ? el("div", { class: "empty-state" },
              el("div", { class: "empty-state-icon" }, "❌"),
              el("h3", { class: "empty-state-title" }, "Order not found"),
              el("p", { class: "empty-state-text" }, "This order doesn't exist or you don't have access to it. ", el("a", { href: "orders.html" }, "See all orders"))
            )
          : errorState(e, load)
      );
    }
  }
  load();
})();
