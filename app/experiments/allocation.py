from __future__ import annotations
import hashlib, statistics

_METRIC_WEIGHTS={'retention':.30,'views_ratio':.25,'ctr':.20,'subs_per_1k':.15,'watch_per_1k_imp':.10}
_METRIC_TARGETS={'retention':.55,'views_ratio':1.0,'ctr':.06,'subs_per_1k':8.0,'watch_per_1k_imp':100.0}

def performance_score(metrics: dict[str,float|None]) -> float:
    vals=[]
    for k,w in _METRIC_WEIGHTS.items():
        v=metrics.get(k)
        if v is not None:
            vals.append((w,max(0,float(v))/_METRIC_TARGETS[k]))
    if not vals: return 0.0
    total=sum(w for w,_ in vals)
    return sum((w/total)*min(v,3.0) for w,v in vals)

def compute_niche_weights(scores: dict[str,list[float]], floor=.12, cap=.80) -> dict[str,float]:
    if not scores: return {}
    med={k:(statistics.median(v) if v else 1.0) for k,v in scores.items()}
    positive={k:max(.01,v) for k,v in med.items()}
    total=sum(positive.values())
    raw={k:v/total for k,v in positive.items()}
    n=len(raw)
    if floor*n>=1: return {k:1/n for k in raw}
    w={k:max(floor,min(cap,v)) for k,v in raw.items()}
    for _ in range(20):
        s=sum(w.values())
        if abs(s-1)<1e-9: break
        if s>1:
            adjustable=[k for k,v in w.items() if v>floor+1e-12]
            if not adjustable: break
            excess=s-1
            room=sum(w[k]-floor for k in adjustable)
            for k in adjustable: w[k]-=excess*(w[k]-floor)/room
        else:
            adjustable=[k for k,v in w.items() if v<cap-1e-12]
            if not adjustable: break
            need=1-s
            room=sum(cap-w[k] for k in adjustable)
            for k in adjustable: w[k]+=need*(cap-w[k])/room
    s=sum(w.values())
    return {k:v/s for k,v in w.items()}

def choose_niche(niches:list[str], day_index:int, exploration_days:int=45, weights:dict[str,float]|None=None)->str:
    if not niches: raise ValueError('no niches')
    if day_index<exploration_days or not weights:
        return niches[day_index%len(niches)]
    r=int(hashlib.sha256(str(day_index).encode()).hexdigest()[:12],16)/(16**12)
    acc=0.0
    for n in niches:
        acc += weights.get(n,0)
        if r<=acc: return n
    return niches[-1]
