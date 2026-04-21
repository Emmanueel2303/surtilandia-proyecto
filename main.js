const products = [
  {
    name: "Audifonos Bluetooth Premium",
    category: "Tecnologia",
    city: "Bogota",
    price: 54900,
    oldPrice: 79900,
    badge: "Top",
    stock: "Disponible",
    featured: 1,
    seller: "Surtilandia Tech",
    delivery: "Entrega 24 a 48 horas",
    image:
      "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Organizador modular para cocina",
    category: "Hogar",
    city: "Medellin",
    price: 39900,
    oldPrice: 52900,
    badge: "Flash",
    stock: "Ultimas unidades",
    featured: 2,
    seller: "Casa Surtilandia",
    delivery: "Despacho nacional",
    image:
      "https://images.unsplash.com/photo-1586208958839-06c17cacdf08?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Kit skincare de rutina diaria",
    category: "Belleza",
    city: "Cali",
    price: 29900,
    oldPrice: 44900,
    badge: "Nuevo",
    stock: "Disponible",
    featured: 3,
    seller: "Beauty Aliado",
    delivery: "Listo para envio",
    image:
      "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Set de cuchillos con soporte",
    category: "Cocina",
    city: "Barranquilla",
    price: 64900,
    oldPrice: 89900,
    badge: "Combo",
    stock: "Disponible",
    featured: 4,
    seller: "Cocina Practica",
    delivery: "Entrega en ciudades principales",
    image:
      "https://images.unsplash.com/photo-1593618998160-2d03ea5f2e72?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Blusa casual para vitrina social",
    category: "Moda",
    city: "Bogota",
    price: 46900,
    oldPrice: 63900,
    badge: "Top",
    stock: "Disponible",
    featured: 5,
    seller: "Moda Surti",
    delivery: "Disponible por pedido",
    image:
      "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Pizarra magica infantil reutilizable",
    category: "Infantil",
    city: "Medellin",
    price: 25900,
    oldPrice: 34900,
    badge: "Nuevo",
    stock: "Disponible",
    featured: 6,
    seller: "Kids Market",
    delivery: "Salida inmediata",
    image:
      "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Cama acolchada para mascota",
    category: "Mascotas",
    city: "Cali",
    price: 58900,
    oldPrice: 73900,
    badge: "Flash",
    stock: "Disponible",
    featured: 7,
    seller: "Pet Surti",
    delivery: "Cobertura nacional",
    image:
      "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Lampara LED recargable de escritorio",
    category: "Tecnologia",
    city: "Bogota",
    price: 34900,
    oldPrice: 45900,
    badge: "Combo",
    stock: "Disponible",
    featured: 8,
    seller: "Ilumina Hogar",
    delivery: "Entrega rapida",
    image:
      "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=900&q=80",
  },
];

const state = {
  search: "",
  category: "Todos",
  city: "Todas",
  sort: "featured",
};

const grid = document.getElementById("productGrid");
const resultsCount = document.getElementById("resultsCount");
const catalogSearch = document.getElementById("catalogSearch");
const heroSearch = document.getElementById("heroSearch");
const heroSearchInput = document.getElementById("hero-search-input");
const cityFilter = document.getElementById("cityFilter");
const sortFilter = document.getElementById("sortFilter");
const clearFiltersButton = document.getElementById("clearFilters");
const filterPills = document.querySelectorAll(".filter-pill");
const navChips = document.querySelectorAll(".nav-chip");
const categoryTargets = document.querySelectorAll("[data-category-target]");
const heroShowcase = document.querySelector(".hero-showcase");
const tiltSelector = [
  ".showcase-card",
  ".product-card",
  ".timeline-card",
  ".story-stat",
  ".signature-panel",
  ".audience-card",
  ".journey-card",
  ".community-panel",
  ".trust-point",
  ".signature-chip",
  ".promo-banner__card",
].join(", ");
const supportsMotion = window.matchMedia("(hover: hover) and (pointer: fine)");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
let revealObserver = null;

