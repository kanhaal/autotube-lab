from datetime import datetime, timezone, timedelta
from pathlib import Path
from app.domain.models import Publication
from app.storage.sqlite import Repository
from app.analytics.youtube import refresh_channel_analytics

class FakeAnalyticsClient:
    def analytics_row(self, video_id, start_date, end_date):
        return {'views':300 if 'ai' in video_id else 100,'watch_minutes':120 if 'ai' in video_id else 30,'retention':.65 if 'ai' in video_id else .35,'subs_gained':6 if 'ai' in video_id else 1,'subs_lost':0}

def test_refresh_channel_analytics_ingests_published_video_and_updates_weights(tmp_path: Path):
    repo=Repository(tmp_path/'a.db'); repo.init(); now=datetime.now(timezone.utc)
    for i in range(3):
        repo.save_publication(Publication(f'2026-09-0{i+1}-kernelrush-ai_software','kernelrush',f'ai-{i}','published',now-timedelta(days=10+i)))
        repo.save_publication(Publication(f'2026-09-0{i+1}-kernelrush-open_source','kernelrush',f'os-{i}','published',now-timedelta(days=10+i)))
    result=refresh_channel_analytics(FakeAnalyticsClient(),repo,'kernelrush',['ai_software','open_source'],now=now,min_age_days=7,min_samples=2)
    assert result['snapshots']==6
    assert result['weights']['ai_software']>result['weights']['open_source']
    assert len(repo.mature_analytics('kernelrush',now=now,min_age_days=7))==6
