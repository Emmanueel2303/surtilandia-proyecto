import unittest

from surtilandia import create_app


class AppBootTests(unittest.TestCase):
    def test_home_route_responds(self):
        app = create_app({"TESTING": True, "DATABASE_PATH": ":memory:"})
        client = app.test_client()

        response = client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_home_route_uses_surtilandia_brand_copy(self):
        app = create_app({"TESTING": True, "DATABASE_PATH": ":memory:"})
        client = app.test_client()

        response = client.get("/")
        body = response.get_data(as_text=True)

        self.assertIn("MARCA OFICIAL", body)
        self.assertIn("Contenido oficial de Surtilandia", body)
        self.assertIn("Nuestra esencia", body)

    def test_home_route_does_not_expose_admin_entry(self):
        app = create_app({"TESTING": True, "DATABASE_PATH": ":memory:"})
        client = app.test_client()

        response = client.get("/")
        body = response.get_data(as_text=True)

        self.assertNotIn("/admin", body)
        self.assertNotIn("Admin", body)


if __name__ == "__main__":
    unittest.main()
