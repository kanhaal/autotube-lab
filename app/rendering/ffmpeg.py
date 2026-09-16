from __future__ import annotations
from pathlib import Path
import subprocess, json

def build_color_video(out:Path,seconds:int,title:str='AUTOTUBE')->Path:
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
    filt=f"drawtext=text='{title.replace(':',' ')}':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2"
    subprocess.run(['ffmpeg','-y','-f','lavfi','-i',f'color=c=0x0A0D12:s=1920x1080:d={seconds}','-vf',filt,'-r','30','-c:v','libx264','-pix_fmt','yuv420p',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def probe_video(path:Path)->dict:
    p=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,duration','-of','json',str(path)],check=True,capture_output=True,text=True)
    s=json.loads(p.stdout)['streams'][0]; return {'width':int(s['width']),'height':int(s['height']),'duration':float(s.get('duration',0) or 0)}
