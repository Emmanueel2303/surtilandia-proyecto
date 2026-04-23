const adminControls = document.querySelectorAll("[data-admin-controls]");

function normalize(value) {
  return (value || "").toString().trim().toLowerCase();
}

function applyAdminFilter(control) {
  const key = control.dataset.adminControls;
  const table = document.querySelector(`[data-admin-table="${key}"]`);
  const empty = document.querySelector(`[data-admin-empty="${key}"]`);
  if (!table) return;

  const rows = [...table.querySelectorAll("[data-admin-row]")];
  const search = normalize(control.querySelector("[data-admin-search]")?.value);
  const status = normalize(control.querySelector("[data-admin-status]")?.value);
  let visibleRows = 0;

  rows.forEach((row) => {
    const searchable = normalize(row.dataset.search);
    const rowStatus = normalize(row.dataset.status);
    const matchesSearch = !search || searchable.includes(search);
    const matchesStatus = !status || rowStatus === status;
    const isVisible = matchesSearch && matchesStatus;

    row.hidden = !isVisible;
    if (isVisible) visibleRows += 1;
  });

  if (empty) empty.hidden = rows.length === 0 || visibleRows > 0;
}

adminControls.forEach((control) => {
  control.addEventListener("input", () => applyAdminFilter(control));
  control.addEventListener("change", () => applyAdminFilter(control));
  applyAdminFilter(control);
});

const adminLogo = document.querySelector(".admin-brand__logo")?.getAttribute("src");

if (adminLogo) {
  document.querySelectorAll(".admin-reference img").forEach((image) => {
    const useFallback = () => {
      if (image.getAttribute("src") === adminLogo) return;
      image.classList.add("is-fallback");
      image.setAttribute("src", adminLogo);
    };

    image.addEventListener("error", useFallback, { once: true });

    if (image.complete && image.naturalWidth === 0) {
      useFallback();
    }
  });
}

requestAnimationFrame(() => {
  document.body.classList.add("admin-ready");
});

const canUsePointerMotion =
  window.matchMedia("(hover: hover) and (pointer: fine)").matches &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (canUsePointerMotion) {
  let frame = null;
  let nextX = 0;
  let nextY = 0;

  window.addEventListener(
    "pointermove",
    (event) => {
      nextX = (event.clientX / window.innerWidth - 0.5) * 2;
      nextY = (event.clientY / window.innerHeight - 0.5) * 2;

      if (frame) return;
      frame = requestAnimationFrame(() => {
        document.documentElement.style.setProperty("--admin-cursor-x", nextX.toFixed(3));
        document.documentElement.style.setProperty("--admin-cursor-y", nextY.toFixed(3));
        frame = null;
      });
    },
    { passive: true }
  );
}
