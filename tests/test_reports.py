import os
import tempfile
import unittest

from surtilandia import create_app
from surtilandia.db import init_db, seed_demo_data
from surtilandia.services.orders import create_guest_order
from surtilandia.services.reports import summarize_dashboard


class ReportsTests(unittest.TestCase):
    def setUp(self):
        db_fd, self.db_path = tempfile.mkstemp(suffix=".sqlite3")
        os.close(db_fd)

        self.app = create_app({"TESTING": True, "DATABASE_PATH": self.db_path})
        with self.app.app_context():
            init_db()
            seed_demo_data()
            create_guest_order(
                {
                    "full_name": "Mariana Ruiz",
                    "phone": "3031234567",
                    "email": "mariana@example.com",
                    "city": "Barranquilla",
                    "address": "Calle 80 # 55-40",
                    "address_notes": "",
                    "payment_method": "cash_on_delivery",
                    "items": '[{"product_id": 1, "quantity": 1}]',
                }
            )

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_dashboard_summary_exposes_kpis(self):
        with self.app.app_context():
            summary = summarize_dashboard()

        self.assertIn("total_orders", summary)
        self.assertIn("total_sales", summary)
        self.assertEqual(summary["total_orders"], 1)


if __name__ == "__main__":
    unittest.main()
