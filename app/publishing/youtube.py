from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
@dataclass(frozen=True)
class StageResult:
    video_id:str; status:str
class PrivateFirstPublisher:
    def __init__(self,client):self.client=client
    def stage(self,video:Path,thumbnail:Path,metadata:dict)->StageResult:
        vid=self.client.upload_private(video=video,title=metadata['title'],description=metadata.get('description',''),tags=metadata.get('tags',[]))
        self.client.set_thumbnail(vid,thumbnail)
        state=self.client.processing_state(vid)
        return StageResult(vid, state)
    def schedule_if_ready(self,video_id:str,publish_at:datetime)->bool:
        if self.client.processing_state(video_id)!='succeeded': return False
        self.client.schedule(video_id,publish_at); return True
