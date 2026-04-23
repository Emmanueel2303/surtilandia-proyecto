(function () {
  const CART_KEY = "surtilandia-cart-v1";
  const productMap = window.SURTI_PRODUCT_MAP || {};

  function readCart() {
    try {
      return JSON.parse(window.localStorage.getItem(CART_KEY) || "{}");
    } catch (error) {
      return {};
    }
  }

  function writeCart(cart) {
    window.localStorage.setItem(CART_KEY, JSON.stringify(cart));
    syncCartCount();
  }

  function syncCartCount() {
    const cart = readCart();
    const totalItems = Object.values(cart).reduce((sum, quantity) => sum + quantity, 0);
    document.querySelectorAll("[data-cart-count]").forEach((node) => {
      node.textContent = String(totalItems);
    });
  }

  function addToCart(button) {
    const cart = readCart();
    const productId = button.dataset.productId;
    cart[productId] = (cart[productId] || 0) + 1;
    writeCart(cart);
    button.textContent = "Agregado";
    window.setTimeout(() => {
      button.textContent = "Agregar";
    }, 900);
  }

  function buildCartItems() {
    const cart = readCart();
    return Object.entries(cart)
      .map(([productId, quantity]) => {
        const product = productMap[productId];
        if (!product) return null;
        return {
          productId,
          quantity,
          product,
          subtotal: product.price * quantity,
        };
      })
      .filter(Boolean);
  }

  function formatCurrency(value) {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    })
      .format(value)
      .replace("COP", "")
      .trim();
  }

  function renderCartPage() {
    const root = document.querySelector("[data-cart-root]");
    const summary = document.querySelector("[data-cart-summary]");
    if (!root || !summary) return;

    const items = buildCartItems();
    if (!items.length) {
      root.innerHTML = '<div class="empty-state">Tu seleccion esta vacia. Agrega referencias desde la vitrina.</div>';
      summary.innerHTML = "<h2>Resumen</h2><p>Sin referencias seleccionadas.</p>";
      return;
    }

    const total = items.reduce((sum, item) => sum + item.subtotal, 0);
    root.innerHTML = items
      .map(
        (item) => `
          <article class="cart-item">
            <img src="${item.product.primary_image}" alt="${item.product.name}" />
            <div>
              <h2>${item.product.name}</h2>
              <p>${item.quantity} x ${formatCurrency(item.product.price)}</p>
            </div>
            <strong>${formatCurrency(item.subtotal)}</strong>
          </article>
        `
      )
      .join("");

    summary.innerHTML = `
      <h2>Resumen</h2>
      <p>${items.length} referencia(s)</p>
      <strong class="summary-total">${formatCurrency(total)}</strong>
      <a class="button button--primary" href="/checkout">Continuar solicitud</a>
    `;
  }

  function renderCheckoutPage() {
    const summaryRoot = document.querySelector("[data-checkout-summary]");
    const itemsField = document.querySelector("[data-checkout-items]");
    const form = document.querySelector("[data-checkout-form]");
    if (!summaryRoot || !itemsField || !form) return;

    const items = buildCartItems();
    if (!items.length) {
      summaryRoot.innerHTML = '<div class="empty-state">No hay referencias en tu seleccion.</div>';
      form.querySelector('button[type="submit"]').disabled = true;
      return;
    }

    const payload = items.map((item) => ({
      product_id: Number(item.productId),
      quantity: item.quantity,
    }));
    itemsField.value = JSON.stringify(payload);

    const total = items.reduce((sum, item) => sum + item.subtotal, 0);
    summaryRoot.innerHTML = `
      <div class="checkout-items">
        ${items
          .map(
            (item) => `
            <article class="cart-item">
              <img src="${item.product.primary_image}" alt="${item.product.name}" />
              <div>
                <h2>${item.product.name}</h2>
                <p>${item.quantity} x ${formatCurrency(item.product.price)}</p>
              </div>
              <strong>${formatCurrency(item.subtotal)}</strong>
            </article>
          `
          )
          .join("")}
      </div>
      <div class="summary-total">${formatCurrency(total)}</div>
    `;

    form.addEventListener("submit", () => {
      window.localStorage.removeItem(CART_KEY);
    });
  }

  document.querySelectorAll("[data-add-to-cart]").forEach((button) => {
    button.addEventListener("click", () => addToCart(button));
  });

  syncCartCount();
  renderCartPage();
  renderCheckoutPage();
})();
