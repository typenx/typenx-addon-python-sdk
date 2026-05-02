from __future__ import annotations

import asyncio
import inspect
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote, urlparse

from .types import (
    AddonHealth,
    AddonManifest,
    AnimeMetadata,
    CatalogRequest,
    CatalogResponse,
    SearchRequest,
    VideoSourceRequest,
)

JsonObject = dict[str, Any]
MaybeAwaitable = Awaitable[Any] | Any
HealthHandler = Callable[[], MaybeAwaitable]
CatalogHandler = Callable[[CatalogRequest], MaybeAwaitable]
SearchHandler = Callable[[SearchRequest], MaybeAwaitable]
AnimeHandler = Callable[[str], MaybeAwaitable]
VideoSourcesHandler = Callable[[VideoSourceRequest], MaybeAwaitable]


@dataclass(frozen=True)
class Response:
    body: bytes
    status: int = 200
    headers: dict[str, str] | None = None


@dataclass(frozen=True)
class TypenxAddon:
    manifest: AddonManifest
    health_handler: HealthHandler | None
    catalog_handler: CatalogHandler
    search_handler: SearchHandler
    anime_handler: AnimeHandler
    videos_handler: VideoSourcesHandler | None = None

    def handle(self, method: str, url: str, body: bytes | str | None = None) -> Response:
        path = _strip_trailing_slash(urlparse(url).path or "/")

        try:
            if method == "GET" and path == "/health":
                health: AddonHealth = {"ok": True, "message": None}
                return json_response(_resolve(self.health_handler() if self.health_handler else health))

            if method == "GET" and path == "/manifest":
                return json_response(self.manifest)

            if method == "POST" and path == "/catalog":
                return json_response(_resolve(self.catalog_handler(_read_json(body))))

            if method == "POST" and path == "/search":
                return json_response(_resolve(self.search_handler(_read_json(body))))

            if method == "GET" and path.startswith("/anime/"):
                anime_id = unquote(path[len("/anime/") :])
                return json_response(_resolve(self.anime_handler(anime_id)))

            if method == "POST" and path == "/videos":
                if not self.videos_handler:
                    return json_response({"message": "Video sources are not supported"}, status=404)
                return json_response(_resolve(self.videos_handler(_read_json(body))))

            return json_response({"message": "Not found"}, status=404)
        except Exception as error:
            return json_response({"message": str(error) or "Addon failed"}, status=500)


def create_typenx_addon(
    *,
    manifest: AddonManifest,
    handlers: dict[str, Callable[..., MaybeAwaitable]],
) -> TypenxAddon:
    return TypenxAddon(
        manifest=manifest,
        health_handler=handlers.get("health"),
        catalog_handler=_required_handler(handlers, "catalog"),
        search_handler=_required_handler(handlers, "search"),
        anime_handler=_required_handler(handlers, "anime"),
        videos_handler=handlers.get("videos"),
    )


def json_response(payload: Any, status: int = 200) -> Response:
    return Response(
        body=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        status=status,
        headers={"content-type": "application/json; charset=utf-8"},
    )


def _required_handler(handlers: dict[str, Callable[..., MaybeAwaitable]], name: str) -> Callable[..., MaybeAwaitable]:
    if name not in handlers:
        raise ValueError(f"Missing required addon handler: {name}")
    return handlers[name]


def _read_json(body: bytes | str | None) -> JsonObject:
    if body is None or body == b"" or body == "":
        return {}
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    return json.loads(body)


def _resolve(value: MaybeAwaitable) -> Any:
    if not inspect.isawaitable(value):
        return value

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(value)

    raise RuntimeError("Async addon handlers require an async server integration")


def _strip_trailing_slash(path: str) -> str:
    if len(path) > 1 and path.endswith("/"):
        return path[:-1]
    return path
