from __future__ import annotations

import re
from copy import deepcopy
from typing import NotRequired, cast

from .types import AnimeMetadata, AnimePreview, EpisodeMetadata, SeasonEntry


class CentralizedAnimePreview(AnimePreview):
    season_entries: NotRequired[list[SeasonEntry]]


_SEASON_PATTERNS = [
    re.compile(r"\b(?:the\s+)?final\s+season\b", re.IGNORECASE),
    re.compile(r"\bseason\s+\d+\b", re.IGNORECASE),
    re.compile(r"\bs\d+\b", re.IGNORECASE),
    re.compile(r"\b\d+(?:st|nd|rd|th)\s+season\b", re.IGNORECASE),
    re.compile(r"\bpart\s+\d+\b", re.IGNORECASE),
    re.compile(r"\bcour\s+\d+\b", re.IGNORECASE),
]
_TRAILING_SEASON_PATTERN = re.compile(r"\s*[:-]\s*$")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_SEASON_NUMBER_PATTERNS = [
    re.compile(r"\bseason\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"\bs(\d+)\b", re.IGNORECASE),
    re.compile(r"\b(\d+)(?:st|nd|rd|th)\s+season\b", re.IGNORECASE),
]
_ORDINAL_WORDS = {
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
}
_ORDINAL_WORD_PATTERN = re.compile(
    r"\b(" + "|".join(_ORDINAL_WORDS.keys()) + r")\s+season\b",
    re.IGNORECASE,
)


def centralize_seasons(
    items: list[AnimePreview],
    *,
    key_titles: dict[str, str] | None = None,
) -> list[CentralizedAnimePreview]:
    """Collapse season-split search/catalog previews into one show-level item.

    Providers such as MAL, Kitsu, and AniList often expose each season as a
    separate anime. This helper groups previews by their base show title and
    keeps a `season_entries` list so an addon can later fetch and merge all
    seasons for the selected show.
    """

    groups: dict[str, list[AnimePreview]] = {}
    for item in items:
        base_title = (key_titles or {}).get(item["id"]) or base_show_title(item["title"])
        groups.setdefault(normalize_title_key(base_title), []).append(item)

    centralized: list[CentralizedAnimePreview] = []
    for group in groups.values():
        sorted_group = sorted(
            group,
            key=lambda item: (
                season_number_of(item["title"]) or 1,
                item.get("year") or 0,
                item["title"],
            ),
        )
        primary = deepcopy(sorted_group[0])
        primary["title"] = (key_titles or {}).get(primary["id"]) or base_show_title(primary["title"])
        centralized_item = cast(CentralizedAnimePreview, primary)
        centralized_item["season_entries"] = [
            {
                "id": item["id"],
                "title": item["title"],
                "season_number": season_number_of(item["title"]),
                "year": item.get("year"),
                "episode_count": None,
            }
            for item in sorted_group
        ]
        centralized.append(centralized_item)

    return centralized


def combine_anime_seasons(seasons: list[AnimeMetadata]) -> AnimeMetadata:
    """Merge multiple season metadata responses into one show-level metadata."""

    if not seasons:
        raise ValueError("at least one season is required")

    ordered = sorted(
        seasons,
        key=lambda item: (
            item.get("season_year") or item.get("year") or 0,
            item.get("start_date") or "",
            season_number_of(item["title"]) or 1,
        ),
    )
    combined = deepcopy(ordered[0])
    combined["id"] = "central:" + ",".join(item["id"] for item in ordered)
    combined["title"] = base_show_title(combined["title"])
    combined["alternative_titles"] = unique_strings(
        title
        for item in ordered
        for title in [item["title"], *item.get("alternative_titles", [])]
        if title != combined["title"]
    )
    combined["genres"] = unique_strings(genre for item in ordered for genre in item.get("genres", []))
    combined["tags"] = unique_strings(tag for item in ordered for tag in item.get("tags", []))
    combined["studios"] = unique_strings(studio for item in ordered for studio in item.get("studios", []))
    combined["episodes"] = _combined_episodes(ordered)
    combined["episode_count"] = len(combined["episodes"]) or sum(
        item.get("episode_count") or 0 for item in ordered
    ) or None
    combined["start_date"] = next((item.get("start_date") for item in ordered if item.get("start_date")), None)
    combined["end_date"] = next((item.get("end_date") for item in reversed(ordered) if item.get("end_date")), None)
    combined["season"] = None
    combined["season_year"] = combined.get("year")
    return combined


def base_show_title(title: str) -> str:
    value = title
    for pattern in _SEASON_PATTERNS:
        value = pattern.sub("", value)
    value = _ORDINAL_WORD_PATTERN.sub("", value)
    value = _TRAILING_SEASON_PATTERN.sub("", value)
    return _WHITESPACE_PATTERN.sub(" ", value).strip()


def normalize_title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", base_show_title(title).lower())


def season_number_of(title: str) -> int | None:
    for pattern in _SEASON_NUMBER_PATTERNS:
        match = pattern.search(title)
        if match:
            return int(match.group(1))
    match = _ORDINAL_WORD_PATTERN.search(title)
    if match:
        return _ORDINAL_WORDS[match.group(1).lower()]
    return None


def unique_strings(values) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip() if isinstance(value, str) else ""
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _combined_episodes(seasons: list[AnimeMetadata]) -> list[EpisodeMetadata]:
    episodes: list[EpisodeMetadata] = []
    used_season_numbers: set[int] = set()
    for season in seasons:
        explicit_season_number = season_number_of(season["title"])
        if explicit_season_number is not None:
            season_number = explicit_season_number
        else:
            season_number = next_later_season_number(used_season_numbers)
        used_season_numbers.add(season_number)
        for episode in season.get("episodes", []):
            merged = deepcopy(episode)
            merged["anime_id"] = "central:" + ",".join(item["id"] for item in seasons)
            merged["season_number"] = episode.get("season_number") or season_number
            merged["id"] = f'{season["id"]}:{episode["id"]}'
            episodes.append(merged)
    return episodes


def next_later_season_number(used: set[int]) -> int:
    return max(used, default=0) + 1
