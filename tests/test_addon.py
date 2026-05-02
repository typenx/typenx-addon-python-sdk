import json
import unittest

from typenx_addon_python_sdk import (
    base_show_title,
    centralize_seasons,
    combine_anime_seasons,
    create_typenx_addon,
)


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
                    "alternative_titles": [],
                    "synopsis": None,
                    "description": None,
                    "poster": None,
                    "banner": None,
                    "year": None,
                    "season": None,
                    "season_year": None,
                    "status": None,
                    "content_type": "anime",
                    "source": None,
                    "duration_minutes": None,
                    "episode_count": None,
                    "score": None,
                    "rank": None,
                    "popularity": None,
                    "rating": None,
                    "genres": [],
                    "tags": [],
                    "authors": [],
                    "studios": [],
                    "staff": [],
                    "country_of_origin": None,
                    "start_date": None,
                    "end_date": None,
                    "site_url": None,
                    "trailer_url": None,
                    "external_links": [],
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

    def test_centralize_seasons_collapses_split_show_results(self):
        items = [
            {
                "id": "aot-1",
                "title": "Attack on Titan",
                "poster": None,
                "year": 2013,
                "content_type": "anime",
            },
            {
                "id": "aot-2",
                "title": "Attack on Titan Season 2",
                "poster": None,
                "year": 2017,
                "content_type": "anime",
            },
            {
                "id": "aot-3",
                "title": "Attack on Titan 3rd Season",
                "poster": None,
                "year": 2018,
                "content_type": "anime",
            },
        ]

        centralized = centralize_seasons(items)

        self.assertEqual(len(centralized), 1)
        self.assertEqual(centralized[0]["title"], "Attack on Titan")
        self.assertEqual(
            [entry["id"] for entry in centralized[0]["season_entries"]],
            ["aot-1", "aot-2", "aot-3"],
        )

    def test_combine_anime_seasons_marks_episode_season_numbers(self):
        first = self._metadata("aot-1", "Attack on Titan", 2013, 2)
        second = self._metadata("aot-2", "Attack on Titan Season 2", 2017, 1)

        combined = combine_anime_seasons([second, first])

        self.assertEqual(combined["title"], "Attack on Titan")
        self.assertEqual(combined["episode_count"], 3)
        self.assertEqual(
            [episode["season_number"] for episode in combined["episodes"]],
            [1, 1, 2],
        )

    def test_combine_anime_seasons_avoids_unnamed_season_number_collisions(self):
        first = self._metadata("aot-1", "Attack on Titan", 2013, 1)
        third = self._metadata("aot-3", "Attack on Titan Season 3", 2018, 1)
        final = self._metadata("aot-final", "Attack on Titan Final Season", 2021, 1)

        combined = combine_anime_seasons([final, third, first])

        self.assertEqual(
            [episode["season_number"] for episode in combined["episodes"]],
            [1, 3, 4],
        )

    def test_base_show_title_removes_common_season_suffixes(self):
        self.assertEqual(base_show_title("Mob Psycho 100 III"), "Mob Psycho 100 III")
        self.assertEqual(base_show_title("Attack on Titan Final Season"), "Attack on Titan")

    def _metadata(self, anime_id, title, year, episode_count):
        return {
            "id": anime_id,
            "title": title,
            "original_title": None,
            "alternative_titles": [],
            "synopsis": None,
            "description": None,
            "poster": None,
            "banner": None,
            "year": year,
            "season": None,
            "season_year": year,
            "status": None,
            "content_type": "anime",
            "source": None,
            "duration_minutes": None,
            "episode_count": episode_count,
            "score": None,
            "rank": None,
            "popularity": None,
            "rating": None,
            "genres": [],
            "tags": [],
            "authors": [],
            "studios": [],
            "staff": [],
            "country_of_origin": "JP",
            "start_date": f"{year}-01-01",
            "end_date": None,
            "site_url": None,
            "trailer_url": None,
            "external_links": [],
            "episodes": [
                {
                    "id": f"{anime_id}:{number}",
                    "anime_id": anime_id,
                    "number": number,
                    "title": f"Episode {number}",
                    "synopsis": None,
                    "thumbnail": None,
                    "aired_at": None,
                }
                for number in range(1, episode_count + 1)
            ],
            "updated_at": None,
        }


if __name__ == "__main__":
    unittest.main()
