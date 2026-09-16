from __future__ import annotations
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def channel_config(channel_id:str)->dict:
    return yaml.safe_load((ROOT/'config'/'channels'/f'{channel_id}.yml').read_text(encoding='utf-8'))
def all_channels():return [channel_config('kernelrush'),channel_config('lobbysignal')]
