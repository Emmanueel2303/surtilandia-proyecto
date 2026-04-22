import io
import os
import tempfile
import unittest

from surtilandia import create_app
from surtilandia.db import get_db, init_db, seed_admin_user, seed_demo_data


class AdminProductsTests(unittest.TestCase):
    def setUp(self):
        db_fd, self.db_path = tempfile.mkstemp(suffix=".sqlite3")
        os.close(db_fd)

        self.app = create_app({"TESTING": True, "DATABASE_PATH": self.db_path})
        with self.app.app_context():
            init_db()
            seed_demo_data()
            seed_admin_user()

        self.client = self.app.test_client()
        with self.client.session_transaction() as session:
            session["is_admin_authenticated"] = True
            session["admin_username"] = "surtiadmin"

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_admin_can_create_product(self):
        response = self.client.post(
            "/admin/products/new",
            data={
                "name": "Freidora de aire compacta",
                "reference": "SURTI-COC-900",
                "slug": "freidora-aire-compacta",
                "category": "Cocina",
                "price": "189900",
                "stock": "6",
                "short_description": "Coccion rapida para espacios pequenos.",
                "details": "Freidora de aire compacta con control sencillo.",
                "primary_image_url": "https://images.unsplash.com/photo-1585515656826-9721b5f66063?auto=format&fit=crop&w=900&q=80",
                "gallery_images": (io.BytesIO(b""), ""),
            },
            content_type="multipart/form-data",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/products", response.headers["Location"])

        with self.app.app_context():
            db = get_db()
            product = db.execute(
                "SELECT * FROM products WHERE reference = ?",
                ("SURTI-COC-900",),
            ).fetchone()

        self.assertIsNotNone(product)
        self.assertEqual(product["name"], "Freidora de aire compacta")


if __name__ == "__main__":
    unittest.main()
