from __future__ import annotations
from datetime import datetime, timezone
from app.domain.models import AnalyticsSnapshot

def snapshot_from_client(client, video_id:str, channel_id:str, niche:str, published_at:datetime, snapshot_at:datetime|None=None):
    snapshot_at=snapshot_at or datetime.now(timezone.utc)
    start=published_at.date().isoformat(); end=snapshot_at.date().isoformat()
    row=client.analytics_row(video_id,start,end)
    return AnalyticsSnapshot(video_id,channel_id,niche,published_at,snapshot_at,None,None,row.get('views'),row.get('retention'),row.get('watch_minutes'),row.get('subs_gained'),row.get('subs_lost'))
