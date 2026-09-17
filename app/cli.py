from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.analytics.learning import refresh_niche_weights
from app.analytics.youtube import refresh_channel_analytics
from app.config import all_channels, channel_config
from app.storage.sqlite import Repository


def _repo(args):
    repository = Repository(Path(args.db))
    repository.init()
    return repository


def refresh_live_learning(client, repo, channel_id):
    cfg = channel_config(channel_id)
    return refresh_channel_analytics(client, repo, channel_id, cfg["niches"])


def _build_channel_tts(cfg):
    from app.narration.backend import ConfiguredTTS, select_tts_backend
    from app.narration.fallback import FallbackTTS

    voice = cfg.get("voice", {})
    profile = voice.get("profile", "default")
    primary_name = os.getenv(
        "AUTOTUBE_TTS_BACKEND",
        voice.get("backend", "chatterbox"),
    ).strip().lower()
    primary = select_tts_backend(
        primary_name,
        voice_profiles={profile: voice.get("settings", {})},
    )
    fallback = select_tts_backend(
        voice.get("fallback_backend", "kokoro"),
        voice_profiles={profile: voice.get("fallback_settings", {})},
    )
    return ConfiguredTTS(FallbackTTS(primary, fallback), profile)


def cmd_init(args):
    repository = _repo(args)
    print(
        json.dumps(
            {
                "ok": True,
                "db": str(repository.path),
                "channels": [channel["name"] for channel in all_channels()],
            },
            indent=2,
        )
    )


def cmd_auth(args):
    from app.publishing.google_client import GoogleYouTubeClient, authorize

    token = Path("data/oauth") / f"{args.channel}.json"
    creds = authorize(Path(args.client_secrets), token)
    ident = GoogleYouTubeClient(creds).channel_identity()
    expected = channel_config(args.channel)["name"]
    if ident["title"].lower() != expected.lower():
        token.unlink(missing_ok=True)
        raise SystemExit(
            f"Authorized channel is {ident['title']!r}, expected {expected!r}. "
            "Token deleted; rerun and choose the correct YouTube channel."
        )
    print(json.dumps({"authorized": args.channel, "youtube": ident, "token": str(token)}, indent=2))


def cmd_run(args):
    from app.orchestration.daily import run_channel

    repository = _repo(args)
    if args.live and not repository.renderer_approved(args.renderer):
        raise SystemExit(
            f"{args.renderer} renderer is not approved for live publishing. "
            f"Review supervised renders, then run: autotube approve-renderer {args.renderer}"
        )

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    day = (now.date() - datetime(2026, 9, 16, tzinfo=timezone.utc).date()).days
    results = []
    channel_ids = [args.channel] if args.channel != "all" else ["kernelrush", "lobbysignal"]
    for channel_id in channel_ids:
        tts = publisher = None
        cfg = channel_config(channel_id)
        if args.render or args.live:
            tts = _build_channel_tts(cfg)
        if args.live:
            from app.publishing.google_client import GoogleYouTubeClient, authorize
            from app.publishing.youtube import PrivateFirstPublisher

            creds = authorize(
                Path(args.client_secrets),
                Path("data/oauth") / f"{channel_id}.json",
            )
            yt_client = GoogleYouTubeClient(creds)
            refresh_live_learning(yt_client, repository, channel_id)
            publisher = PrivateFirstPublisher(yt_client)
        publish_at = datetime.now(timezone.utc) + timedelta(hours=2) if args.live else None
        results.append(
            run_channel(
                channel_id,
                repository,
                max(0, day),
                out,
                dry_run=not args.live,
                tts=tts,
                publisher=publisher,
                publish_at=publish_at,
                renderer=args.renderer,
            )
        )
    print(json.dumps(results, indent=2, default=str))


def cmd_renderer_status(args):
    repository = _repo(args)
    print(
        json.dumps(
            {
                "legacy": {"approved": repository.renderer_approved("legacy")},
                "professional": {"approved": repository.renderer_approved("professional")},
            },
            indent=2,
        )
    )


