(function () {
  renderHeader();
  const id = parseInt(new URLSearchParams(location.search).get("id"), 10), app = $("#app");

  function card(r) {
    const out = r.amount <= 0, low = r.amount > 0 && r.amount <= 5;
    const add = el("button", {
      class: "btn", type: "button", disabled: out,
      onclick: () => {
        const res = Cart.add({ product_id: r.product_id, product_name: r.product_name, product_price: r.product_price,
          shop_id: r.shop_id, shop_name: "Shop #" + r.shop_id, stock: r.amount });
        toast(res.message, res.ok ? "ok" : "error");
      },
    }, out ? "Out of stock" : "Add to cart");
    return el("article", { class: "card" }, tile(r.product_name),
      el("h2", {}, el("a", { href: "product-details.html?id=" + encodeURIComponent(r.product_id) + "&shop=" + encodeURIComponent(r.shop_id) }, r.product_name)),
      el("p", { class: "price" }, money(r.product_price)),
      el("p", { class: "stock" + (low || out ? " low" : "") }, out ? "Unavailable" : low ? "Only " + r.amount + " left" : "In stock"), add);
  }

  async function load() {
    if (!id) { app.replaceChildren(el("div", { class: "state error" }, "This shop link is incomplete.")); return; }
    app.replaceChildren(el("h1", {}, "Shop #" + id), el("div", { class: "state" }, "Loading products…"));
    try {
      const list = await Api.viewShop(id);
      app.replaceChildren(el("h1", {}, "Shop #" + id),
        Array.isArray(list) && list.length ? el("div", { class: "grid" }, list.map(card)) : el("div", { class: "state" }, "This shop has no products yet."));
    } catch (e) { app.replaceChildren(el("h1", {}, "Shop #" + id), errorState(e, load)); }
  }
  load();
})();
