import os
import tempfile
import unittest

from surtilandia import create_app
from surtilandia.db import init_db, seed_demo_data
from surtilandia.services.orders import create_guest_order


class OrderTrackingTests(unittest.TestCase):
    def setUp(self):
        db_fd, self.db_path = tempfile.mkstemp(suffix=".sqlite3")
        os.close(db_fd)

        self.app = create_app({"TESTING": True, "DATABASE_PATH": self.db_path})
        with self.app.app_context():
            init_db()
            seed_demo_data()
            self.public_order_id = create_guest_order(
                {
                    "full_name": "Luisa Gomez",
                    "phone": "3021234567",
                    "email": "luisa@example.com",
                    "city": "Cali",
                    "address": "Av 4 # 22-10",
                    "address_notes": "",
                    "payment_method": "wompi",
                    "items": '[{"product_id": 1, "quantity": 1}]',
                }
            )

        self.client = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_tracking_page_shows_order_status(self):
        response = self.client.get(f"/seguimiento?order_id={self.public_order_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.public_order_id, response.get_data(as_text=True))
        self.assertIn("Pendiente", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
