from __future__ import annotations
from dataclasses import dataclass
import re
@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    reasons: tuple[str,...]=()

def validate_script(script:str, packet:dict)->ValidationResult:
    corpus=' '.join(s.get('text','') for s in packet.get('sources',[])).lower()
    reasons=[]
    nums=re.findall(r'\b\d[\d,.]*%?\b', script)
    for n in nums:
        if n.lower() not in corpus:
            reasons.append(f'unsupported numeric claim: {n}')
    if len(packet.get('sources',[]))<2: reasons.append('fewer than two sources')
    if len(script.split())<5: reasons.append('script too short')
    return ValidationResult(not reasons, tuple(reasons))