const currency = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

function formatPrice(value) {
  return currency.format(value).replace("COP", "").trim();
}

function canUseInteractiveMotion() {
  return supportsMotion.matches && !reducedMotion.matches;
}

function applyRevealDelays(scope = document) {
  const items = scope.querySelectorAll("[data-reveal]");

  items.forEach((item, index) => {
    item.style.setProperty("--reveal-delay", `${(index % 4) * 80}ms`);
  });
}

function syncScrollState() {
  const scrollRoot = document.documentElement;
  const maxScroll = scrollRoot.scrollHeight - scrollRoot.clientHeight;
  const progress = maxScroll > 0 ? scrollRoot.scrollTop / maxScroll : 0;

  document.body.classList.toggle("is-scrolled", window.scrollY > 12);
  document.documentElement.style.setProperty("--scroll-progress", progress.toFixed(4));
}

function attachTiltEffects(scope = document) {
  const items = scope.querySelectorAll(tiltSelector);

  items.forEach((item) => {
    if (item.dataset.tiltBound === "true") return;

    item.dataset.tiltBound = "true";
    item.classList.add("has-tilt");

    if (!canUseInteractiveMotion()) return;

    item.addEventListener("pointermove", (event) => {
      const rect = item.getBoundingClientRect();
      const offsetX = (event.clientX - rect.left) / rect.width - 0.5;
      const offsetY = (event.clientY - rect.top) / rect.height - 0.5;
      const rotateY = offsetX * 10;
      const rotateX = offsetY * -10;

      item.classList.add("is-tilting");
      item.style.setProperty("--tilt-x", `${rotateX.toFixed(2)}deg`);
      item.style.setProperty("--tilt-y", `${rotateY.toFixed(2)}deg`);
    });

    const resetTilt = () => {
      item.classList.remove("is-tilting");
      item.style.setProperty("--tilt-x", "0deg");
      item.style.setProperty("--tilt-y", "0deg");
    };

    item.addEventListener("pointerleave", resetTilt);
    item.addEventListener("pointercancel", resetTilt);
  });
}

function initHeroParallax() {
  if (!heroShowcase || !canUseInteractiveMotion()) return;

  const resetHero = () => {
    heroShowcase.style.setProperty("--hero-x", "0");
    heroShowcase.style.setProperty("--hero-y", "0");
  };

  heroShowcase.addEventListener("pointermove", (event) => {
    const rect = heroShowcase.getBoundingClientRect();
    const offsetX = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
    const offsetY = ((event.clientY - rect.top) / rect.height - 0.5) * 2;

    heroShowcase.style.setProperty("--hero-x", offsetX.toFixed(3));
    heroShowcase.style.setProperty("--hero-y", offsetY.toFixed(3));
  });

  heroShowcase.addEventListener("pointerleave", resetHero);
  heroShowcase.addEventListener("pointercancel", resetHero);
}

function ensureRevealObserver() {
  if (!("IntersectionObserver" in window) || revealObserver) return;

  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.18 }
  );
}

function observeReveals(scope = document) {
  applyRevealDelays(scope);

  const items = scope.querySelectorAll("[data-reveal]");

  if (!("IntersectionObserver" in window)) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  ensureRevealObserver();
  items.forEach((item) => {
    if (!item.classList.contains("is-visible")) revealObserver.observe(item);
  });
}

function setCategory(category) {
  state.category = category;

  filterPills.forEach((pill) => {
    pill.classList.toggle("is-active", pill.dataset.category === category);
  });

  navChips.forEach((chip) => {
    chip.classList.toggle("is-active", chip.dataset.category === category);
  });

  renderProducts();
}

