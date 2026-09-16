from __future__ import annotations
from app.collectors.live import google_news_search
from app.research.packet import build_research_packet

def research_candidate(candidate):
    query=' '.join(candidate.entities) if candidate.entities else candidate.title
    secondary=google_news_search(query,candidate.niche,limit=8)
    sources=[{'source_name':candidate.source_name,'url':candidate.canonical_url,'text':candidate.title+'. '+candidate.summary}]
    for c in secondary:
        sources.append({'source_name':c.source_name,'url':c.canonical_url,'text':c.title+'. '+c.summary})
    packet=build_research_packet(candidate.title,{'title':candidate.title,'summary':candidate.summary},sources)
    packet['entities']=list(candidate.entities)
    return packet
