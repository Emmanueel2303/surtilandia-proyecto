import os
import tempfile
import unittest

from surtilandia import create_app
from surtilandia.db import get_db, init_db, seed_admin_user, seed_demo_data
from surtilandia.services.orders import create_guest_order


class AdminOrderTests(unittest.TestCase):
    def setUp(self):
        db_fd, self.db_path = tempfile.mkstemp(suffix=".sqlite3")
        os.close(db_fd)

        self.app = create_app({"TESTING": True, "DATABASE_PATH": self.db_path})
        with self.app.app_context():
            init_db()
            seed_demo_data()
            seed_admin_user()
            self.public_order_id = create_guest_order(
                {
                    "full_name": "Carlos Perez",
                    "phone": "3011234567",
                    "email": "carlos@example.com",
                    "city": "Medellin",
                    "address": "Cra 45 # 10-11",
                    "address_notes": "",
                    "payment_method": "cash_on_delivery",
                    "items": '[{"product_id": 1, "quantity": 1}]',
                }
            )

        self.client = self.app.test_client()
        with self.client.session_transaction() as session:
            session["is_admin_authenticated"] = True
            session["admin_username"] = "surtiadmin"

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_admin_can_move_order_to_enviado(self):
        response = self.client.post(
            f"/admin/orders/{self.public_order_id}/status",
            data={
                "status": "Enviado",
                "shipping_carrier": "Servientrega",
                "shipping_guide": "SURTI123",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            db = get_db()
            order = db.execute(
                "SELECT status, shipping_carrier, shipping_guide FROM orders WHERE public_order_id = ?",
                (self.public_order_id,),
            ).fetchone()

        self.assertEqual(order["status"], "Enviado")
        self.assertEqual(order["shipping_carrier"], "Servientrega")
        self.assertEqual(order["shipping_guide"], "SURTI123")


if __name__ == "__main__":
    unittest.main()
