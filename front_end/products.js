// Catalog + search page. Browsing = POST /search; an empty query matches every product (confirmed by the backend owner).
(function () {
  renderHeader();
  const p = new URLSearchParams(location.search);
  const q = (p.get("q") || "").trim();
  const offset = Math.max(0, parseInt(p.get("offset"), 10) || 0);
  const grid = $("#grid"), pager = $("#pager"), meta = $("#meta");
  $("#title").textContent = q ? "Results for “" + q + "”" : "All products";

  function card(r) {
    const out = r.amount <= 0, low = r.amount > 0 && r.amount <= 5;
    const href = "product-details.html?id=" + encodeURIComponent(r.product_id) + "&shop=" + encodeURIComponent(r.shop.shop_id);
    const add = el("button", {
      class: "btn", type: "button", disabled: out,
      onclick: () => {
        const res = Cart.add({ product_id: r.product_id, product_name: r.product_name, product_price: r.product_price,
          shop_id: r.shop.shop_id, shop_name: r.shop.shop_name, stock: r.amount });
        toast(res.message, res.ok ? "ok" : "error");
      },
    }, out ? "Out of stock" : "Add to cart");
    return el("article", { class: "card" }, tile(r.product_name),
      el("h2", {}, el("a", { href }, r.product_name)),
      el("a", { class: "shop", href: "shop.html?id=" + encodeURIComponent(r.shop.shop_id) }, r.shop.shop_name),
      el("p", { class: "price" }, money(r.product_price)),
      el("p", { class: "stock" + (low || out ? " low" : "") }, out ? "Unavailable" : low ? "Only " + r.amount + " left" : "In stock"),
      add);
  }

  async function load() {
    grid.setAttribute("aria-busy", "true");
    grid.replaceChildren(el("div", { class: "state" }, "Loading products…"));
    pager.replaceChildren(); meta.textContent = "";
    try {
      const d = await Api.search(q, offset);
      const list = Array.isArray(d.results) ? d.results : [];
      if (!list.length) {
        grid.replaceChildren(el("div", { class: "state" }, q ? "No products match “" + q + "”. Try a different word." : offset ? "No more products." : "No products have been listed yet."));
      } else grid.replaceChildren(...list.map(card));
      const limit = d.limit || 20;
      if (list.length) meta.textContent = "Showing " + (offset + 1) + "–" + (offset + list.length);
      const go = (o) => "index.html?" + new URLSearchParams({ q, offset: o });
      pager.append(offset > 0 ? el("a", { href: go(Math.max(0, offset - limit)) }, "Previous") : el("span", {}, "Previous"),
        list.length === limit ? el("a", { href: go(offset + limit) }, "Next") : el("span", {}, "Next"));
    } catch (e) {
      grid.replaceChildren(el("div", { class: "state error", role: "alert" }, e.message, " ", el("button", { class: "btn alt", type: "button", onclick: load }, "Try again")));
    } finally { grid.setAttribute("aria-busy", "false"); }
  }
  load();
})();
