from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def _font(size):
    for p in ['C:/Windows/Fonts/arialbd.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def render_thumbnail(channel:str,headline:str,out:Path,brand:dict)->Path:
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new('RGB',(1280,720),brand['background']); d=ImageDraw.Draw(im)
    d.rectangle((0,0,18,720),fill=brand['accent']); d.text((72,64),channel.upper(),fill=brand['accent'],font=_font(44))
    words=headline.upper().split()[:5]
    y=180
    for line in [' '.join(words[:3]),' '.join(words[3:])]:
        if line:d.text((72,y),line,fill=brand['foreground'],font=_font(86)); y+=110
    im.save(out,quality=95); return out
