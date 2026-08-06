import os
import tempfile
import unittest

from web_dashboard import create_app


class WebDashboardTests(unittest.TestCase):
    def test_dashboard_renders_with_empty_data(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
            temp_db = handle.name

        try:
            app = create_app(database_path=temp_db)
            app.config.update(TESTING=True)
            client = app.test_client()

            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Sentinel Dashboard", response.get_data(as_text=True))
        finally:
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except PermissionError:
                    pass


if __name__ == "__main__":
    unittest.main()
