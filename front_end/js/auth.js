const Auth = {
  get() {
    try { const s = JSON.parse(localStorage.getItem(SESSION_KEY)); if (s && Date.now() - s.at < SESSION_MS) return s; } catch {}
    localStorage.removeItem(SESSION_KEY);
    return null;
  },
  set(email) { localStorage.setItem(SESSION_KEY, JSON.stringify({ email, at: Date.now() })); },
  clear() { localStorage.removeItem(SESSION_KEY); },
  requireLogin() {
    if (Auth.get()) return true;
    const here = location.pathname.split("/").pop() + location.search;
    location.replace("login.html?next=" + encodeURIComponent(here));
    return false;
  },
  async logout() {
    try { await Api.logout(); }
    catch (e) {
      toast(e.status === 404 ? "The backend has no POST /logout yet (see BACKEND_CHANGES.md). You are still signed in." : e.message, "error");
      return;
    }
    Auth.clear(); Cart.clear();
    location.href = "login.html";
  },
};

function nextUrl() {
  const n = new URLSearchParams(location.search).get("next");
  return n && /^[\w.\-]+\.html(\?.*)?$/.test(n) ? n : "index.html"; // same-site pages only
}

function bindForm(form, fn) {
  const btn = form.querySelector("button[type=submit]"), err = form.querySelector(".form-error");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    err.textContent = "";
    if (!form.reportValidity()) return;
    setBusy(btn, true);
    try { await fn(Object.fromEntries(new FormData(form))); }
    catch (x) { err.textContent = x.message; }
    finally { setBusy(btn, false); }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const login = $("#login-form"), reg = $("#register-form");
  if (login) bindForm(login, async (d) => {
    const email = d.email.trim();
    const r = await Api.login({ email, password: d.password });
    // "Already logged in" ignores the submitted credentials and returns the cookie's user.
    const other = r.email && r.email.toLowerCase() !== email.toLowerCase();
    Auth.set(r.email || email);
    if (other) {
      renderHeader();
      throw new Error("Another account (" + r.email + ") is already signed in in this browser, so your credentials were not used. Use Sign out, then sign in again.");
    }
    location.href = nextUrl();
  });
  if (reg) bindForm(reg, async (d) => {
    const body = { name: d.name.trim(), email: d.email.trim(), password: d.password, phone: d.phone.trim(), address: d.address.trim() };
    await Api.signin(body); // backend sets access_token; the user is signed in immediately
    Auth.set(body.email);
    location.href = "index.html";
  });
});
