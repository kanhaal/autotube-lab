from __future__ import annotations
import argparse, json, os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from app.storage.sqlite import Repository
from app.config import all_channels, channel_config
from app.analytics.learning import refresh_niche_weights
from app.analytics.youtube import refresh_channel_analytics

def _repo(args):
    r=Repository(Path(args.db));r.init();return r

def refresh_live_learning(client,repo,channel_id):
    cfg=channel_config(channel_id)
    return refresh_channel_analytics(client,repo,channel_id,cfg['niches'])

def _build_channel_tts(cfg):
    from app.narration.backend import ConfiguredTTS, select_tts_backend
    from app.narration.fallback import FallbackTTS

    voice=cfg.get('voice',{})
    profile=voice.get('profile','default')
    primary=select_tts_backend(
        voice.get('backend','chatterbox'),
        voice_profiles={profile:voice.get('settings',{})},
    )
    fallback=select_tts_backend(
        voice.get('fallback_backend','kokoro'),
        voice_profiles={profile:voice.get('fallback_settings',{})},
    )
    return ConfiguredTTS(FallbackTTS(primary,fallback),profile)

def cmd_init(args):
    r=_repo(args); print(json.dumps({'ok':True,'db':str(r.path),'channels':[c['name'] for c in all_channels()]},indent=2))

def cmd_auth(args):
    from app.publishing.google_client import authorize,GoogleYouTubeClient
    token=Path('data/oauth')/f'{args.channel}.json'; creds=authorize(Path(args.client_secrets),token); ident=GoogleYouTubeClient(creds).channel_identity()
    expected=channel_config(args.channel)['name']
    if ident['title'].lower()!=expected.lower():
        token.unlink(missing_ok=True); raise SystemExit(f'Authorized channel is {ident["title"]!r}, expected {expected!r}. Token deleted; rerun and choose the correct YouTube channel.')
    print(json.dumps({'authorized':args.channel,'youtube':ident,'token':str(token)},indent=2))

def cmd_run(args):
    from app.orchestration.daily import run_channel
    r=_repo(args); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    now=datetime.now(timezone.utc)
    day=(now.date()-datetime(2026,9,16,tzinfo=timezone.utc).date()).days
    results=[]
    for cid in ([args.channel] if args.channel!='all' else ['kernelrush','lobbysignal']):
        tts=publisher=None
        cfg=channel_config(cid)
        if args.render or args.live:
            tts=_build_channel_tts(cfg)
        if args.live:
            from app.publishing.google_client import authorize,GoogleYouTubeClient
            from app.publishing.youtube import PrivateFirstPublisher
            creds=authorize(Path(args.client_secrets),Path('data/oauth')/f'{cid}.json')
            yt_client=GoogleYouTubeClient(creds)
            refresh_live_learning(yt_client,r,cid)
            publisher=PrivateFirstPublisher(yt_client)
        publish_at=datetime.now(timezone.utc)+timedelta(hours=2) if args.live else None
        results.append(run_channel(cid,r,max(0,day),out,dry_run=not args.live,tts=tts,publisher=publisher,publish_at=publish_at,renderer=args.renderer))
    print(json.dumps(results,indent=2,default=str))

def cmd_weights(args):
    r=_repo(args); cfg=channel_config(args.channel); print(json.dumps(refresh_niche_weights(r,args.channel,cfg['niches']),indent=2))

def cmd_youtube_analytics(args):
    from app.publishing.google_client import authorize,GoogleYouTubeClient
    r=_repo(args)
    creds=authorize(Path(args.client_secrets),Path('data/oauth')/f'{args.channel}.json')
    result=refresh_live_learning(GoogleYouTubeClient(creds),r,args.channel)
    print(json.dumps(result,indent=2))

def cmd_health(args):
    import shutil
    from app.narration.health import media_health

    r=_repo(args)
    print(json.dumps({'db':str(r.path),'ffmpeg':bool(shutil.which('ffmpeg')),'ffprobe':bool(shutil.which('ffprobe')),'media':media_health(),'weights':{c['id']:r.get_weights(c['id']) for c in all_channels()},'oauth':{c['id']:(Path('data/oauth')/f"{c['id']}.json").exists() for c in all_channels()}},indent=2))

def main():
    p=argparse.ArgumentParser(prog='autotube');p.add_argument('--db',default=os.getenv('AUTOTUBE_DB','data/autotube.db'))
    sub=p.add_subparsers(dest='cmd',required=True)
    x=sub.add_parser('init');x.set_defaults(func=cmd_init)
    x=sub.add_parser('youtube-auth');x.add_argument('channel',choices=['kernelrush','lobbysignal']);x.add_argument('--client-secrets',default=os.getenv('AUTOTUBE_CLIENT_SECRETS','client_secret.json'));x.set_defaults(func=cmd_auth)
    x=sub.add_parser('run-daily');x.add_argument('--channel',default='all',choices=['all','kernelrush','lobbysignal']);x.add_argument('--output',default=os.getenv('AUTOTUBE_OUTPUT','output'));x.add_argument('--render',action='store_true');x.add_argument('--live',action='store_true');x.add_argument('--renderer',default=os.getenv('AUTOTUBE_RENDERER','legacy'),choices=['legacy','professional']);x.add_argument('--client-secrets',default=os.getenv('AUTOTUBE_CLIENT_SECRETS','client_secret.json'));x.set_defaults(func=cmd_run)
    x=sub.add_parser('refresh-weights');x.add_argument('channel',choices=['kernelrush','lobbysignal']);x.set_defaults(func=cmd_weights)
    x=sub.add_parser('refresh-youtube-analytics');x.add_argument('channel',choices=['kernelrush','lobbysignal']);x.add_argument('--client-secrets',default=os.getenv('AUTOTUBE_CLIENT_SECRETS','client_secret.json'));x.set_defaults(func=cmd_youtube_analytics)
    x=sub.add_parser('health');x.set_defaults(func=cmd_health)
    a=p.parse_args();a.func(a)
if __name__=='__main__':main()