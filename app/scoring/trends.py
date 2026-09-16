from __future__ import annotations
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit
from app.domain.models import StoryCandidate

def _norm_url(url: str) -> str:
    p=urlsplit(url)
    return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip('/'),'', ''))

def score_candidate(c: StoryCandidate) -> float:
    now=datetime.now(timezone.utc)
    pub=c.published_at if c.published_at.tzinfo else c.published_at.replace(tzinfo=timezone.utc)
    age_h=max(0,(now-pub).total_seconds()/3600)
    freshness=max(0,1-age_h/72)
    velocity=float(c.raw_metrics.get('velocity', c.raw_metrics.get('score_norm', .4)) or 0)
    rel=max(0,min(1,c.source_reliability_weight))
    visual=.8 if c.entities else .6
    return .35*freshness+.30*max(0,min(1,velocity))+.25*rel+.10*visual

def deduplicate_candidates(items: list[StoryCandidate]) -> list[StoryCandidate]:
    by={}
    for c in items:
        k=_norm_url(c.canonical_url)
        if k not in by or c.source_reliability_weight>by[k].source_reliability_weight:
            by[k]=c
    return list(by.values())
