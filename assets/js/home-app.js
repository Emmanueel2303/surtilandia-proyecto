const categoryAssets = {
  Tecnologia: "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
  Hogar: "https://images.unsplash.com/photo-1586208958839-06c17cacdf08?auto=format&fit=crop&w=800&q=80",
  Belleza: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
  Cocina: "https://images.unsplash.com/photo-1593618998160-2d03ea5f2e72?auto=format&fit=crop&w=800&q=80",
  Moda: "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80",
  Infantil: "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?auto=format&fit=crop&w=800&q=80",
  Mascotas: "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?auto=format&fit=crop&w=800&q=80",
};

const state = {
  category: "Todos",
  search: "",
};

const currency = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

let products = [];
let revealObserver = null;

function formatPrice(value) {
  return currency.format(value || 0).replace("COP", "").trim();
}

function normalize(value) {
  return (value || "").toString().trim().toLowerCase();
}

function escapeHTML(value) {
  return (value || "").toString().replace(/[&<>"']/g, (character) => {
    const replacements = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };

    return replacements[character];
  });
}

function initIntro(prefersReducedMotion) {
  if (prefersReducedMotion) {
    document.body.classList.remove("is-loading");
    document.body.classList.add("is-products-ready");
    return;
  }

  window.setTimeout(() => {
    document.body.classList.remove("is-loading");
  }, 2850);

  window.setTimeout(() => {
    document.body.classList.add("is-products-ready");
  }, 3450);
}

function syncScrollState() {
  const root = document.documentElement;
  const maxScroll = root.scrollHeight - root.clientHeight;
  const progress = maxScroll > 0 ? root.scrollTop / maxScroll : 0;
  root.style.setProperty("--progress", progress.toFixed(4));
  root.style.setProperty("--scroll-shift", Math.min(progress * 16, 12).toFixed(3));
}

function setupRevealObserver(prefersReducedMotion) {
  const revealItems = [...document.querySelectorAll("[data-reveal]")];

  revealItems.forEach((item, index) => {
    item.style.setProperty("--delay", `${Math.min(index % 5, 4) * 70}ms`);
  });

  if (!("IntersectionObserver" in window) || prefersReducedMotion) {
    revealItems.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -10% 0px", threshold: 0.16 }
  );

  revealItems.forEach((item) => revealObserver.observe(item));
}

function observeNewRevealItems(scope) {
  const items = [...scope.querySelectorAll("[data-reveal]")];
  items.forEach((item, index) => {
    item.style.setProperty("--delay", `${Math.min(index % 8, 7) * 80}ms`);

    if (revealObserver) {
      revealObserver.observe(item);
    } else {
      item.classList.add("is-visible");
    }
  });
}

function getCategories() {
  const categories = [...new Set(products.map((product) => product.category).filter(Boolean))];
  return categories.length ? categories : Object.keys(categoryAssets);
}

function renderCategories() {
  const track = document.getElementById("categoryTrack");
  if (!track) return;

  track.innerHTML = getCategories()
    .map((category) => {
      const image = categoryAssets[category] || categoryAssets.Tecnologia;
      return `
        <button class="category-card" type="button" data-category-target="${escapeHTML(category)}">
          <img src="${image}" alt="" loading="lazy" />
          <span>Linea</span>
          <strong>${escapeHTML(category)}</strong>
        </button>
      `;
    })
    .join("");
}

function syncActiveCategory() {
  document.querySelectorAll(".filter-pill").forEach((pill) => {
    pill.classList.toggle("is-active", pill.dataset.category === state.category);
  });
}

function getFilteredProducts() {
  const search = normalize(state.search);

  return [...products]
    .filter((product) => {
      const matchesCategory = state.category === "Todos" || product.category === state.category;
      const searchable = [
        product.name,
        product.category,
        product.city,
        product.seller,
        product.delivery,
      ].map(normalize).join(" ");

      return matchesCategory && (!search || searchable.includes(search));
    })
    .sort((a, b) => (a.featured || 0) - (b.featured || 0));
}

function productCardTemplate(product, index) {
  const detailUrl = product.detailUrl || "#";
  const oldPrice = product.oldPrice || Math.round((product.price || 0) * 1.35 / 100) * 100;
  const badge = product.badge || "Nuevo";

  return `
    <article class="product-card" style="--delay: ${index * 85}ms">
      <a class="product-card__media" href="${detailUrl}">
        <img src="${escapeHTML(product.image)}" alt="${escapeHTML(product.name)}" loading="lazy" />
        <span class="product-card__badge">${escapeHTML(badge)}</span>
        <span class="product-card__heart" aria-hidden="true">+</span>
      </a>
      <div class="product-card__body">
        <div class="product-card__line">
          <h3>${escapeHTML(product.name)}</h3>
          <strong>${formatPrice(product.price)}</strong>
        </div>
        <div class="product-card__meta">
          <span>${escapeHTML(product.category || "Surtilandia")}</span>
          <span>${escapeHTML(product.city || "Marca oficial")}</span>
        </div>
        <div class="product-card__footer">
          <span class="product-card__stars">5.0 Surtilandia</span>
          <span>${formatPrice(oldPrice)}</span>
        </div>
        <a class="product-card__cta" href="${detailUrl}">Ver detalle</a>
      </div>
    </article>
  `;
}

function attachImageFallbacks(scope = document) {
  scope.querySelectorAll("img").forEach((image) => {
    if (image.dataset.fallbackBound === "true") return;
    image.dataset.fallbackBound = "true";

    const useFallback = () => {
      if (image.src.includes("surtilandia-logo.jpg")) return;
      image.classList.add("is-fallback");
      image.src = "/static/uploads/surtilandia-logo.jpg";
    };

    image.addEventListener("error", useFallback, { once: true });

    if (image.complete && image.naturalWidth === 0) {
      useFallback();
    }
  });
}

