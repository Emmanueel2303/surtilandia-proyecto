import json
import uuid

from werkzeug.exceptions import BadRequest

from ..db import get_db, now_iso
from .shared import format_currency


def create_guest_order(form_data):
    items = _parse_items_payload(form_data.get("items", "[]"))
    if not items:
        raise BadRequest("No items were provided.")

    db = get_db()
    timestamp = now_iso()

    customer_cursor = db.execute(
        """
        INSERT INTO customers (full_name, phone, email, city, address, address_notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            form_data["full_name"],
            form_data["phone"],
            form_data["email"],
            form_data["city"],
            form_data["address"],
            form_data.get("address_notes", ""),
            timestamp,
            timestamp,
        ),
    )
    customer_id = customer_cursor.lastrowid

    subtotal = 0
    order_rows = []

    for item in items:
        product = db.execute("SELECT * FROM products WHERE id = ?", (item["product_id"],)).fetchone()
        if product is None:
            raise BadRequest("The selected product does not exist.")
        if product["stock"] < item["quantity"]:
            raise BadRequest("The selected quantity is not available.")

        line_subtotal = product["price"] * item["quantity"]
        subtotal += line_subtotal
        order_rows.append((product, item["quantity"], line_subtotal))

    public_order_id = "SURTI-" + uuid.uuid4().hex[:8].upper()
    payment_method = form_data.get("payment_method", "cash_on_delivery")
    payment_status = "paid" if payment_method == "wompi" else "pending"

    order_cursor = db.execute(
        """
        INSERT INTO orders (
            public_order_id, customer_id, status, payment_method, payment_status,
            shipping_city, shipping_address_snapshot, shipping_notes,
            subtotal, shipping_amount, total, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            public_order_id,
            customer_id,
            "Pendiente",
            payment_method,
            payment_status,
            form_data["city"],
            form_data["address"],
            form_data.get("address_notes", ""),
            subtotal,
            0,
            subtotal,
            timestamp,
            timestamp,
        ),
    )
    order_id = order_cursor.lastrowid

    for product, quantity, line_subtotal in order_rows:
        db.execute(
            """
            INSERT INTO order_items (
                order_id, product_id, product_name_snapshot, product_reference_snapshot,
                unit_price_snapshot, quantity, subtotal
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                product["id"],
                product["name"],
                product["reference"],
                product["price"],
                quantity,
                line_subtotal,
            ),
        )
        db.execute(
            "UPDATE products SET stock = ?, updated_at = ? WHERE id = ?",
            (product["stock"] - quantity, timestamp, product["id"]),
        )

    db.execute(
        """
        INSERT INTO order_history (order_id, from_status, to_status, note, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, "", "Pendiente", "Solicitud creada desde la vitrina Surtilandia.", timestamp),
    )
    db.commit()

    return public_order_id


def get_order_by_public_id(public_order_id):
    db = get_db()
    order = db.execute(
        """
        SELECT orders.*, customers.full_name, customers.phone, customers.email
        FROM orders
        JOIN customers ON customers.id = orders.customer_id
        WHERE public_order_id = ?
        """,
        (public_order_id,),
    ).fetchone()

    if order is None:
        return None

    items = db.execute(
        """
        SELECT *
        FROM order_items
        WHERE order_id = ?
        ORDER BY id ASC
        """,
        (order["id"],),
    ).fetchall()

    order_dict = dict(order)
    order_dict["subtotal_display"] = format_currency(order_dict["subtotal"])
    order_dict["total_display"] = format_currency(order_dict["total"])
    order_dict["shipping_amount_display"] = format_currency(order_dict["shipping_amount"])

    item_rows = []
    for item in items:
        item_dict = dict(item)
        item_dict["unit_price_display"] = format_currency(item_dict["unit_price_snapshot"])
        item_dict["subtotal_display"] = format_currency(item_dict["subtotal"])
        item_rows.append(item_dict)

    history = db.execute(
        """
        SELECT from_status, to_status, note, created_at
        FROM order_history
        WHERE order_id = ?
        ORDER BY id DESC
        """,
        (order["id"],),
    ).fetchall()

    return {
        "order": order_dict,
        "items": item_rows,
        "history": [dict(row) for row in history],
    }


def update_order_status(public_order_id, status, note="", shipping_carrier="", shipping_guide=""):
    db = get_db()
    order = db.execute(
        "SELECT id, status FROM orders WHERE public_order_id = ?",
        (public_order_id,),
    ).fetchone()
    if order is None:
        raise BadRequest("The selected order does not exist.")

    timestamp = now_iso()
    db.execute(
        """
        UPDATE orders
        SET status = ?, shipping_carrier = ?, shipping_guide = ?, updated_at = ?
        WHERE public_order_id = ?
        """,
        (status, shipping_carrier, shipping_guide, timestamp, public_order_id),
    )
    db.execute(
        """
        INSERT INTO order_history (order_id, from_status, to_status, note, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order["id"], order["status"], status, note, timestamp),
    )
    db.commit()


def list_orders():
    rows = get_db().execute(
        """
        SELECT orders.public_order_id, orders.status, orders.payment_method, orders.total, orders.created_at,
               customers.full_name, customers.city
        FROM orders
        JOIN customers ON customers.id = orders.customer_id
        ORDER BY orders.created_at DESC
        """
    ).fetchall()

    return [
        {**dict(row), "total_display": format_currency(row["total"])}
        for row in rows
    ]


def list_customers():
    rows = get_db().execute(
        """
        SELECT customers.*,
               COUNT(orders.id) AS total_orders,
               COALESCE(SUM(orders.total), 0) AS total_spent
        FROM customers
        LEFT JOIN orders ON orders.customer_id = customers.id
        GROUP BY customers.id
        ORDER BY customers.created_at DESC
        """
    ).fetchall()

    return [
        {**dict(row), "total_spent_display": format_currency(row["total_spent"])}
        for row in rows
    ]


def _parse_items_payload(raw_items):
    try:
        payload = json.loads(raw_items)
    except json.JSONDecodeError as exc:
        raise BadRequest("The order payload is invalid.") from exc

    parsed = []
    for item in payload:
        parsed.append(
            {
                "product_id": int(item["product_id"]),
                "quantity": int(item["quantity"]),
            }
        )
    return parsed
