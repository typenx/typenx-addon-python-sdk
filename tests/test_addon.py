import json
import unittest

from typenx_addon_python_sdk import create_typenx_addon


class TypenxAddonTests(unittest.TestCase):
    def setUp(self):
        self.addon = create_typenx_addon(
            manifest={
                "id": "test-addon",
                "name": "Test Addon",
                "version": "0.1.0",
                "description": None,
                "icon": None,
                "resources": ["catalog", "search", "anime_meta"],
                "catalogs": [
                    {"id": "popular", "name": "Popular", "content_type": "anime", "filters": []}
                ],
            },
            handlers={
                "catalog": lambda request: {"items": []},
                "search": lambda request: {"items": []},
                "anime": lambda anime_id: {
                    "id": anime_id,
                    "title": "Test",
                    "original_title": None,
                    "synopsis": None,
                    "poster": None,
                    "banner": None,
                    "year": None,
                    "status": None,
                    "genres": [],
                    "episodes": [],
                    "updated_at": None,
                },
            },
        )

    def test_manifest_route(self):
        response = self.addon.handle("GET", "http://127.0.0.1/manifest")
        self.assertEqual(response.status, 200)
        self.assertEqual(json.loads(response.body)["id"], "test-addon")

    def test_anime_route_decodes_id(self):
        response = self.addon.handle("GET", "http://127.0.0.1/anime/frieren%201")
        self.assertEqual(response.status, 200)
        self.assertEqual(json.loads(response.body)["id"], "frieren 1")


if __name__ == "__main__":
    unittest.main()
