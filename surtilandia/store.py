import json

from flask import Blueprint, abort, redirect, render_template, request, url_for

from .db import get_db, init_db, seed_demo_data
from .services.catalog import get_product_by_slug, list_active_products
from .services.orders import create_guest_order, get_order_by_public_id

store_bp = Blueprint("store", __name__)


@store_bp.before_app_request
def ensure_database_ready():
    init_db()
    seed_demo_data()


@store_bp.get("/")
def home():
    products = list_active_products()
    return render_template(
        "store/home.html",
        products=products,
        product_map_json=json.dumps({str(product["id"]): product for product in products}),
    )


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
