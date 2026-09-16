from __future__ import annotations
from pathlib import Path
from datetime import datetime
SCOPES=['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/yt-analytics.readonly']

def authorize(client_secrets:Path,token_path:Path):
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError as e: raise RuntimeError('Install: pip install -e .[youtube]') from e
    creds=None
    if token_path.exists(): creds=Credentials.from_authorized_user_file(str(token_path),SCOPES)
    if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
    if not creds or not creds.valid:
        flow=InstalledAppFlow.from_client_secrets_file(str(client_secrets),SCOPES); creds=flow.run_local_server(port=0)
    token_path.parent.mkdir(parents=True,exist_ok=True); token_path.write_text(creds.to_json(),encoding='utf-8'); return creds

class GoogleYouTubeClient:
    def __init__(self,creds):
        from googleapiclient.discovery import build
        self.youtube=build('youtube','v3',credentials=creds,cache_discovery=False)
        self.analytics=build('youtubeAnalytics','v2',credentials=creds,cache_discovery=False)
    def channel_identity(self):
        r=self.youtube.channels().list(part='snippet',mine=True).execute(); item=r['items'][0]; return {'id':item['id'],'title':item['snippet']['title']}
    def upload_private(self,video,title,description,tags=None):
        from googleapiclient.http import MediaFileUpload
        body={'snippet':{'title':title[:100],'description':description[:5000],'tags':(tags or [])[:30]},'status':{'privacyStatus':'private','selfDeclaredMadeForKids':False}}
        req=self.youtube.videos().insert(part='snippet,status',body=body,media_body=MediaFileUpload(str(video),chunksize=-1,resumable=True)); return req.execute()['id']
    def set_thumbnail(self,video_id,thumbnail):
        from googleapiclient.http import MediaFileUpload
        self.youtube.thumbnails().set(videoId=video_id,media_body=MediaFileUpload(str(thumbnail))).execute()
    def processing_state(self,video_id):
        r=self.youtube.videos().list(part='processingDetails,status',id=video_id).execute()
        if not r.get('items'):return 'missing'
        return r['items'][0].get('processingDetails',{}).get('processingStatus','succeeded')
    def schedule(self,video_id,publish_at:datetime):
        body={'id':video_id,'status':{'privacyStatus':'private','publishAt':publish_at.isoformat().replace('+00:00','Z'),'selfDeclaredMadeForKids':False}}
        self.youtube.videos().update(part='status',body=body).execute()
    def analytics_row(self,video_id,start_date,end_date):
        metrics='views,estimatedMinutesWatched,averageViewPercentage,subscribersGained,subscribersLost'
        r=self.analytics.reports().query(ids='channel==MINE',startDate=start_date,endDate=end_date,metrics=metrics,filters=f'video=={video_id}').execute()
        row=(r.get('rows') or [[0,0,0,0,0]])[0]
        return {'views':int(row[0]),'watch_minutes':float(row[1]),'retention':float(row[2])/100,'subs_gained':int(row[3]),'subs_lost':int(row[4])}
