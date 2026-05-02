from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

AddonResource = Literal["catalog", "search", "anime_meta", "episode_meta", "video_sources"]
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


class VideoSourceRequest(TypedDict):
    anime_id: str
    addon_id: NotRequired[str]
    episode_id: NotRequired[str | None]
    episode_number: NotRequired[int | None]
    season_number: NotRequired[int | None]


class VideoHeader(TypedDict):
    name: str
    value: str


class VideoStream(TypedDict):
    id: str
    title: NotRequired[str | None]
    url: str
    quality: NotRequired[str | None]
    format: NotRequired[str | None]
    audio_language: NotRequired[str | None]
    headers: list[VideoHeader]


class VideoSubtitle(TypedDict):
    id: str
    label: str
    language: NotRequired[str | None]
    url: str
    format: NotRequired[str | None]


class VideoSourceResponse(TypedDict):
    streams: list[VideoStream]
    subtitles: NotRequired[list[VideoSubtitle]]


class SeasonEntry(TypedDict):
    id: str
    title: str
    season_number: int | None
    year: int | None
    episode_count: int | None
    source: NotRequired[str | None]


class AnimePreview(TypedDict):
    id: str
    title: str
    poster: str | None
    banner: NotRequired[str | None]
    synopsis: NotRequired[str | None]
    score: NotRequired[float | None]
    year: int | None
    content_type: ContentType
    genres: NotRequired[list[str]]
    season_entries: NotRequired[list[SeasonEntry]]


class CatalogResponse(TypedDict):
    items: list[AnimePreview]


class EpisodeMetadata(TypedDict):
    id: str
    anime_id: str
    season_number: NotRequired[int | None]
    number: int
    title: str | None
    synopsis: str | None
    thumbnail: str | None
    duration_minutes: NotRequired[int | None]
    source: NotRequired[str | None]
    aired_at: str | None


class StaffCredit(TypedDict):
    name: str
    role: str | None


class ExternalLink(TypedDict):
    site: str
    url: str


class AnimeMetadata(TypedDict):
    id: str
    title: str
    original_title: str | None
    alternative_titles: list[str]
    synopsis: str | None
    description: str | None
    poster: str | None
    banner: str | None
    year: int | None
    season: str | None
    season_year: int | None
    status: str | None
    content_type: ContentType
    source: str | None
    duration_minutes: int | None
    episode_count: int | None
    score: float | None
    rank: int | None
    popularity: int | None
    rating: str | None
    genres: list[str]
    tags: list[str]
    authors: list[str]
    studios: list[str]
    staff: list[StaffCredit]
    country_of_origin: str | None
    start_date: str | None
    end_date: str | None
    site_url: str | None
    trailer_url: str | None
    external_links: list[ExternalLink]
    episodes: list[EpisodeMetadata]
    updated_at: str | None


class AddonHealth(TypedDict):
    ok: bool
    message: str | None
