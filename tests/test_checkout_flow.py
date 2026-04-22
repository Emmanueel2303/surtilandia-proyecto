import os
import tempfile
import unittest

from surtilandia import create_app
from surtilandia.db import get_db, init_db, seed_demo_data


class CheckoutFlowTests(unittest.TestCase):
    def setUp(self):
        db_fd, self.db_path = tempfile.mkstemp(suffix=".sqlite3")
        os.close(db_fd)

        self.app = create_app({"TESTING": True, "DATABASE_PATH": self.db_path})
        with self.app.app_context():
            init_db()
            seed_demo_data()

        self.client = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_guest_checkout_creates_order_and_reduces_stock(self):
        response = self.client.post(
            "/checkout",
            data={
                "full_name": "Ana Gomez",
                "phone": "3001234567",
                "email": "ana@example.com",
                "city": "Bogota",
                "address": "Calle 10 # 20-30",
                "address_notes": "Apto 401",
                "payment_method": "cash_on_delivery",
                "items": '[{"product_id": 1, "quantity": 2}]',
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/pedido/", response.headers["Location"])

        with self.app.app_context():
            db = get_db()
            order = db.execute("SELECT * FROM orders").fetchone()
            product = db.execute("SELECT * FROM products WHERE id = 1").fetchone()

        self.assertIsNotNone(order)
        self.assertEqual(order["status"], "Pendiente")
        self.assertEqual(order["payment_method"], "cash_on_delivery")
        self.assertEqual(order["payment_status"], "pending")
        self.assertEqual(product["stock"], 16)


if __name__ == "__main__":
    unittest.main()
