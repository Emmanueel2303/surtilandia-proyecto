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
        SELECT id, name, stock, category
        FROM products
        WHERE stock <= 5
        ORDER BY stock ASC, name ASC
        LIMIT 5
        """
    ).fetchall()

    recent_orders = db.execute(
        """
        SELECT orders.public_order_id, orders.status, orders.total, orders.created_at,
               customers.full_name, customers.city
        FROM orders
        JOIN customers ON customers.id = orders.customer_id
        ORDER BY orders.created_at DESC
        LIMIT 6
        """
    ).fetchall()

    product_health = db.execute(
        """
        SELECT
            COUNT(*) AS total_references,
            COALESCE(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END), 0) AS active_references,
            COALESCE(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END), 0) AS hidden_references,
            COALESCE(SUM(CASE WHEN stock <= 5 THEN 1 ELSE 0 END), 0) AS low_stock_references,
            COALESCE(SUM(stock), 0) AS total_units
        FROM products
        """
    ).fetchone()

    total_customers = db.execute("SELECT COUNT(*) AS total_customers FROM customers").fetchone()

    status_rows = db.execute(
        """
        SELECT status, COUNT(*) AS count
        FROM orders
        GROUP BY status
        """
    ).fetchall()

    category_rows = db.execute(
        """
        SELECT category, COUNT(*) AS count
        FROM products
        WHERE is_active = 1
        GROUP BY category
        ORDER BY count DESC, category ASC
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

    total_orders = totals["total_orders"]
    total_sales = totals["total_sales"]
    status_map = {row["status"]: row["count"] for row in status_rows}
    statuses = ["Pendiente", "Confirmado", "Enviado", "Entregado"]
    status_breakdown = []
    for status in statuses:
        count = status_map.get(status, 0)
        percent = round((count / total_orders) * 100) if total_orders else 0
        status_breakdown.append({"status": status, "count": count, "percent": percent})

    max_top_units = max([row["total_units"] for row in top_products], default=0)
    top_products_payload = []
    for row in top_products:
        percent = round((row["total_units"] / max_top_units) * 100) if max_top_units else 0
        top_products_payload.append({**dict(row), "percent": percent})

    pending_work = totals["pending_orders"] + status_map.get("Confirmado", 0) + status_map.get("Enviado", 0)
    next_actions = [
        {
            "label": "Confirmar solicitudes pendientes",
            "value": totals["pending_orders"],
            "tone": "warning" if totals["pending_orders"] else "ok",
        },
        {
            "label": "Revisar referencias con stock bajo",
            "value": product_health["low_stock_references"],
            "tone": "warning" if product_health["low_stock_references"] else "ok",
        },
        {
            "label": "Mantener vitrina activa",
            "value": product_health["active_references"],
            "tone": "ok" if product_health["active_references"] else "warning",
        },
    ]

    return {
        "total_orders": total_orders,
        "total_sales": total_sales,
        "total_sales_display": format_currency(total_sales),
        "pending_orders": totals["pending_orders"],
        "delivered_orders": totals["delivered_orders"],
        "pending_work": pending_work,
        "fulfillment_rate": round((totals["delivered_orders"] / total_orders) * 100) if total_orders else 0,
        "average_order_display": format_currency(total_sales // total_orders if total_orders else 0),
        "total_customers": total_customers["total_customers"],
        "product_health": dict(product_health),
        "status_breakdown": status_breakdown,
        "top_categories": [dict(row) for row in category_rows],
        "next_actions": next_actions,
        "stock_alerts": [dict(row) for row in stock_alerts],
        "recent_orders": [
            {**dict(row), "total_display": format_currency(row["total"])}
            for row in recent_orders
        ],
        "top_products": top_products_payload,
    }