function renderProducts() {
  const grid = document.getElementById("productGrid");
  const resultsCount = document.getElementById("resultsCount");
  if (!grid) return;

  const filtered = getFilteredProducts();

  if (!filtered.length) {
    grid.innerHTML = `
      <div class="product-empty">
        No encontramos referencias con esos filtros. Prueba otra linea de Surtilandia.
      </div>
    `;
  } else {
    grid.innerHTML = filtered.map(productCardTemplate).join("");
  }

  const label = filtered.length === 1 ? "referencia" : "referencias";
  if (resultsCount) {
    resultsCount.textContent = `Mostrando ${filtered.length} ${label}`;
  }

  attachImageFallbacks(grid);
}

function renderFocus() {
  const thumbs = document.getElementById("focusThumbs");
  if (!thumbs) return;

  const visible = products.slice(0, 4);
  thumbs.innerHTML = visible
    .map((product, index) => `
      <button class="focus-thumb" type="button" data-focus-index="${index}" aria-label="${escapeHTML(product.name)}">
        <img src="${escapeHTML(product.image)}" alt="" loading="lazy" />
      </button>
    `)
    .join("");

  thumbs.addEventListener("click", (event) => {
    const button = event.target.closest("[data-focus-index]");
    if (!button) return;
    const product = visible[Number(button.dataset.focusIndex)];
    if (!product) return;

    document.getElementById("focusTitle").textContent = product.name;
    document.getElementById("focusText").textContent = `${product.category} dentro de la vitrina oficial Surtilandia, con valor ${formatPrice(product.price)} y contenido propio de marca.`;

    const image = document.querySelector(".focus-gallery__main img");
    if (image) {
      image.src = product.image;
      image.alt = product.name;
    }
  });

  attachImageFallbacks(thumbs);
}

function setCategory(category) {
  state.category = category || "Todos";
  syncActiveCategory();
  document.body.classList.remove("is-products-ready");
  window.setTimeout(() => {
    renderProducts();
    document.body.classList.add("is-products-ready");
  }, 420);
}

function initFilters() {
  document.addEventListener("click", (event) => {
    const filter = event.target.closest(".filter-pill");
    if (filter) {
      setCategory(filter.dataset.category);
      return;
    }

    const categoryTarget = event.target.closest("[data-category-target]");
    if (categoryTarget) {
      setCategory(categoryTarget.dataset.categoryTarget || "Todos");
      document.getElementById("vitrina")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });

  const heroSearch = document.getElementById("heroSearch");
  const heroSearchInput = document.getElementById("hero-search-input");

  heroSearch?.addEventListener("submit", (event) => {
    event.preventDefault();
    state.search = heroSearchInput?.value || "";
    renderProducts();
    document.getElementById("vitrina")?.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  heroSearchInput?.addEventListener("input", (event) => {
    state.search = event.target.value;
    renderProducts();
  });
}

function initMegaMenu(prefersReducedMotion) {
  const menu = document.querySelector("[data-category-menu]");
  const toggle = document.querySelector("[data-category-toggle]");
  if (!menu || !toggle) return;

  const openMenu = () => menu.classList.add("is-open");
  const closeMenu = () => menu.classList.remove("is-open");
  const closePreview = () => {
    menu.classList.remove("is-open");
    menu.classList.remove("is-preview");
  };

  toggle.addEventListener("click", () => {
    menu.classList.remove("is-preview");
    menu.classList.toggle("is-open");
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-category-menu]") || event.target.closest("[data-category-toggle]")) return;
    closeMenu();
  });

  window.setTimeout(() => {
    menu.classList.add("is-preview");
    openMenu();
  }, prefersReducedMotion ? 400 : 3300);
  window.setTimeout(closePreview, 7600);
}

function initPointerMotion(prefersReducedMotion) {
  const hero = document.querySelector("[data-hero]");
  const canUsePointerMotion = window.matchMedia("(hover: hover) and (pointer: fine)").matches && !prefersReducedMotion;
  if (!hero || !canUsePointerMotion) return;

  let frame = null;
  let nextX = 0;
  let nextY = 0;

  hero.addEventListener(
    "pointermove",
    (event) => {
      const rect = hero.getBoundingClientRect();
      nextX = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
      nextY = ((event.clientY - rect.top) / rect.height - 0.5) * 2;

      if (frame) return;
      frame = requestAnimationFrame(() => {
        document.documentElement.style.setProperty("--mouse-x", nextX.toFixed(3));
        document.documentElement.style.setProperty("--mouse-y", nextY.toFixed(3));
        frame = null;
      });
    },
    { passive: true }
  );

  hero.addEventListener("pointerleave", () => {
    document.documentElement.style.setProperty("--mouse-x", "0");
    document.documentElement.style.setProperty("--mouse-y", "0");
  });
}

export function initSurtilandiaHome(homeProducts) {
  products = Array.isArray(homeProducts) && homeProducts.length ? homeProducts : [];

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  renderCategories();
  renderProducts();
  renderFocus();
  setupRevealObserver(prefersReducedMotion);
  initIntro(prefersReducedMotion);
  initFilters();
  initMegaMenu(prefersReducedMotion);
  initPointerMotion(prefersReducedMotion);
  syncActiveCategory();
  syncScrollState();
  attachImageFallbacks();

  window.addEventListener("scroll", syncScrollState, { passive: true });
  window.addEventListener("resize", syncScrollState, { passive: true });
}
