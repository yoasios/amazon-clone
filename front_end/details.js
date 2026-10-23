(function () {
  renderHeader();
  const p = new URLSearchParams(location.search);
  const id = parseInt(p.get("id"), 10), shop = parseInt(p.get("shop"), 10), app = $("#app");

  function render(pr) {
    document.title = pr.product_name;
    const out = pr.amount <= 0;
    const qty = el("input", { class: "qty", id: "qty", type: "number", min: 1, max: Math.max(1, pr.amount), value: 1, disabled: out });
    const add = el("button", {
      class: "btn", type: "button", disabled: out,
      onclick: () => {
        const n = Math.max(1, Math.min(parseInt(qty.value, 10) || 1, pr.amount));
        let added = 0, res;
        for (let i = 0; i < n; i++) {
          res = Cart.add({ product_id: pr.product_id, product_name: pr.product_name, product_price: pr.product_price,
            shop_id: pr.shop_id, shop_name: "Shop #" + pr.shop_id, stock: pr.amount });
          if (!res.ok) break;
          added++;
        }
        toast(added ? "Added " + added + " to cart" : res.message, added ? "ok" : "error");
      },
    }, out ? "Out of stock" : "Add to cart");
    app.replaceChildren(el("div", { class: "detail" }, tile(pr.product_name),
      el("div", {},
        el("h1", {}, pr.product_name),
        el("p", { class: "price" }, money(pr.product_price)),
        el("p", { class: "stock" + (out || pr.amount <= 5 ? " low" : "") }, out ? "Unavailable" : pr.amount <= 5 ? "Only " + pr.amount + " left" : pr.amount + " in stock"),
        el("p", { class: "desc" }, pr.product_description),
        el("p", { class: "note" }, "Sold by ", el("a", { href: "shop.html?id=" + encodeURIComponent(pr.shop_id) }, "Shop #" + pr.shop_id),
          pr.created_at ? ". Listed " + fmtDate(pr.created_at) + "." : ""),
        el("div", { class: "buy" }, el("label", { for: "qty" }, "Quantity"), qty, add))));
  }

  async function load() {
    if (!id || !shop) { app.replaceChildren(el("div", { class: "state error" }, "This product link is incomplete. Find the product from the catalog.")); return; }
    app.replaceChildren(el("div", { class: "state" }, "Loading product…"));
    try {
      const list = await Api.viewShop(shop); // the API has no get-product-by-ID; the shop list is the source
      const pr = (Array.isArray(list) ? list : []).find((x) => x.product_id === id);
      if (!pr) app.replaceChildren(el("div", { class: "state" }, "This product is no longer listed. ", el("a", { href: "index.html" }, "Back to the catalog")));
      else render(pr);
    } catch (e) { app.replaceChildren(errorState(e, load)); }
  }
  load();
})();
