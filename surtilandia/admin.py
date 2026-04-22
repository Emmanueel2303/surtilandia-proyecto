from functools import wraps

from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db, init_db, seed_admin_user, seed_demo_data
from .db import now_iso
from .services.catalog import create_product, get_product, list_all_products, update_product
from .services.orders import get_order_by_public_id, list_customers, list_orders, update_order_status
from .services.reports import summarize_dashboard
from .services.shared import slugify
from .services.uploads import save_uploaded_images

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_app_request
def ensure_admin_database_ready():
    init_db()
    seed_demo_data()
    seed_admin_user()


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin_authenticated"):
            return redirect(url_for("admin.login"))
        return view_func(*args, **kwargs)

    return wrapped_view


@admin_bp.get("/login")
def login():
    return render_template("admin/login.html")


@admin_bp.post("/login")
def login_submit():
    user = get_db().execute(
        "SELECT * FROM admin_users WHERE username = ?",
        (request.form.get("username", ""),),
    ).fetchone()

    if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
        session["is_admin_authenticated"] = True
        session["admin_username"] = user["username"]
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/login.html", login_error=True), 401


@admin_bp.get("/logout")
@admin_required
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@admin_bp.get("")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html", summary=summarize_dashboard())


@admin_bp.get("/products")
@admin_required
def products():
    return render_template("admin/products.html", products=list_all_products())


@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_required
def product_create():
    if request.method == "POST":
        saved_images = save_uploaded_images(request.files.getlist("gallery_images"))
        primary_image_url = request.form.get("primary_image_url", "").strip()
        primary_image = primary_image_url or (saved_images[0] if saved_images else "")
        gallery_images = saved_images

        create_product(
            {
                **request.form,
                "slug": request.form.get("slug") or slugify(request.form["name"]),
                "timestamp": now_iso(),
            },
            primary_image,
            gallery_images,
        )
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", product=None, form_title="Nuevo producto")


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def product_edit(product_id):
    product = get_product(product_id)
    if product is None:
        return redirect(url_for("admin.products"))

    if request.method == "POST":
        saved_images = save_uploaded_images(request.files.getlist("gallery_images"))
        primary_image_url = request.form.get("primary_image_url", "").strip()
        primary_image = primary_image_url or (saved_images[0] if saved_images else "")
        update_product(
            product_id,
            {
                **request.form,
                "slug": request.form.get("slug") or slugify(request.form["name"]),
                "timestamp": now_iso(),
            },
            primary_image,
            saved_images,
        )
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", product=product, form_title="Editar producto")


@admin_bp.get("/orders")
@admin_required
def orders():
    return render_template("admin/orders.html", orders=list_orders())


@admin_bp.get("/orders/<public_order_id>")
@admin_required
def order_detail(public_order_id):
    payload = get_order_by_public_id(public_order_id)
    if payload is None:
        return redirect(url_for("admin.orders"))
    return render_template("admin/order_detail.html", payload=payload)


@admin_bp.post("/orders/<public_order_id>/status")
@admin_required
def update_order(public_order_id):
    update_order_status(
        public_order_id,
        request.form["status"],
        request.form.get("note", ""),
    )
    return redirect(url_for("admin.order_detail", public_order_id=public_order_id))


@admin_bp.get("/customers")
@admin_required
def customers():
    return render_template("admin/customers.html", customers=list_customers())
