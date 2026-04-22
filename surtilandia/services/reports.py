from ..db import get_db
from .shared import format_currency


def summarize_dashboard():
    db = get_db()

    totals = db.execute(
        """
        SELECT
            COUNT(*) AS total_orders,
            COALESCE(SUM(total), 0) AS total_sales,
            COALESCE(SUM(CASE WHEN status = 'Pendiente' THEN 1 ELSE 0 END), 0) AS pending_orders,
            COALESCE(SUM(CASE WHEN status = 'Entregado' THEN 1 ELSE 0 END), 0) AS delivered_orders
        FROM orders
        """
    ).fetchone()

    stock_alerts = db.execute(
        """
        SELECT id, name, stock
        FROM products
        WHERE stock <= 5
        ORDER BY stock ASC, name ASC
        LIMIT 5
        """
    ).fetchall()

    recent_orders = db.execute(
        """
        SELECT orders.public_order_id, orders.status, orders.total, orders.created_at, customers.full_name
        FROM orders
        JOIN customers ON customers.id = orders.customer_id
        ORDER BY orders.created_at DESC
        LIMIT 6
        """
    ).fetchall()

    top_products = db.execute(
        """
        SELECT product_name_snapshot AS name, SUM(quantity) AS total_units
        FROM order_items
        GROUP BY product_name_snapshot
        ORDER BY total_units DESC, name ASC
        LIMIT 5
        """
    ).fetchall()

    return {
        "total_orders": totals["total_orders"],
        "total_sales": totals["total_sales"],
        "total_sales_display": format_currency(totals["total_sales"]),
        "pending_orders": totals["pending_orders"],
        "delivered_orders": totals["delivered_orders"],
        "stock_alerts": [dict(row) for row in stock_alerts],
        "recent_orders": [
            {**dict(row), "total_display": format_currency(row["total"])}
            for row in recent_orders
        ],
        "top_products": [dict(row) for row in top_products],
    }
