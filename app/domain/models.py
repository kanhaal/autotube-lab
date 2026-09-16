from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass(frozen=True)
class StoryCandidate:
    id: str
    niche: str
    title: str
    canonical_url: str
    source_name: str
    source_type: str
    published_at: datetime
    fetched_at: datetime
    entities: tuple[str, ...] = ()
    summary: str = ""
    raw_metrics: dict[str, Any] = field(default_factory=dict)
    source_reliability_weight: float = .7
    rights_notes: str = ""

@dataclass(frozen=True)
class Publication:
    episode_id: str
    channel_id: str
    youtube_video_id: str
    status: str
    created_at: datetime

@dataclass(frozen=True)
class AnalyticsSnapshot:
    video_id: str
    channel_id: str
    niche: str
    published_at: datetime
    snapshot_at: datetime
    impressions: int | None
    ctr: float | None
    views: int | None
    retention: float | None
    watch_minutes: float | None
    subscribers_gained: int | None
    subscribers_lost: int | None
