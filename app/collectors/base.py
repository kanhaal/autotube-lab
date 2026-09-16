from __future__ import annotations
import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

def get_json(url:str,headers:dict|None=None,timeout=20):
    h={'User-Agent':'AutoTubeLab/0.1 (+https://github.com/kanhaal/autotube-lab)'}; h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))

def get_text(url:str,timeout=20):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AutoTubeLab/0.1'}),timeout=timeout) as r:return r.read().decode('utf-8','replace')

def parse_dt(value):
    if not value:return datetime.now(timezone.utc)
    if isinstance(value,(int,float)):return datetime.fromtimestamp(value,tz=timezone.utc)
    try:return datetime.fromisoformat(str(value).replace('Z','+00:00'))
    except Exception:
        try:return parsedate_to_datetime(str(value)).astimezone(timezone.utc)
        except Exception:return datetime.now(timezone.utc)

def parse_rss(xml:str):
    root=ET.fromstring(xml); out=[]
    for item in root.findall('.//item'):
        def t(name):
            n=item.find(name); return ''.join(n.itertext()).strip() if n is not None else ''
        out.append({'title':t('title'),'url':t('link'),'published':t('pubDate'),'summary':t('description')})
    if out:return out
    ns={'a':'http://www.w3.org/2005/Atom'}
    for e in root.findall('.//a:entry',ns):
        title=e.find('a:title',ns); link=e.find('a:link',ns); updated=e.find('a:updated',ns); summary=e.find('a:summary',ns)
        out.append({'title': ''.join(title.itertext()).strip() if title is not None else '', 'url':link.get('href','') if link is not None else '', 'published':updated.text if updated is not None else '', 'summary':''.join(summary.itertext()).strip() if summary is not None else ''})
    return out
