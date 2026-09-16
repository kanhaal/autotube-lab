from __future__ import annotations
from datetime import datetime, timezone

def build_research_packet(topic:str,candidate:dict,sources:list[dict])->dict:
    seen=set(); clean=[]
    for s in sources:
        u=s.get('url','')
        if u in seen: continue
        seen.add(u); clean.append({'source_name':s.get('source_name','Unknown'),'url':u,'text':s.get('text','').strip()})
    return {'topic':topic,'candidate':candidate,'sources':clean,'built_at':datetime.now(timezone.utc).isoformat()}
