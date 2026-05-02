# Typenx Addon Python SDK

Python SDK for building Typenx addons.

Typenx addons are remote HTTP services. Metadata addons provide catalog, search, and anime metadata. Video addons can also opt into `video_sources` and return episode stream URLs.

## Install

```bash
pip install typenx-addon-python-sdk
```

## Example

```python
from datetime import datetime, timezone

from typenx_addon_python_sdk import create_typenx_addon, serve_typenx_addon

shows = [
    {
        "id": "frieren-beyond-journeys-end",
        "title": "Frieren: Beyond Journey's End",
        "poster": "https://cdn.myanimelist.net/images/anime/1015/138006.jpg",
        "banner": "https://example.com/frieren-banner.jpg",
        "synopsis": "An elf mage retraces a former journey and learns what time leaves behind.",
        "score": 9.2,
        "year": 2023,
        "content_type": "anime",
    }
]

addon = create_typenx_addon(
    manifest={
        "id": "my-anime-source",
        "name": "My Anime Source",
        "version": "0.1.0",
        "description": "Metadata addon backed by my anime catalog service.",
        "icon": "https://typenx.dev/addon-icon.png",
        "resources": ["catalog", "search", "anime_meta", "video_sources"],
        "catalogs": [
            {"id": "popular", "name": "Popular", "content_type": "anime", "filters": []}
        ],
    },
    handlers={
        "catalog": lambda request: {"items": shows},
        "search": lambda request: {
            "items": [
                show
                for show in shows
                if request["query"].lower() in show["title"].lower()
            ]
        },
        "anime": lambda anime_id: {
            "id": anime_id,
            "title": "Frieren: Beyond Journey's End",
            "original_title": "Sousou no Frieren",
            "alternative_titles": ["Frieren: Beyond Journey's End"],
            "synopsis": "An elf mage retraces a former journey and learns what time leaves behind.",
            "description": "An elf mage retraces a former journey and learns what time leaves behind.",
            "poster": shows[0]["poster"],
            "banner": shows[0]["banner"],
            "year": 2023,
            "season": "fall",
            "season_year": 2023,
            "status": "finished",
            "content_type": "anime",
            "source": "manga",
            "duration_minutes": 24,
            "episode_count": 28,
            "score": 9.2,
            "rank": 1,
            "popularity": None,
            "rating": "pg_13",
            "genres": ["Adventure", "Drama", "Fantasy"],
            "tags": ["Magic", "Elf", "Travel"],
            "authors": ["Kanehito Yamada"],
            "studios": ["Madhouse"],
            "staff": [{"name": "Kanehito Yamada", "role": "Original Creator"}],
            "country_of_origin": "JP",
            "start_date": "2023-09-29",
            "end_date": "2024-03-22",
            "site_url": "https://myanimelist.net/anime/52991",
            "trailer_url": None,
            "external_links": [
                {"site": "MyAnimeList", "url": "https://myanimelist.net/anime/52991"}
            ],
            "episodes": [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        "videos": lambda request: {
            "streams": [
                {
                    "id": f"{request['anime_id']}-{request.get('episode_number') or request.get('episode_id')}-720p",
                    "title": "720p",
                    "url": "https://cdn.example/anime/episode-1.mp4",
                    "quality": "720p",
                    "format": "mp4",
                    "audio_language": "ja",
                    "headers": [],
                }
            ],
            "subtitles": [],
        },
    },
)

serve_typenx_addon(addon)
```

## Centralizing split seasons

MAL, Kitsu, and AniList often return separate records for each season of one show. The SDK includes helpers for addon authors that want to present those as one centralized show:

```python
from typenx_addon_python_sdk import centralize_seasons, combine_anime_seasons

search_items = centralize_seasons(provider_search_items)
show = combine_anime_seasons([season_one_meta, season_two_meta, season_three_meta])
```

`centralize_seasons()` keeps the normal preview fields and adds `season_entries`, so your addon can fetch each source season and pass the metadata into `combine_anime_seasons()`.

## Routes

- `GET /health`
- `GET /manifest`
- `POST /catalog`
- `POST /search`
- `GET /anime/:id`
- `POST /videos`
