import unittest

from surtilandia import create_app


class AppBootTests(unittest.TestCase):
    def test_home_route_responds(self):
        app = create_app({"TESTING": True, "DATABASE_PATH": ":memory:"})
        client = app.test_client()

        response = client.get("/")

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
