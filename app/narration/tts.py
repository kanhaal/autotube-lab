from __future__ import annotations
from pathlib import Path
import subprocess, shutil
class WindowsSapiTTS:
    def synthesize(self,text:str,out:Path,rate:int=0)->Path:
        out=Path(out).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
        if shutil.which('powershell') is None and shutil.which('pwsh') is None: raise RuntimeError('PowerShell required for Windows SAPI TTS')
        ps=shutil.which('powershell') or shutil.which('pwsh')
        escaped=text.replace("'","''")
        script=("Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$s.Rate={int(rate)}; $s.SetOutputToWaveFile('{str(out).replace(chr(39),chr(39)*2)}'); $s.Speak('{escaped}'); $s.Dispose()")
        subprocess.run([ps,'-NoProfile','-Command',script],check=True); return out
class PiperTTS:
    def __init__(self,model:Path,exe='piper'):self.model=Path(model);self.exe=exe
    def synthesize(self,text:str,out:Path)->Path:
        out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run([self.exe,'--model',str(self.model),'--output_file',str(out)],input=text,text=True,check=True);return out
