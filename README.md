# Typenx Addon Python SDK

Python SDK for building Typenx metadata addons.

Typenx addons are remote HTTP services. They provide catalog, search, and anime metadata only. They do not return stream URLs or host media.

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
        "resources": ["catalog", "search", "anime_meta"],
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
            "synopsis": "An elf mage retraces a former journey and learns what time leaves behind.",
            "poster": shows[0]["poster"],
            "banner": None,
            "year": 2023,
            "status": "finished",
            "genres": ["Adventure", "Drama", "Fantasy"],
            "episodes": [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    },
)

serve_typenx_addon(addon)
```

## Routes

- `GET /health`
- `GET /manifest`
- `POST /catalog`
- `POST /search`
- `GET /anime/:id`
