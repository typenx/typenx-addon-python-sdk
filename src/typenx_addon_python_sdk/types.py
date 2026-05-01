from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

AddonResource = Literal["catalog", "search", "anime_meta", "episode_meta"]
ContentType = Literal["anime", "movie", "ova", "ona", "special"]


class CatalogFilter(TypedDict):
    id: str
    name: str
    values: list[str]


class CatalogDefinition(TypedDict):
    id: str
    name: str
    content_type: ContentType
    filters: list[CatalogFilter]


class AddonManifest(TypedDict):
    id: str
    name: str
    version: str
    description: str | None
    icon: str | None
    resources: list[AddonResource]
    catalogs: list[CatalogDefinition]


class CatalogRequest(TypedDict):
    catalog_id: str
    addon_id: NotRequired[str]
    skip: NotRequired[int]
    limit: NotRequired[int]
    query: NotRequired[str]


class SearchRequest(TypedDict):
    query: str
    addon_id: NotRequired[str]
    limit: NotRequired[int]


class AnimePreview(TypedDict):
    id: str
    title: str
    poster: str | None
    year: int | None
    content_type: ContentType


class CatalogResponse(TypedDict):
    items: list[AnimePreview]


class EpisodeMetadata(TypedDict):
    id: str
    anime_id: str
    number: int
    title: str | None
    synopsis: str | None
    thumbnail: str | None
    aired_at: str | None


class AnimeMetadata(TypedDict):
    id: str
    title: str
    original_title: str | None
    synopsis: str | None
    poster: str | None
    banner: str | None
    year: int | None
    status: str | None
    genres: list[str]
    episodes: list[EpisodeMetadata]
    updated_at: str | None


class AddonHealth(TypedDict):
    ok: bool
    message: str | None
