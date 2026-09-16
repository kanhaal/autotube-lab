from __future__ import annotations
import re
from app.domain.models import StoryCandidate

def _tokens(text:str)->set[str]:
    return {w for w in re.findall(r'[a-z0-9]{4,}',text.lower()) if w not in {'with','from','this','that','have','will','news'}}

def research_supports_candidate(candidate:StoryCandidate, all_candidates:list[StoryCandidate])->bool:
    seed=_tokens(candidate.title+' '+candidate.summary+' '+' '.join(candidate.entities))
    supporting=set()
    for c in all_candidates:
        if c.id==candidate.id: continue
        if not seed: continue
        overlap=len(seed & _tokens(c.title+' '+c.summary+' '+' '.join(c.entities)))/max(1,len(seed))
        if overlap>=.20:
            supporting.add(c.source_name)
    return len(supporting)>=1