function getFilteredProducts() {
  const search = state.search.trim().toLowerCase();

  return [...products]
    .filter((product) => {
      const matchesCategory = state.category === "Todos" || product.category === state.category;
      const matchesCity = state.city === "Todas" || product.city === state.city;
      const matchesSearch =
        search.length === 0 ||
        product.name.toLowerCase().includes(search) ||
        product.category.toLowerCase().includes(search) ||
        product.city.toLowerCase().includes(search) ||
        product.seller.toLowerCase().includes(search);

      return matchesCategory && matchesCity && matchesSearch;
    })
    .sort((a, b) => {
      if (state.sort === "price-asc") return a.price - b.price;
      if (state.sort === "price-desc") return b.price - a.price;
      if (state.sort === "name") return a.name.localeCompare(b.name);
      return a.featured - b.featured;
    });
}

function productCardTemplate(product) {
  return `
    <article class="product-card" data-reveal>
      <div class="product-card__media">
        <img src="${product.image}" alt="${product.name}" loading="lazy" />
        <span class="product-card__badge badge--${product.badge}">${product.badge}</span>
      </div>
      <div class="product-card__body">
        <div class="product-card__eyebrow">
          <span class="product-card__pill">${product.category}</span>
          <span>${product.city}</span>
        </div>
        <h3>${product.name}</h3>
        <p class="product-card__seller">Aliado: ${product.seller}</p>
        <div class="product-card__meta">
          <span>${product.delivery}</span>
          <span>Compra por Instagram</span>
        </div>
        <div class="product-card__price">
          <strong>${formatPrice(product.price)}</strong>
          <span>${formatPrice(product.oldPrice)}</span>
        </div>
        <div class="product-card__footer">
          <span class="product-card__stock">${product.stock}</span>
          <span class="product-card__cta">Pedir ahora</span>
        </div>
      </div>
    </article>
  `;
}

function renderProducts() {
  const filteredProducts = getFilteredProducts();

  if (!filteredProducts.length) {
    grid.innerHTML = `
      <div class="product-empty">
        No encontramos productos con esos filtros. Prueba otra categoria o limpia la busqueda.
      </div>
    `;
  } else {
    grid.innerHTML = filteredProducts.map(productCardTemplate).join("");
  }

  const label = filteredProducts.length === 1 ? "producto" : "productos";
  resultsCount.textContent = `Mostrando ${filteredProducts.length} ${label}`;
  observeReveals(grid);
  attachTiltEffects(grid);
}

heroSearch?.addEventListener("submit", (event) => {
  event.preventDefault();
  state.search = heroSearchInput.value;
  catalogSearch.value = state.search;
  document.getElementById("catalogo").scrollIntoView({ behavior: "smooth", block: "start" });
  renderProducts();
});

catalogSearch?.addEventListener("input", (event) => {
  state.search = event.target.value;
  heroSearchInput.value = event.target.value;
  renderProducts();
});

cityFilter?.addEventListener("change", (event) => {
  state.city = event.target.value;
  renderProducts();
});

sortFilter?.addEventListener("change", (event) => {
  state.sort = event.target.value;
  renderProducts();
});

clearFiltersButton?.addEventListener("click", () => {
  state.search = "";
  state.city = "Todas";
  state.sort = "featured";
  catalogSearch.value = "";
  heroSearchInput.value = "";
  cityFilter.value = "Todas";
  sortFilter.value = "featured";
  setCategory("Todos");
});

filterPills.forEach((pill) => {
  pill.addEventListener("click", () => setCategory(pill.dataset.category));
});

navChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    const category = chip.dataset.category || "Todos";
    setCategory(category);

    if (category !== "Todos") {
      document.getElementById("catalogo").scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
});

categoryTargets.forEach((target) => {
  target.addEventListener("click", () => {
    setCategory(target.dataset.categoryTarget);
    document.getElementById("catalogo").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  target.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      setCategory(target.dataset.categoryTarget);
      document.getElementById("catalogo").scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
});

renderProducts();
observeReveals();
attachTiltEffects();
initHeroParallax();
syncScrollState();

window.addEventListener("scroll", syncScrollState, { passive: true });
window.addEventListener("resize", syncScrollState, { passive: true });
