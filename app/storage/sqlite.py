from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from app.domain.models import Publication, AnalyticsSnapshot
class Repository:
    def __init__(self,path:Path|str): self.path=Path(path)
    def _c(self): self.path.parent.mkdir(parents=True,exist_ok=True); return sqlite3.connect(self.path)
    def init(self):
        with self._c() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS publications(episode_id TEXT PRIMARY KEY,channel_id TEXT,video_id TEXT,status TEXT,created_at TEXT);
            CREATE TABLE IF NOT EXISTS analytics(video_id TEXT,channel_id TEXT,niche TEXT,published_at TEXT,snapshot_at TEXT,impressions INTEGER,ctr REAL,views INTEGER,retention REAL,watch_minutes REAL,subs_gained INTEGER,subs_lost INTEGER,PRIMARY KEY(video_id,snapshot_at));
            CREATE TABLE IF NOT EXISTS niche_weights(channel_id TEXT,niche TEXT,weight REAL,updated_at TEXT,PRIMARY KEY(channel_id,niche));
            CREATE TABLE IF NOT EXISTS jobs(job_key TEXT PRIMARY KEY,status TEXT,updated_at TEXT,details TEXT);
            ''')
    def save_publication(self,p:Publication):
        with self._c() as c: c.execute('INSERT OR REPLACE INTO publications VALUES(?,?,?,?,?)',(p.episode_id,p.channel_id,p.youtube_video_id,p.status,p.created_at.isoformat()))
    def get_publication(self,eid:str):
        with self._c() as c: r=c.execute('SELECT * FROM publications WHERE episode_id=?',(eid,)).fetchone()
        return Publication(r[0],r[1],r[2],r[3],datetime.fromisoformat(r[4])) if r else None
    def list_publications(self,channel_id:str):
        with self._c() as c: rows=c.execute('SELECT * FROM publications WHERE channel_id=? ORDER BY created_at',(channel_id,)).fetchall()
        return [Publication(r[0],r[1],r[2],r[3],datetime.fromisoformat(r[4])) for r in rows]
    def save_analytics(self,a:AnalyticsSnapshot):
        with self._c() as c:c.execute('INSERT OR REPLACE INTO analytics VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(a.video_id,a.channel_id,a.niche,a.published_at.isoformat(),a.snapshot_at.isoformat(),a.impressions,a.ctr,a.views,a.retention,a.watch_minutes,a.subscribers_gained,a.subscribers_lost))
    def mature_analytics(self,channel_id:str,now:datetime|None=None,min_age_days:int=7):
        now=now or datetime.now(timezone.utc); cutoff=now-timedelta(days=min_age_days)
        with self._c() as c: rows=c.execute('SELECT * FROM analytics WHERE channel_id=? AND published_at<=? ORDER BY published_at',(channel_id,cutoff.isoformat())).fetchall()
        return [AnalyticsSnapshot(r[0],r[1],r[2],datetime.fromisoformat(r[3]),datetime.fromisoformat(r[4]),r[5],r[6],r[7],r[8],r[9],r[10],r[11]) for r in rows]
    def save_weights(self,channel_id:str,weights:dict[str,float]):
        now=datetime.now(timezone.utc).isoformat()
        with self._c() as c:
            for n,w in weights.items(): c.execute('INSERT OR REPLACE INTO niche_weights VALUES(?,?,?,?)',(channel_id,n,w,now))
    def get_weights(self,channel_id:str)->dict[str,float]:
        with self._c() as c: rows=c.execute('SELECT niche,weight FROM niche_weights WHERE channel_id=?',(channel_id,)).fetchall()
        return dict(rows)
    def claim_job(self,key:str)->bool:
        try:
            with self._c() as c:c.execute('INSERT INTO jobs VALUES(?,?,?,?)',(key,'running',datetime.now(timezone.utc).isoformat(),'{}'))
            return True
        except sqlite3.IntegrityError:return False
    def finish_job(self,key,status,details='{}'):
        with self._c() as c:c.execute('UPDATE jobs SET status=?,updated_at=?,details=? WHERE job_key=?',(status,datetime.now(timezone.utc).isoformat(),details,key))
