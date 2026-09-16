from datetime import date, datetime, timezone
from app.orchestration.daily import build_job_key
from app.domain.models import Publication

def test_job_key_separates_dry_render_and_live_runs():
    d=date(2026,9,16)
    assert build_job_key('kernelrush', d, dry_run=True, has_tts=False, has_publisher=False).endswith(':dry')
    assert build_job_key('kernelrush', d, dry_run=True, has_tts=True, has_publisher=False).endswith(':render')
    assert build_job_key('kernelrush', d, dry_run=False, has_tts=True, has_publisher=True).endswith(':live')

class PubRepo:
    def __init__(self): self.saved=None
    def save_publication(self,p): self.saved=p

def test_record_publication_preserves_episode_channel_video_and_status():
    from app.orchestration.daily import record_publication
    repo=PubRepo(); now=datetime.now(timezone.utc)
    record_publication(repo,'2026-09-16-kernelrush-ai_software','kernelrush','abc123','published',created_at=now)
    assert repo.saved == Publication('2026-09-16-kernelrush-ai_software','kernelrush','abc123','published',now)
