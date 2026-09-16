from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json, os
from app.config import channel_config
from app.collectors.live import collect_for_niche
from app.scoring.trends import score_candidate,deduplicate_candidates
from app.research.live import research_candidate
from app.scripting.engine import OllamaScriptEngine,TemplateScriptEngine
from app.validation.facts import validate_script
from app.visuals.thumbnail import render_thumbnail
from app.experiments.allocation import choose_niche
from app.domain.models import Publication

def select_candidate(items):
    items=deduplicate_candidates(items)
    return max(items,key=score_candidate) if items else None

def record_publication(repo,episode_id,channel_id,video_id,status,created_at=None):
    created_at=created_at or datetime.now(timezone.utc)
    p=Publication(episode_id,channel_id,video_id,status,created_at)
    repo.save_publication(p)
    return p

def build_job_key(channel_id, run_date, dry_run=True, has_tts=False, has_publisher=False):
    mode='live' if (has_publisher and not dry_run) else ('render' if has_tts else 'dry')
    return f'{run_date.isoformat()}:{channel_id}:{mode}'

def run_channel(channel_id:str,repo,day_index:int,output_dir:Path,dry_run=True,script_engine=None,tts=None,publisher=None,publish_at=None):
    cfg=channel_config(channel_id); weights=repo.get_weights(channel_id)
    niche=choose_niche(cfg['niches'],day_index,45,weights or None)
    job_key=build_job_key(channel_id, datetime.now().date(), dry_run=dry_run, has_tts=bool(tts), has_publisher=bool(publisher))
    if not repo.claim_job(job_key): return {'status':'duplicate','channel':channel_id,'niche':niche}
    try:
        candidates=collect_for_niche(niche); candidate=select_candidate(candidates)
        if not candidate: repo.finish_job(job_key,'blocked_quality'); return {'status':'blocked_quality','reason':'no candidates'}
        packet=research_candidate(candidate)
        if len({s['url'] for s in packet['sources'] if s.get('url')})<2:
            repo.finish_job(job_key,'blocked_factcheck');return {'status':'blocked_factcheck','reason':'insufficient corroboration'}
        engine=script_engine or OllamaScriptEngine()
        try: script=engine.generate(packet)
        except Exception:
            if not dry_run: raise
            script=TemplateScriptEngine().generate(packet)
        check=validate_script(script,packet)
        if not check.ok:
            repo.finish_job(job_key,'blocked_factcheck',json.dumps(check.reasons));return {'status':'blocked_factcheck','reason':check.reasons}
        episode=f"{datetime.now().date().isoformat()}-{channel_id}-{niche}"
        d=Path(output_dir)/episode; d.mkdir(parents=True,exist_ok=True)
        (d/'research.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
        (d/'script.txt').write_text(script,encoding='utf-8')
        thumbs=[render_thumbnail(cfg['name'],candidate.title,d/f'thumbnail-{i}.png',cfg['brand']) for i in range(1,4)]
        result={'status':'generated','episode':episode,'channel':channel_id,'niche':niche,'title':candidate.title,'script':str(d/'script.txt'),'thumbnail':str(thumbs[0])}
        if tts:
            wav=tts.synthesize(script,d/'narration.wav'); result['audio']=str(wav)
            from app.rendering.episode import render_episode
            video=render_episode(cfg['name'],candidate.title,script,wav,d/'video.mp4',cfg['brand']);result['video']=str(video)
            if publisher and not dry_run:
                meta={'title':candidate.title,'description':candidate.summary+'\n\nSources are listed in the research packet used by AutoTube Lab.','tags':cfg['niches']}
                if publish_at:
                    staged=publisher.stage_and_schedule(video,thumbs[0],meta,publish_at)
                else:
                    staged=publisher.stage(video,thumbs[0],meta)
                result['youtube_video_id']=staged.video_id;result['youtube_status']=staged.status
                pub_status='scheduled' if (staged.status=='succeeded' and publish_at) else 'private'
                record_publication(repo,episode,channel_id,staged.video_id,pub_status)
        repo.finish_job(job_key,'succeeded',json.dumps({k:v for k,v in result.items() if k!='script'}));return result
    except Exception as e:
        repo.finish_job(job_key,'failed',json.dumps({'error':str(e)})); raise
