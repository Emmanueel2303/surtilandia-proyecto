import json

from ..db import get_db
from .shared import format_currency, slugify


def list_active_products():
    rows = get_db().execute(
        """
        SELECT *
        FROM products
        WHERE is_active = 1
        ORDER BY created_at DESC
        """
    ).fetchall()
    return [serialize_product(row) for row in rows]


def list_all_products():
    rows = get_db().execute(
        """
        SELECT *
        FROM products
        ORDER BY updated_at DESC, id DESC
        """
    ).fetchall()
    return [serialize_product(row) for row in rows]


def get_product(product_id):
    row = get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return serialize_product(row) if row else None


def get_product_by_slug(slug):
    row = get_db().execute("SELECT * FROM products WHERE slug = ? AND is_active = 1", (slug,)).fetchone()
    return serialize_product(row) if row else None


def create_product(form_data, primary_image, gallery_images):
    db = get_db()
    timestamp = form_data.get("timestamp")
    slug = slugify(form_data.get("slug") or form_data["name"])
    gallery_json = json.dumps(gallery_images)

    cursor = db.execute(
        """
        INSERT INTO products (
            slug, reference, name, category, price, stock,
            short_description, details, primary_image, gallery_json,
            is_active, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            slug,
            form_data["reference"],
            form_data["name"],
            form_data["category"],
            int(form_data["price"]),
            int(form_data["stock"]),
            form_data["short_description"],
            form_data["details"],
            primary_image,
            gallery_json,
            1 if form_data.get("is_active", "1") == "1" else 0,
            timestamp,
            timestamp,
        ),
    )
    db.commit()
    return cursor.lastrowid


def update_product(product_id, form_data, primary_image, gallery_images):
    db = get_db()
    current = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if current is None:
        return False

    timestamp = form_data.get("timestamp")
    existing_gallery = json.loads(current["gallery_json"] or "[]")
    merged_gallery = existing_gallery + gallery_images
    final_primary_image = primary_image or form_data.get("primary_image_url") or current["primary_image"]
    if not final_primary_image and merged_gallery:
        final_primary_image = merged_gallery[0]

    db.execute(
        """
        UPDATE products
        SET slug = ?, reference = ?, name = ?, category = ?, price = ?, stock = ?,
            short_description = ?, details = ?, primary_image = ?, gallery_json = ?,
            is_active = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            slugify(form_data.get("slug") or form_data["name"]),
            form_data["reference"],
            form_data["name"],
            form_data["category"],
            int(form_data["price"]),
            int(form_data["stock"]),
            form_data["short_description"],
            form_data["details"],
            final_primary_image,
            json.dumps(merged_gallery),
            1 if form_data.get("is_active", "1") == "1" else 0,
            timestamp,
            product_id,
        ),
    )
    db.commit()
    return True


def serialize_product(row):
    if row is None:
        return None

    product = dict(row)
    product["gallery_images"] = json.loads(product.get("gallery_json") or "[]")
    product["price_display"] = format_currency(product["price"])
    return product
