from __future__ import annotations
from pathlib import Path
import subprocess, json
from PIL import Image, ImageDraw, ImageFont

def _font(size):
    for p in ['C:/Windows/Fonts/arialbd.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def audio_duration(path:Path)->float:
    p=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path)],capture_output=True,text=True,check=True)
    return float(json.loads(p.stdout)['format']['duration'])

def render_episode(channel:str,title:str,script:str,audio:Path,out:Path,brand:dict)->Path:
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
    bg=out.with_suffix('.scene.png')
    im=Image.new('RGB',(1920,1080),brand['background']); d=ImageDraw.Draw(im)
    d.rectangle((0,0,22,1080),fill=brand['accent'])
    d.text((100,90),channel.upper(),font=_font(52),fill=brand['accent'])
    words=title.upper().split(); lines=[' '.join(words[i:i+5]) for i in range(0,min(len(words),15),5)]
    y=300
    for line in lines:d.text((100,y),line,font=_font(92),fill=brand['foreground']); y+=120
    d.text((100,900),'DAILY SIGNAL • SOURCE-VERIFIED',font=_font(34),fill=brand.get('secondary',brand['accent']))
    im.save(bg)
    dur=audio_duration(audio)
    vf="scale=2048:1152,zoompan=z='min(zoom+0.00018,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30"
    subprocess.run(['ffmpeg','-y','-loop','1','-i',str(bg),'-i',str(audio),'-vf',vf,'-t',f'{dur:.3f}','-c:v','libx264','-preset','medium','-crf','20','-c:a','aac','-b:a','192k','-pix_fmt','yuv420p','-shortest',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    bg.unlink(missing_ok=True); return out
