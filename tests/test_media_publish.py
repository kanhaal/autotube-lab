from pathlib import Path
from app.visuals.thumbnail import render_thumbnail
from app.rendering.ffmpeg import build_color_video, probe_video
from app.publishing.youtube import PrivateFirstPublisher


def test_thumbnail_dimensions(tmp_path: Path):
    p=render_thumbnail('KernelRush','THIS REPO EXPLODED',tmp_path/'t.png',{'background':'#0A0D12','foreground':'#ffffff','accent':'#5EF2C2'})
    from PIL import Image
    assert Image.open(p).size == (1280,720)


def test_ffmpeg_smoke(tmp_path: Path):
    p=build_color_video(tmp_path/'v.mp4', seconds=1, title='TEST')
    info=probe_video(p)
    assert info['width']==1920 and info['height']==1080


class FakeYT:
    def __init__(self): self.state='processing'; self.scheduled=None
    def upload_private(self, **kwargs): return 'abc123'
    def set_thumbnail(self, video_id, thumbnail): assert video_id=='abc123'
    def processing_state(self, video_id): return self.state
    def schedule(self, video_id, publish_at): self.scheduled=publish_at


def test_private_first_does_not_schedule_until_processing_done(tmp_path: Path):
    y=FakeYT(); pub=PrivateFirstPublisher(y)
    video=tmp_path/'v.mp4'; video.write_bytes(b'x')
    thumb=tmp_path/'t.png'; thumb.write_bytes(b'x')
    result=pub.stage(video,thumb,{'title':'x','description':'y'})
    assert result.status=='processing'
    assert y.scheduled is None
