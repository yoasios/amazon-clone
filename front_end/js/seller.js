// Seller dashboard: shops (/my_shops, /shop_login, /switch_shop) and products (/view, /products, /product_change, /product_stock).
(function () {
  if (!Auth.requireLogin()) return;
  renderHeader();
  const ACTIVE_KEY = "bazaar_active_shop"; // remembers the selection only; the real shop cookie is HTTP-only
  const app = $("#app");
  const shopsBox = el("section", { "aria-label": "Your shops" }, el("div", { class: "seller-section" })), 
        manage = el("section", { "aria-label": "Shop products" }, el("div", { class: "seller-section" })), 
        ordersBox = el("section", { "aria-label": "Shop orders" }, el("div", { class: "seller-section" })), 
        salesBox = el("section", { "aria-label": "Product sales" }, el("div", { class: "seller-section" }));
  let active = null;
  let currentTab = "products"; // "products", "orders", or "sales"
  let tabsElement = null; // Store reference to tabs element

  const toCents = (v) => {
    const n = parseFloat(v);
    if (!isFinite(n) || n < 0) throw new Error("Enter a valid price, like 79.99.");
    return Math.round(n * 100);
  };
  function field(label, name, attrs = {}) {
    const id = "f-" + name + "-" + Math.random().toString(36).slice(2, 6);
    const input = attrs.tag === "textarea" ? el("textarea", { id, name, rows: 2, required: true }) : el("input", { id, name, required: true, ...attrs });
    return el("div", { class: "fld" }, el("label", { for: id }, label), input);
  }

  // ---------- shops ----------
  function createShopForm() {
    const f = el("form", { class: "panel", novalidate: true }, 
      el("h2", {}, "✨ Create New Shop"),
      field("Shop Name", "shop_name"), 
      field("Description", "shop_description", { tag: "textarea" }),
      field("Address", "shop_address"), 
      field("Phone", "shop_phone", { type: "tel" }), 
      field("Email", "shop_email", { type: "email" }),
      el("p", { class: "form-error", role: "alert" }), 
      el("button", { class: "btn", type: "submit" }, "🚀 Create Shop")
    );
    bindForm(f, async (d) => {
      const r = await Api.shopLogin({ shop_name: d.shop_name.trim(), shop_description: d.shop_description.trim(),
        shop_address: d.shop_address.trim(), shop_phone: d.shop_phone.trim(), shop_email: d.shop_email.trim() });
      toast("Shop created successfully!", "ok");
      f.reset();
      await loadShops(r.shop_id, false); // creating a shop already sets the shop cookie
    });
    return f;
  }

  async function select(shop, sync) {
    if (sync) {
      try { await Api.switchShop(shop.shop_id); } catch (e) { toast(e.message, "error"); return; }
    }
    active = shop;
    sessionStorage.setItem(ACTIVE_KEY, String(shop.shop_id));
    drawShops(); loadCurrentTab();
  }

  function switchTab(tab) {
    currentTab = tab;
    updateTabs();
    loadCurrentTab();
  }

  function updateTabs() {
    if (!tabsElement) return;
    const buttons = tabsElement.querySelectorAll('.tab');
    buttons.forEach(btn => {
      btn.classList.remove('active');
      if (btn.textContent.includes('Products') && currentTab === 'products') {
        btn.classList.add('active');
      } else if (btn.textContent.includes('Orders') && currentTab === 'orders') {
        btn.classList.add('active');
      } else if (btn.textContent.includes('Sales') && currentTab === 'sales') {
        btn.classList.add('active');
      }
    });
  }

  function drawTabs() {
    if (tabsElement) return tabsElement; // Return existing if already created
    tabsElement = el("div", { class: "tabs" },
      el("button", { class: "tab" + (currentTab === "products" ? " active" : ""), type: "button" }, "📦 Products"),
      el("button", { class: "tab" + (currentTab === "orders" ? " active" : ""), type: "button" }, "📋 Orders"),
      el("button", { class: "tab" + (currentTab === "sales" ? " active" : ""), type: "button" }, "💰 Sales")
    );
    
    // Add event listeners separately to ensure they work
    const buttons = tabsElement.querySelectorAll('.tab');
    buttons[0].addEventListener('click', () => switchTab("products"));
    buttons[1].addEventListener('click', () => switchTab("orders"));
    buttons[2].addEventListener('click', () => switchTab("sales"));
    
    return tabsElement;
  }

  async function loadCurrentTab() {
    if (!active) return;
    if (currentTab === "products") {
      manage.style.display = "block";
      ordersBox.style.display = "none";
      salesBox.style.display = "none";
      await loadProducts();
    } else if (currentTab === "orders") {
      manage.style.display = "none";
      ordersBox.style.display = "block";
      salesBox.style.display = "none";
      await loadOrders();
    } else if (currentTab === "sales") {
      manage.style.display = "none";
      ordersBox.style.display = "none";
      salesBox.style.display = "block";
      await loadSales();
    }
  }

  let shops = [];
  function drawShops() {
    shopsBox.firstElementChild.replaceChildren(
      el("h2", {}, "🏪 Your Shops"),
      shops.length 
        ? el("div", { class: "shops" }, shops.map((s) => {
            const on = active && active.shop_id === s.shop_id;
            return el("article", { class: "shopcard" + (on ? " on" : "") }, 
              el("div", { class: "shopcard-header" },
                el("h3", {}, s.shop_name),
                on ? el("span", { class: "badge ok" }, "Active") : null
              ),
              el("p", {}, s.shop_description),
              el("div", { class: "shopcard-meta" },
                el("span", {}, "📍 " + s.shop_address),
                el("span", {}, "📞 " + s.shop_phone),
                el("span", {}, "✉️ " + s.shop_email)
              ),
              el("button", { 
                class: "btn" + (on ? "" : " alt"), 
                type: "button", 
                disabled: on, 
                onclick: () => select(s, true) 
              }, on ? "✓ Managing" : "Manage Products")
            );
          }))
        : el("div", { class: "empty-state" },
            el("div", { class: "empty-state-icon" }, "🏪"),
            el("h3", { class: "empty-state-title" }, "No shops yet"),
            el("p", { class: "empty-state-text" }, "Create your first shop below to start selling.")
          )
    );
  }

  async function loadShops(selectId, sync) {
    try {
      const d = await Api.myShops();
      shops = Array.isArray(d.shops) ? d.shops : [];
      const want = selectId != null ? selectId : parseInt(sessionStorage.getItem(ACTIVE_KEY), 10);
      const found = shops.find((s) => s.shop_id === want);
      drawShops();
      if (found) await select(found, sync !== false);
      else { active = null; manage.firstElementChild.replaceChildren(); ordersBox.firstElementChild.replaceChildren(); salesBox.firstElementChild.replaceChildren(); }
    } catch (e) { shopsBox.firstElementChild.replaceChildren(el("h2", {}, "🏪 Your Shops"), errorState(e, () => loadShops())); }
  }

  // ---------- products ----------
  function row(p) {
    const stock = el("input", { class: "qty", type: "number", min: 0, step: 1, value: p.amount, "aria-label": "Stock for " + p.product_name });
    const sbtn = el("button", { class: "btn alt sm", type: "button" }, "Set stock");
    sbtn.addEventListener("click", async () => {
      const n = Number(stock.value);
      if (stock.value === "" || !Number.isInteger(n) || n < 0) { toast("Enter a whole number, 0 or more.", "error"); return; }
      setBusy(sbtn, true, "Saving…");
      try {
        const r = await Api.setStock({ product_id: p.product_id, amount: n });
        p.amount = r.new_amount; stock.value = r.new_amount;
        toast("Stock set to " + r.new_amount, "ok");
      } catch (e) { toast(e.message, "error"); } finally { setBusy(sbtn, false); }
    });
    const tr = el("tr", {},
      el("td", {}, el("a", { href: "product-details.html?id=" + encodeURIComponent(p.product_id) + "&shop=" + encodeURIComponent(p.shop_id) }, p.product_name)),
      el("td", {}, money(p.product_price)), el("td", { class: "stockcell" }, stock, sbtn),
      el("td", {}, el("button", { class: "btn sm", type: "button", onclick: () => tr.replaceWith(editRow(p)) }, "Edit")));
    return tr;
  }

  function editRow(p) {
    const f = el("form", { class: "panel", novalidate: true },
      field("Name", "product_name", { value: p.product_name }), field("Price (USD)", "product_price", { type: "number", step: "0.01", min: "0", value: (p.product_price / 100).toFixed(2) }),
      el("div", { class: "fld" }, el("label", {}, "Description"), el("textarea", { name: "product_description", rows: 2, required: true }, p.product_description)),
      el("p", { class: "form-error", role: "alert" }),
      el("button", { class: "btn", type: "submit" }, "Save changes"),
      el("button", { class: "btn sm", type: "button", onclick: () => tr.replaceWith(row(p)) }, "Cancel"));
    const tr = el("tr", {}, el("td", { colspan: 4 }, f));
    bindForm(f, async (d) => {
      const body = { product_id: p.product_id }; // send only what changed (partial update)
      if (d.product_name.trim() !== p.product_name) body.product_name = d.product_name.trim();
      const cents = toCents(d.product_price);
      if (cents !== p.product_price) body.product_price = cents;
      if (d.product_description.trim() !== p.product_description) body.product_description = d.product_description.trim();
      if (Object.keys(body).length === 1) { toast("No changes to save.", "info"); return; }
      await Api.changeProduct(body);
      toast("Product updated", "ok");
      await loadProducts();
    });
    return tr;
  }

  function addForm() {
    const f = el("form", { class: "panel", novalidate: true }, 
      el("h2", {}, "➕ Add New Product"),
      field("Product Name", "product_name"), 
      field("Price (USD)", "product_price", { type: "number", step: "0.01", min: "0" }),
      field("Description", "product_description", { tag: "textarea" }), 
      field("Starting Stock", "amount", { type: "number", step: "1", min: "0", value: "0" }),
      el("p", { class: "form-error", role: "alert" }), 
      el("button", { class: "btn", type: "submit" }, "➕ Add Product")
    );
    bindForm(f, async (d) => {
      const amount = Number(d.amount);
      if (!Number.isInteger(amount) || amount < 0) throw new Error("Starting stock must be a whole number, 0 or more.");
      const body = { product_name: d.product_name.trim(), product_price: toCents(d.product_price), product_description: d.product_description.trim(), amount };
      await Api.switchShop(active.shop_id); // make sure the shop cookie points at the shop shown on this page
      await Api.addProduct(body);
      toast("Product added successfully!", "ok");
      f.reset();
      await loadProducts();
    });
    return f;
  }

  async function loadProducts() {
    if (!active) return;
    const shop = active;
    manage.firstElementChild.replaceChildren(
      el("h2", {}, "📦 " + shop.shop_name + " - Products"),
      el("div", { class: "state" }, "Loading products…")
    );
    try {
      const list = await Api.viewShop(shop.shop_id);
      if (!active || active.shop_id !== shop.shop_id) return; // selection changed while loading
      const rows = Array.isArray(list) ? list : [];
      manage.firstElementChild.replaceChildren(
        el("h2", {}, "📦 " + shop.shop_name + " - Products"),
        rows.length
          ? el("div", { class: "tblwrap" }, el("table", { class: "tbl" },
              el("thead", {}, el("tr", {}, 
                el("th", {}, "Product"), 
                el("th", {}, "Price"), 
                el("th", {}, "Stock"), 
                el("th", {}, "Actions")
              )),
              el("tbody", {}, rows.map(row))))
          : el("div", { class: "empty-state" },
              el("div", { class: "empty-state-icon" }, "📦"),
              el("h3", { class: "empty-state-title" }, "No products yet"),
              el("p", { class: "empty-state-text" }, "Add your first product below.")
            ),
        el("div", { style: "height:1.25rem" }), 
        addForm()
      );
    } catch (e) { manage.firstElementChild.replaceChildren(el("h2", {}, "📦 " + shop.shop_name + " - Products"), errorState(e, loadProducts)); }
  }

  // ---------- orders ----------
  function statusBadge(status) {
    const colors = { pending: "warn", working: "info", delivered: "info", completed: "ok", cancelled: "error" };
    return el("span", { class: "badge " + (colors[status] || "neutral") }, status.toUpperCase());
  }

  function orderCard(o) {
    const items = Array.isArray(o.items) ? o.items : [];
    const itemsList = el("ul", { class: "items" }, items.map(i =>
      el("li", {}, 
        el("span", { class: "item-name" }, i.product_name),
        el("span", { class: "item-qty" }, "× " + i.quantity),
        el("span", { class: "item-total" }, money(i.price * i.quantity))
      )
    ));
    
    const statusSelect = el("select", { class: "status-select" },
      el("option", { value: "pending" }, "⏳ Pending"),
      el("option", { value: "working" }, "🔧 Working")
    );
    statusSelect.value = o.status;
    
    const updateBtn = el("button", { class: "btn btn-primary", type: "button" }, "Update Status");
    updateBtn.addEventListener("click", async () => {
      setBusy(updateBtn, true, "Updating…");
      try {
        await Api.updateOrderStatus({ order_id: o.order_id, status: statusSelect.value });
        toast("Order status updated", "ok");
        await loadOrders();
      } catch (e) { toast(e.message, "error"); } finally { setBusy(updateBtn, false); }
    });

    return el("article", { class: "ordercard order-shop" },
      el("div", { class: "order-header" },
        el("div", { class: "order-id-section" },
          el("span", { class: "order-icon" }, "📦"),
          el("h3", {}, "Order #" + o.order_id)
        ),
        statusBadge(o.status),
        el("span", { class: "order-date" }, "📅 " + fmtDate(o.created_at))
      ),
      el("div", { class: "order-customer-section" },
        el("h4", {}, "👤 Customer Information"),
        el("div", { class: "customer-details" },
          el("span", { class: "customer-detail" }, "📧 " + o.user_email)
        )
      ),
      el("div", { class: "order-items-section" },
        el("h4", {}, "🛍️ Items in this order"),
        itemsList
      ),
      el("div", { class: "order-footer" },
        el("span", { class: "order-total-label" }, "Order total"),
        el("span", { class: "order-total-amount" }, money(o.total_cost))
      ),
      el("div", { class: "order-actions" },
        el("span", { class: "action-hint" }, "Change status to update customer"),
        statusSelect,
        updateBtn
      )
    );
  }

  async function loadOrders() {
    if (!active) return;
    const shop = active;
    ordersBox.firstElementChild.replaceChildren(
      el("h2", {}, "📋 " + shop.shop_name + " - Orders"),
      el("p", { class: "page-subtitle" }, "Manage orders from customers who purchased your products"),
      el("div", { class: "state" }, "Loading orders…")
    );
    try {
      const d = await Api.shopOrders();
      if (!active || active.shop_id !== shop.shop_id) return; // selection changed while loading
      const orders = Array.isArray(d.orders) ? d.orders : [];
      ordersBox.firstElementChild.replaceChildren(
        el("h2", {}, "📋 " + shop.shop_name + " - Orders"),
        el("p", { class: "page-subtitle" }, "Manage orders from customers who purchased your products"),
        orders.length
          ? el("div", { class: "orders" }, orders.map(orderCard))
          : el("div", { class: "empty-state" },
              el("div", { class: "empty-state-icon" }, "📋"),
              el("h3", { class: "empty-state-title" }, "No orders yet"),
              el("p", { class: "empty-state-text" }, "Orders will appear here when customers purchase your products.")
            )
      );
    } catch (e) { ordersBox.firstElementChild.replaceChildren(el("h2", {}, "📋 " + shop.shop_name + " - Orders"), el("p", { class: "page-subtitle" }, "Manage orders from customers who purchased your products"), errorState(e, loadOrders)); }
  }

  // ---------- sales ----------
  function salesRow(p) {
    const tr = el("tr", {},
      el("td", {}, el("a", { href: "product-details.html?id=" + encodeURIComponent(p.product_id) + "&shop=" + encodeURIComponent(active.shop_id) }, p.product_name)),
      el("td", {}, p.total_quantity.toString()),
      el("td", {}, money(p.total_revenue)),
      el("td", {}, p.total_orders.toString()),
      el("td", {}, 
        el("div", {}, p.buyers.length.toString() + " unique buyer" + (p.buyers.length === 1 ? "" : "s")),
        el("div", { class: "customer-info" }, p.buyers.slice(0, 3).join(", ") + (p.buyers.length > 3 ? "..." : ""))
      ),
      el("td", {}, el("button", { class: "btn sm", type: "button", onclick: () => showSalesDetail(p.product_id, p.product_name) }, "View details"))
    );
    return tr;
  }

  async function showSalesDetail(productId, productName) {
    salesBox.firstElementChild.replaceChildren(
      el("h2", {}, "💰 " + active.shop_name + " - Sales"), 
      el("button", { class: "btn sm", type: "button", onclick: loadSales }, "← Back to all sales"), 
      el("h3", {}, productName + " - Sales Details"), 
      el("div", { class: "state" }, "Loading…")
    );
    try {
      const d = await Api.productSalesDetail(productId);
      const sales = Array.isArray(d.sales) ? d.sales : [];
      
      const rows = sales.map(s => el("tr", {},
        el("td", {}, s.order_id.toString()),
        el("td", {}, 
          el("div", {}, el("strong", {}, s.customer_name)),
          el("div", { class: "customer-info" }, s.customer_email),
          el("div", { class: "customer-info" }, "📞 " + s.customer_phone),
          el("div", { class: "customer-info" }, "📍 " + s.customer_address)
        ),
        el("td", {}, s.quantity.toString()),
        el("td", {}, money(s.price)),
        el("td", {}, money(s.total)),
        el("td", {}, fmtDate(s.purchase_date)),
        el("td", {}, statusBadge(s.order_status))
      ));
      
      salesBox.firstElementChild.replaceChildren(
        el("h2", {}, "💰 " + active.shop_name + " - Sales"),
        el("button", { class: "btn sm", type: "button", onclick: loadSales }, "← Back to all sales"),
        el("h3", {}, productName + " - Sales Details"),
        el("p", { class: "note" }, "Total sales: " + d.total_sales),
        rows.length
          ? el("div", { class: "tblwrap" }, el("table", { class: "tbl" },
              el("thead", {}, el("tr", {},
                el("th", {}, "Order ID"),
                el("th", {}, "Customer Details"),
                el("th", {}, "Quantity"),
                el("th", {}, "Price"),
                el("th", {}, "Total"),
                el("th", {}, "Date"),
                el("th", {}, "Status")
              )),
              el("tbody", {}, rows)))
          : el("div", { class: "empty-state" },
              el("div", { class: "empty-state-icon" }, "📊"),
              el("h3", { class: "empty-state-title" }, "No sales yet"),
              el("p", { class: "empty-state-text" }, "This product hasn't been purchased yet.")
            )
      );
    } catch (e) { salesBox.firstElementChild.replaceChildren(el("h2", {}, "💰 " + active.shop_name + " - Sales"), el("button", { class: "btn sm", type: "button", onclick: loadSales }, "← Back to all sales"), errorState(e, loadSales)); }
  }

  async function loadSales() {
    if (!active) return;
    const shop = active;
    salesBox.firstElementChild.replaceChildren(
      el("h2", {}, "💰 " + shop.shop_name + " - Sales Analytics"),
      el("div", { class: "state" }, "Loading sales…")
    );
    try {
      const d = await Api.productSales();
      if (!active || active.shop_id !== shop.shop_id) return; // selection changed while loading
      const sales = Array.isArray(d.product_sales) ? d.product_sales : [];
      
      // Calculate totals
      const totalRevenue = sales.reduce((sum, s) => sum + s.total_revenue, 0);
      const totalItemsSold = sales.reduce((sum, s) => sum + s.total_quantity, 0);
      const totalOrders = sales.reduce((sum, s) => sum + s.total_orders, 0);
      
      salesBox.firstElementChild.replaceChildren(
        el("h2", {}, "💰 " + shop.shop_name + " - Sales Analytics"),
        el("div", { class: "stats-grid" },
          el("div", { class: "stat-card" }, el("div", { class: "stat-value" }, money(totalRevenue)), el("div", { class: "stat-label" }, "Total Revenue")),
          el("div", { class: "stat-card" }, el("div", { class: "stat-value" }, totalItemsSold.toString()), el("div", { class: "stat-label" }, "Items Sold")),
          el("div", { class: "stat-card" }, el("div", { class: "stat-value" }, totalOrders.toString()), el("div", { class: "stat-label" }, "Total Orders")),
          el("div", { class: "stat-card" }, el("div", { class: "stat-value" }, sales.length.toString()), el("div", { class: "stat-label" }, "Products"))
        ),
        sales.length
          ? el("div", { class: "tblwrap" }, el("table", { class: "tbl" },
              el("thead", {}, el("tr", {},
                el("th", {}, "Product"),
                el("th", {}, "Total Sold"),
                el("th", {}, "Revenue"),
                el("th", {}, "Orders"),
                el("th", {}, "Buyers"),
                el("th", {}, "Actions")
              )),
              el("tbody", {}, sales.map(salesRow))))
          : el("div", { class: "empty-state" },
              el("div", { class: "empty-state-icon" }, "💰"),
              el("h3", { class: "empty-state-title" }, "No sales yet"),
              el("p", { class: "empty-state-text" }, "Sales data will appear here once customers start purchasing your products.")
            )
      );
    } catch (e) { salesBox.firstElementChild.replaceChildren(el("h2", {}, "💰 " + shop.shop_name + " - Sales Analytics"), errorState(e, loadSales)); }
  }

  app.replaceChildren(shopsBox, createShopForm(), manage, ordersBox, salesBox, drawTabs());
  
  // Initialize display states
  ordersBox.style.display = "none";
  salesBox.style.display = "none";
  
  loadShops();
})();
