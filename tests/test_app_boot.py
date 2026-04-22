import unittest

from surtilandia import create_app


class AppBootTests(unittest.TestCase):
    def test_home_route_responds(self):
        app = create_app({"TESTING": True, "DATABASE_PATH": ":memory:"})
        client = app.test_client()

        response = client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_home_route_uses_original_storefront_copy(self):
        app = create_app({"TESTING": True, "DATABASE_PATH": ":memory:"})
        client = app.test_client()

        response = client.get("/")
        body = response.get_data(as_text=True)

        self.assertIn("SURTITODO VIRTUAL", body)
        self.assertIn("Compra facil por Instagram", body)
        self.assertIn("Nuestra esencia", body)


if __name__ == "__main__":
    unittest.main()
