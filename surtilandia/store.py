import json
from pathlib import Path

from flask import Blueprint, abort, current_app, redirect, render_template, request, send_from_directory, url_for

from .db import init_db, seed_demo_data
from .services.catalog import get_product_by_slug, list_active_products
from .services.orders import create_guest_order, get_order_by_public_id

store_bp = Blueprint("store", __name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@store_bp.before_app_request
def ensure_database_ready():
    init_db()
    seed_demo_data()


@store_bp.get("/")
def home():
    products = list_active_products()
    legacy_html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
    legacy_html = legacy_html.replace('./styles.css', url_for("store.legacy_asset", filename="styles.css"))
    legacy_html = legacy_html.replace(
        '<script src="./main.js"></script>',
        (
            f"<script>window.SURTI_PRODUCTS = {json.dumps(_build_legacy_products(products), ensure_ascii=False)};</script>\n"
            f'<script src="{url_for("store.legacy_asset", filename="main.js")}"></script>'
        ),
    )
    return current_app.response_class(legacy_html, mimetype="text/html")


@store_bp.get("/legacy/<path:filename>")
def legacy_asset(filename):
    if filename not in {"styles.css", "main.js"}:
        abort(404)
    return send_from_directory(PROJECT_ROOT, filename)


@store_bp.get("/producto/<slug>")
def product_detail(slug):
    product = get_product_by_slug(slug)
    if product is None:
        abort(404)

    return render_template(
        "store/product.html",
        product=product,
        product_map_json=json.dumps({str(product["id"]): product}),
    )


@store_bp.get("/carrito")
def cart():
    products = list_active_products()
    return render_template(
        "store/cart.html",
        products=products,
        product_map_json=json.dumps({str(product["id"]): product for product in products}),
    )


@store_bp.get("/checkout")
def checkout():
    products = list_active_products()
    return render_template(
        "store/checkout.html",
        products=products,
        product_map_json=json.dumps({str(product["id"]): product for product in products}),
    )


@store_bp.post("/checkout")
def checkout_submit():
    public_order_id = create_guest_order(request.form)
    return redirect(url_for("store.order_success", public_order_id=public_order_id))


@store_bp.get("/pedido/<public_order_id>")
def order_success(public_order_id):
    payload = get_order_by_public_id(public_order_id)
    if payload is None:
        abort(404)

    return render_template("store/order_success.html", payload=payload)


@store_bp.get("/seguimiento")
def track_order():
    public_order_id = request.args.get("order_id", "").strip()
    payload = get_order_by_public_id(public_order_id) if public_order_id else None
    not_found = bool(public_order_id) and payload is None
    return render_template(
        "store/track_order.html",
        payload=payload,
        order_id=public_order_id,
        not_found=not_found,
    )


def _build_legacy_products(products):
    badges = ["Top", "Flash", "Nuevo", "Combo"]
    cities = ["Bogota", "Medellin", "Cali", "Barranquilla"]
    deliveries = [
        "Entrega 24 a 48 horas",
        "Despacho nacional",
        "Listo para envio",
        "Entrega en ciudades principales",
    ]

    legacy_products = []
    for index, product in enumerate(products, start=1):
        old_price = int(round(product["price"] * 1.35 / 100.0) * 100)
        stock_label = "Disponible" if product["stock"] > 6 else "Ultimas unidades"
        legacy_products.append(
            {
                "name": product["name"],
                "category": product["category"],
                "city": cities[(index - 1) % len(cities)],
                "price": product["price"],
                "oldPrice": old_price,
                "badge": badges[(index - 1) % len(badges)],
                "stock": stock_label,
                "featured": index,
                "seller": "Surtilandia",
                "delivery": deliveries[(index - 1) % len(deliveries)],
                "image": product["primary_image"],
                "detailUrl": url_for("store.product_detail", slug=product["slug"]),
            }
        )

    return legacy_products
