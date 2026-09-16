from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import time
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
    def stage_and_schedule(self,video:Path,thumbnail:Path,metadata:dict,publish_at:datetime,poll_seconds:int=20,max_polls:int=30)->StageResult:
        result=self.stage(video,thumbnail,metadata)
        state=result.status
        polls=1
        while state in {'processing','uploaded'} and polls < max_polls:
            time.sleep(poll_seconds)
            state=self.client.processing_state(result.video_id)
            polls += 1
        if state=='succeeded':
            self.client.schedule(result.video_id,publish_at)
        return StageResult(result.video_id,state)
