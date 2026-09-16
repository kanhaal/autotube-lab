from __future__ import annotations
from datetime import datetime, timezone
from app.domain.models import AnalyticsSnapshot

def snapshot_from_client(client, video_id:str, channel_id:str, niche:str, published_at:datetime, snapshot_at:datetime|None=None):
    snapshot_at=snapshot_at or datetime.now(timezone.utc)
    start=published_at.date().isoformat(); end=snapshot_at.date().isoformat()
    row=client.analytics_row(video_id,start,end)
    return AnalyticsSnapshot(video_id,channel_id,niche,published_at,snapshot_at,None,None,row.get('views'),row.get('retention'),row.get('watch_minutes'),row.get('subs_gained'),row.get('subs_lost'))

def refresh_channel_analytics(client,repo,channel_id:str,niches:list[str],now:datetime|None=None,min_age_days:int=7,min_samples:int=3):
    from datetime import timedelta
    from app.analytics.learning import refresh_niche_weights
    now=now or datetime.now(timezone.utc)
    cutoff=now-timedelta(days=min_age_days)
    saved=0
    marker=f'-{channel_id}-'
    for pub in repo.list_publications(channel_id):
        if pub.created_at > cutoff: continue
        if marker not in pub.episode_id: continue
        niche=pub.episode_id.split(marker,1)[1]
        if niche not in niches: continue
        snap=snapshot_from_client(client,pub.youtube_video_id,channel_id,niche,pub.created_at,now)
        repo.save_analytics(snap); saved += 1
    weights=refresh_niche_weights(repo,channel_id,niches,now=now,min_samples=min_samples)
    return {'snapshots':saved,'weights':weights}
