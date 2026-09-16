from __future__ import annotations
import json, urllib.request

SYSTEM_PROMPT='''You are the writer for a high-retention faceless YouTube news channel. Use ONLY the supplied research packet. Never invent numbers, dates, quotes, causality, or capabilities. Write 650-900 spoken words: 5-12 second hook, immediate context, 3-5 clear sections, a section literally titled "Why it matters", and a tight close. Explain rather than hype. Attribute uncertainty. No generic intro, no like/subscribe filler.'''

class TemplateScriptEngine:
    """Offline fallback. Safe and deterministic; live production should prefer Ollama."""
    def generate(self,packet:dict)->str:
        topic=packet['topic']; src=packet['sources']
        evidence=' '.join(s['text'] for s in src if s.get('text'))
        sentences=[x.strip() for x in evidence.replace('\n',' ').split('.') if x.strip()]
        if not sentences: sentences=[packet.get('candidate',{}).get('summary','There is not enough source detail yet')]
        hook=f"{topic} is moving quickly, but the useful question is what actually changed and why people are paying attention."
        blocks=[hook,"Here is the signal without the noise."]
        heads=['What happened','What the sources actually say','The practical angle','Why it matters','What to watch next']
        for i,h in enumerate(heads):
            blocks.append(f"\n{h}\n")
            base=sentences[i%len(sentences)]
            expansion=(f"{base}. This matters in context because the change affects how people discover, evaluate, or use the product. "
                       f"The important distinction is between what has been directly reported and what is only being inferred from attention around the story. "
                       f"Based on the available sources, the safest conclusion is to focus on the documented change itself rather than extrapolating beyond the evidence. ")
            blocks.extend([expansion]*3)
        blocks.append("\nThe story is still developing. The next meaningful signal will be concrete usage, follow-up releases, or an official update rather than raw hype.")
        return '\n'.join(blocks)

class OllamaScriptEngine:
    def __init__(self,model='qwen2.5:7b-instruct',base_url='http://127.0.0.1:11434'):
        self.model=model; self.base=base_url.rstrip('/')
    def generate(self,packet:dict)->str:
        payload=json.dumps({'model':self.model,'stream':False,'prompt':SYSTEM_PROMPT+'\n\nRESEARCH PACKET:\n'+json.dumps(packet,ensure_ascii=False) }).encode()
        req=urllib.request.Request(self.base+'/api/generate',data=payload,headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=180) as r: data=json.loads(r.read())
        return data['response'].strip()