def cmd_approve_renderer(args):
    repository = _repo(args)
    repository.set_renderer_approved(args.renderer, True)
    print(json.dumps({"renderer": args.renderer, "approved": True}, indent=2))


def cmd_media_smoke(args):
    from app.health.media import run_media_smoke

    print(json.dumps(run_media_smoke(deep=args.deep), indent=2))


def cmd_weights(args):
    repository = _repo(args)
    cfg = channel_config(args.channel)
    print(
        json.dumps(
            refresh_niche_weights(repository, args.channel, cfg["niches"]),
            indent=2,
        )
    )


def cmd_youtube_analytics(args):
    from app.publishing.google_client import GoogleYouTubeClient, authorize

    repository = _repo(args)
    creds = authorize(
        Path(args.client_secrets),
        Path("data/oauth") / f"{args.channel}.json",
    )
    result = refresh_live_learning(GoogleYouTubeClient(creds), repository, args.channel)
    print(json.dumps(result, indent=2))


def cmd_health(args):
    import shutil

    from app.narration.health import media_health

    repository = _repo(args)
    print(
        json.dumps(
            {
                "db": str(repository.path),
                "ffmpeg": bool(shutil.which("ffmpeg")),
                "ffprobe": bool(shutil.which("ffprobe")),
                "media": media_health(),
                "weights": {
                    channel["id"]: repository.get_weights(channel["id"])
                    for channel in all_channels()
                },
                "oauth": {
                    channel["id"]: (Path("data/oauth") / f"{channel['id']}.json").exists()
                    for channel in all_channels()
                },
                "renderers": {
                    "legacy": {"approved": repository.renderer_approved("legacy")},
                    "professional": {
                        "approved": repository.renderer_approved("professional")
                    },
                },
            },
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser(prog="autotube")
    parser.add_argument("--db", default=os.getenv("AUTOTUBE_DB", "data/autotube.db"))
    sub = parser.add_subparsers(dest="cmd", required=True)

    command = sub.add_parser("init")
    command.set_defaults(func=cmd_init)

    command = sub.add_parser("youtube-auth")
    command.add_argument("channel", choices=["kernelrush", "lobbysignal"])
    command.add_argument(
        "--client-secrets",
        default=os.getenv("AUTOTUBE_CLIENT_SECRETS", "client_secret.json"),
    )
    command.set_defaults(func=cmd_auth)

    command = sub.add_parser("run-daily")
    command.add_argument(
        "--channel",
        default="all",
        choices=["all", "kernelrush", "lobbysignal"],
    )
    command.add_argument("--output", default=os.getenv("AUTOTUBE_OUTPUT", "output"))
    command.add_argument("--render", action="store_true")
    command.add_argument("--live", action="store_true")
    command.add_argument(
        "--renderer",
        default=os.getenv("AUTOTUBE_RENDERER", "legacy"),
        choices=["legacy", "professional"],
    )
    command.add_argument(
        "--client-secrets",
        default=os.getenv("AUTOTUBE_CLIENT_SECRETS", "client_secret.json"),
    )
    command.set_defaults(func=cmd_run)

    command = sub.add_parser("renderer-status")
    command.set_defaults(func=cmd_renderer_status)

    command = sub.add_parser("approve-renderer")
    command.add_argument("renderer", choices=["professional"])
    command.set_defaults(func=cmd_approve_renderer)

    command = sub.add_parser("media-smoke")
    command.add_argument("--deep", action="store_true")
    command.set_defaults(func=cmd_media_smoke)

    command = sub.add_parser("refresh-weights")
    command.add_argument("channel", choices=["kernelrush", "lobbysignal"])
    command.set_defaults(func=cmd_weights)

    command = sub.add_parser("refresh-youtube-analytics")
    command.add_argument("channel", choices=["kernelrush", "lobbysignal"])
    command.add_argument(
        "--client-secrets",
        default=os.getenv("AUTOTUBE_CLIENT_SECRETS", "client_secret.json"),
    )
    command.set_defaults(func=cmd_youtube_analytics)

    command = sub.add_parser("health")
    command.set_defaults(func=cmd_health)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
