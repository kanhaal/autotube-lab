from __future__ import annotations
import statistics
from datetime import datetime, timezone
from app.experiments.allocation import performance_score, compute_niche_weights

def refresh_niche_weights(repo,channel_id:str,niches:list[str],now:datetime|None=None,min_samples:int=3)->dict[str,float]:
    now=now or datetime.now(timezone.utc)
    rows=repo.mature_analytics(channel_id,now=now,min_age_days=7)
    views=[r.views for r in rows if r.views is not None]
    median_views=statistics.median(views) if views else 1
    grouped={n:[] for n in niches}
    for r in rows:
        impressions=r.impressions or 0; views_n=r.views or 0
        grouped.setdefault(r.niche,[]).append(performance_score({
            'retention':r.retention,
            'views_ratio': views_n/max(1,median_views),
            'ctr':r.ctr,
            'subs_per_1k': ((r.subscribers_gained or 0)-(r.subscribers_lost or 0))*1000/max(1,views_n),
            'watch_per_1k_imp': (r.watch_minutes or 0)*1000/max(1,impressions),
        }))
    eligible={k:v for k,v in grouped.items() if len(v)>=min_samples}
    if len(eligible)<2:
        w={n:1/len(niches) for n in niches}
    else:
        all_scores={n:(grouped[n] if len(grouped[n])>=min_samples else [statistics.median([x for vs in eligible.values() for x in vs])]) for n in niches}
        w=compute_niche_weights(all_scores,floor=.12,cap=.80)
    repo.save_weights(channel_id,w); return w
