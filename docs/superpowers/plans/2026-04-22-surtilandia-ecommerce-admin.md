# Surtilandia Ecommerce Admin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the current static Surtilandia landing page into a functional ecommerce demo with a public storefront, guest checkout, order tracking, and an authenticated admin panel backed by a central SQLite database.

**Architecture:** Use a single Flask application with server-rendered templates, modular route files, SQLite persistence, and a small service layer for catalog, checkout, admin auth, reporting, and file uploads. Preserve Surtilandia’s bright storefront language for the public site and use a utility-focused admin surface with shared design tokens.

**Tech Stack:** Python 3.12, Flask, SQLite, unittest, vanilla JavaScript, CSS, local file uploads.

---

### Task 1: Scaffold the Flask app and database foundation

**Files:**
- Create: `requirements.txt`
- Create: `app.py`
- Create: `surtilandia/__init__.py`
- Create: `surtilandia/config.py`
- Create: `surtilandia/db.py`
- Create: `surtilandia/schema.sql`
- Create: `tests/test_app_boot.py`

- [ ] **Step 1: Write the failing boot test**

```python
import unittest

from surtilandia import create_app


class AppBootTests(unittest.TestCase):
    def test_home_route_responds(self):
        app = create_app({"TESTING": True, "DATABASE_PATH": ":memory:"})
        client = app.test_client()

        response = client.get("/")

        self.assertEqual(response.status_code, 200)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_app_boot -v`
Expected: FAIL because `surtilandia` package and `create_app` do not exist yet.

- [ ] **Step 3: Write minimal app factory and database bootstrap**

```python
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="change-me",
        DATABASE_PATH="data/surtilandia.sqlite3",
    )

    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def home():
        return "Surtilandia"

    return app
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_app_boot -v`
Expected: PASS

- [ ] **Step 5: Expand the database layer with schema and helpers**

```python
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    reference TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price INTEGER NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    short_description TEXT NOT NULL,
    details TEXT NOT NULL,
    primary_image TEXT,
    gallery_json TEXT NOT NULL DEFAULT '[]',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

- [ ] **Step 6: Commit**

```bash
git add requirements.txt app.py surtilandia/__init__.py surtilandia/config.py surtilandia/db.py surtilandia/schema.sql tests/test_app_boot.py
git commit -m "feat: scaffold flask storefront foundation"
```

### Task 2: Build the public storefront, cart, checkout, and tracking

**Files:**
- Create: `surtilandia/store.py`
- Create: `surtilandia/services/catalog.py`
- Create: `surtilandia/services/orders.py`
- Create: `surtilandia/templates/base.html`
- Create: `surtilandia/templates/store/home.html`
- Create: `surtilandia/templates/store/product.html`
- Create: `surtilandia/templates/store/cart.html`
- Create: `surtilandia/templates/store/checkout.html`
- Create: `surtilandia/templates/store/order_success.html`
- Create: `surtilandia/templates/store/track_order.html`
- Create: `surtilandia/static/css/site.css`
- Create: `surtilandia/static/js/store.js`
- Create: `tests/test_checkout_flow.py`

- [ ] **Step 1: Write the failing checkout test**

```python
import unittest

from surtilandia import create_app
from surtilandia.db import init_db, seed_demo_data


class CheckoutFlowTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "DATABASE_PATH": "test-checkout.sqlite3"})
        with self.app.app_context():
            init_db()
            seed_demo_data()
        self.client = self.app.test_client()

    def test_guest_checkout_creates_order_and_reduces_stock(self):
        response = self.client.post(
            "/checkout",
            data={
                "full_name": "Ana Gomez",
                "phone": "3001234567",
                "email": "ana@example.com",
                "city": "Bogota",
                "address": "Calle 10 # 20-30",
                "payment_method": "cash_on_delivery",
                "items": "1:2",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/pedido/", response.headers["Location"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_checkout_flow -v`
Expected: FAIL because checkout route and order service do not exist yet.

- [ ] **Step 3: Implement the public routes and order service**

```python
@store_bp.post("/checkout")
def checkout_submit():
    order_id = create_guest_order(request.form, session_cart)
    session["cart"] = {}
    return redirect(url_for("store.order_success", public_order_id=order_id))
```

- [ ] **Step 4: Run tests to verify checkout passes**

Run: `python -m unittest tests.test_checkout_flow -v`
Expected: PASS

- [ ] **Step 5: Implement storefront templates and assets**

```html
<section class="catalog-grid">
  {% for product in products %}
    <article class="product-tile">
      <a href="{{ url_for('store.product_detail', slug=product['slug']) }}">{{ product["name"] }}</a>
      <p>{{ product["short_description"] }}</p>
      <strong>{{ product["price_display"] }}</strong>
    </article>
  {% endfor %}
</section>
```

- [ ] **Step 6: Commit**

```bash
git add surtilandia/store.py surtilandia/services/catalog.py surtilandia/services/orders.py surtilandia/templates surtilandia/static/css/site.css surtilandia/static/js/store.js tests/test_checkout_flow.py
git commit -m "feat: add storefront checkout and order tracking"
```

### Task 3: Build admin authentication, product management, and order operations

**Files:**
- Create: `surtilandia/admin.py`
- Create: `surtilandia/services/admin_auth.py`
- Create: `surtilandia/services/reports.py`
- Create: `surtilandia/templates/admin/login.html`
- Create: `surtilandia/templates/admin/dashboard.html`
- Create: `surtilandia/templates/admin/products.html`
- Create: `surtilandia/templates/admin/product_form.html`
- Create: `surtilandia/templates/admin/orders.html`
- Create: `surtilandia/templates/admin/order_detail.html`
- Create: `surtilandia/templates/admin/customers.html`
- Create: `surtilandia/static/css/admin.css`
- Create: `tests/test_admin_auth.py`
- Create: `tests/test_admin_orders.py`

- [ ] **Step 1: Write the failing admin auth test**

```python
import unittest

from surtilandia import create_app


class AdminAuthTests(unittest.TestCase):
    def test_admin_requires_login(self):
        app = create_app({"TESTING": True, "DATABASE_PATH": "test-admin.sqlite3"})
        client = app.test_client()

        response = client.get("/admin", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_admin_auth -v`
Expected: FAIL because admin routes and auth guard do not exist yet.

- [ ] **Step 3: Implement login, session guard, dashboard, and CRUD pages**

```python
@admin_bp.before_request
def require_admin_login():
    if request.endpoint in {"admin.login", "admin.login_submit"}:
        return None
    if not session.get("is_admin_authenticated"):
        return redirect(url_for("admin.login"))
```

- [ ] **Step 4: Add failing order status update test**

```python
def test_admin_can_move_order_to_enviado(self):
    response = self.client.post(f"/admin/orders/{self.public_order_id}/status", data={"status": "Enviado"})
    self.assertEqual(response.status_code, 302)
```

- [ ] **Step 5: Implement admin order updates, customer list, and reports**

```python
def update_order_status(public_order_id: str, status: str, note: str = ""):
    db.execute(
        "UPDATE orders SET status = ?, updated_at = ? WHERE public_order_id = ?",
        (status, now_iso(), public_order_id),
    )
```

- [ ] **Step 6: Run admin tests to verify they pass**

Run: `python -m unittest tests.test_admin_auth tests.test_admin_orders -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add surtilandia/admin.py surtilandia/services/admin_auth.py surtilandia/services/reports.py surtilandia/templates/admin surtilandia/static/css/admin.css tests/test_admin_auth.py tests/test_admin_orders.py
git commit -m "feat: add admin panel for products and orders"
```

### Task 4: Add uploads, demo credentials, polish, and end-to-end verification

**Files:**
- Modify: `surtilandia/config.py`
- Modify: `surtilandia/db.py`
- Modify: `surtilandia/admin.py`
- Modify: `surtilandia/templates/admin/product_form.html`
- Modify: `surtilandia/templates/store/home.html`
- Create: `surtilandia/static/uploads/.gitkeep`
- Create: `tests/test_reports.py`
- Create: `README.md`

- [ ] **Step 1: Write the failing reports test**

```python
import unittest

from surtilandia.services.reports import summarize_dashboard


class ReportsTests(unittest.TestCase):
    def test_dashboard_summary_exposes_kpis(self):
        summary = summarize_dashboard()
        self.assertIn("total_orders", summary)
        self.assertIn("total_sales", summary)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_reports -v`
Expected: FAIL because reporting service is incomplete.

- [ ] **Step 3: Implement uploads, seed credentials, and reporting polish**

```python
app.config.from_mapping(
    ADMIN_USERNAME="surtiadmin",
    ADMIN_PASSWORD="SurtiDemo2026!",
    UPLOAD_FOLDER="surtilandia/static/uploads",
)
```

- [ ] **Step 4: Run the full verification suite**

Run: `python -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 5: Run the app manually for smoke verification**

Run: `python app.py`
Expected: Flask dev server starts and exposes storefront plus `/admin/login`.

- [ ] **Step 6: Commit**

```bash
git add surtilandia/config.py surtilandia/db.py surtilandia/admin.py surtilandia/templates/admin/product_form.html surtilandia/templates/store/home.html surtilandia/static/uploads/.gitkeep tests/test_reports.py README.md
git commit -m "feat: polish ecommerce demo and admin setup"
```
