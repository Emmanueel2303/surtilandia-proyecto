import os
import tempfile
import unittest

from surtilandia import create_app
from surtilandia.db import init_db, seed_admin_user, seed_demo_data


class AdminAuthTests(unittest.TestCase):
    def setUp(self):
        db_fd, self.db_path = tempfile.mkstemp(suffix=".sqlite3")
        os.close(db_fd)

        self.app = create_app({"TESTING": True, "DATABASE_PATH": self.db_path})
        with self.app.app_context():
            init_db()
            seed_demo_data()
            seed_admin_user()

        self.client = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_admin_requires_login(self):
        response = self.client.get("/admin", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])


if __name__ == "__main__":
    unittest.main()
