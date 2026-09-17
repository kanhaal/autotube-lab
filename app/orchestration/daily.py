from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from app.collectors.live import collect_for_niche
from app.config import channel_config
from app.domain.models import Publication
from app.experiments.allocation import choose_niche
from app.research.live import research_candidate
from app.scoring.trends import deduplicate_candidates, score_candidate
from app.scripting.engine import TemplateScriptEngine
from app.validation.facts import validate_script
from app.visuals.thumbnail import render_thumbnail


def select_candidate(items):
    items = deduplicate_candidates(items)
    return max(items, key=score_candidate) if items else None


def record_publication(repo, episode_id, channel_id, video_id, status, created_at=None):
    created_at = created_at or datetime.now(timezone.utc)
    publication = Publication(episode_id, channel_id, video_id, status, created_at)
    repo.save_publication(publication)
    return publication


def build_job_key(channel_id, run_date, dry_run=True, has_tts=False, has_publisher=False):
    mode = "live" if (has_publisher and not dry_run) else ("render" if has_tts else "dry")
    return f"{run_date.isoformat()}:{channel_id}:{mode}"


def _source_description(summary: str, packet: dict) -> str:
    lines = []
    seen = set()
    for source in packet.get("sources", []):
        url = str(source.get("url", "")).strip()
        if not url or url in seen:
            continue
        seen.add(url)
        name = str(source.get("source_name", "")).strip()
        lines.append(f"- {name}: {url}" if name else f"- {url}")
    if not lines:
        return summary
    return summary.rstrip() + "\n\nSources:\n" + "\n".join(lines)


def _finish_blocked_production(repo, job_key, channel_id, niche, production):
    issues = [
        {"code": issue.code, "message": issue.message, "fatal": issue.fatal}
        for issue in production.quality_report.issues
    ]
    fact_failed = any(issue["code"] == "fact_gate_failed" for issue in issues)
    status = "blocked_factcheck" if fact_failed else "blocked_quality"
    repo.finish_job(job_key, status, json.dumps(issues))
    return {
        "status": status,
        "channel": channel_id,
        "niche": niche,
        "quality_issues": issues,
    }


def _professional_result(episode, channel_id, niche, title, directory, production):
    state = production.state
    thumbs = list(production.thumbnails)
    if production.long_video is None or not thumbs:
        raise RuntimeError("publishable professional production is missing video or thumbnail")
    result = {
        "status": "generated",
        "episode": episode,
        "channel": channel_id,
        "niche": niche,
        "title": title,
        "script": str(directory / "script.txt"),
        "thumbnail": str(thumbs[0]),
        "renderer": "professional",
        "video": str(production.long_video),
        "quality_ok": production.quality_report.ok,
    }
    if state.get("editorial_bundle") is not None:
        result["editorial"] = str(directory / "editorial.json")
        result["scenes"] = str(directory / "scenes.json")
    if state.get("asset_manifest") is not None:
        result["asset_manifest"] = str(directory / "asset-manifest.json")
    if state.get("audio") is not None:
        result["audio"] = str(state["audio"])
    if production.short_video is not None:
        result["short_video"] = str(production.short_video)
    if state.get("short_error"):
        result["short_error"] = str(state["short_error"])
    return result, production.long_video, thumbs


def run_channel(
    channel_id: str,
    repo,
    day_index: int,
    output_dir: Path,
    dry_run=True,
    script_engine=None,
    editorial_llm=None,
    asset_capturer=None,
    tts=None,
    publisher=None,
    publish_at=None,
    renderer=None,
):
    from app.rendering.pipeline import renderer_mode

    mode = renderer_mode(renderer)
    cfg = channel_config(channel_id)
    weights = repo.get_weights(channel_id)
    niche = choose_niche(cfg["niches"], day_index, 45, weights or None)
    today = datetime.now(timezone.utc).date()
    job_key = build_job_key(
        channel_id,
        today,
        dry_run=dry_run,
        has_tts=bool(tts),
        has_publisher=bool(publisher),
    )
    if not repo.claim_job(job_key):
        return {"status": "duplicate", "channel": channel_id, "niche": niche}

    try:
        candidates = collect_for_niche(niche)
        candidate = select_candidate(candidates)
        if not candidate:
            repo.finish_job(job_key, "blocked_quality")
            return {"status": "blocked_quality", "reason": "no candidates"}

        packet = research_candidate(candidate)
        if len({source["url"] for source in packet["sources"] if source.get("url")}) < 2:
            repo.finish_job(job_key, "blocked_factcheck")
            return {"status": "blocked_factcheck", "reason": "insufficient corroboration"}

        episode = f"{today.isoformat()}-{channel_id}-{niche}"
        directory = Path(output_dir) / episode
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "research.json").write_text(
            json.dumps(packet, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        video = None
        thumbs = []
        result = None

        if tts and mode == "professional" and script_engine is None:
            from app.orchestration.production import produce_professional_episode

            production = produce_professional_episode(
                channel_id=channel_id,
                channel_cfg=cfg,
                packet=packet,
                title=candidate.title,
                output_dir=directory,
                tts=tts,
                editorial_llm=editorial_llm,
                asset_capturer=asset_capturer,
            )
            if not production.publishable:
                return _finish_blocked_production(
                    repo,
                    job_key,
                    channel_id,
                    niche,
                    production,
                )
            result, video, thumbs = _professional_result(
                episode,
                channel_id,
                niche,
                candidate.title,
                directory,
                production,
            )
        else:
            editorial_bundle = None
            scene_plan = None
            if script_engine is not None:
                try:
                    script = script_engine.generate(packet)
                except (OSError, TimeoutError, RuntimeError, ValueError, KeyError):
                    if not dry_run:
                        raise
                    script = TemplateScriptEngine().generate(packet)
            else:
                from app.orchestration.editorial import prepare_editorial

                editorial_bundle, scene_plan = prepare_editorial(packet, channel_id, editorial_llm)
                script = editorial_bundle.script

            check = validate_script(script, packet)
            if not check.ok:
                repo.finish_job(job_key, "blocked_factcheck", json.dumps(check.reasons))
                return {"status": "blocked_factcheck", "reason": check.reasons}

            (directory / "script.txt").write_text(script, encoding="utf-8")
            asset_manifest = None
            if editorial_bundle is not None and scene_plan is not None:
                (directory / "editorial.json").write_text(
                    json.dumps(asdict(editorial_bundle), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                (directory / "scenes.json").write_text(
                    json.dumps(asdict(scene_plan), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                from app.orchestration.editorial import prepare_episode_assets

                asset_manifest = prepare_episode_assets(
                    scene_plan,
                    packet,
                    cfg,
                    directory,
                    asset_capturer,
                )

            if mode == "professional" and scene_plan is not None and asset_manifest is not None:
                from app.visuals.thumbnail_v2 import render_thumbnail_variants

                thumbs = list(
                    render_thumbnail_variants(
                        cfg,
                        candidate.title,
                        scene_plan,
                        asset_manifest,
                        directory / "thumbnails",
                        count=5,
                    )
                )
            else:
                thumbs = [
                    render_thumbnail(
                        cfg["name"],
                        candidate.title,
                        directory / f"thumbnail-{index}.png",
                        cfg["brand"],
                    )
                    for index in range(1, 4)
                ]

            result = {
                "status": "generated",
                "episode": episode,
                "channel": channel_id,
                "niche": niche,
                "title": candidate.title,
                "script": str(directory / "script.txt"),
                "thumbnail": str(thumbs[0]),
            }
            if editorial_bundle is not None:
                result["editorial"] = str(directory / "editorial.json")
                result["scenes"] = str(directory / "scenes.json")
            if asset_manifest is not None:
                result["asset_manifest"] = str(directory / "asset-manifest.json")

            if tts:
                wav = tts.synthesize(script, directory / "narration.wav")
                result["audio"] = str(wav)
                from app.rendering.episode import render_episode

                video = render_episode(
                    cfg["name"],
                    candidate.title,
                    script,
                    wav,
                    directory / "video.mp4",
                    cfg["brand"],
                )
                result["video"] = str(video)

        if video is not None and publisher and not dry_run:
            if mode == "professional" and not repo.renderer_approved("professional"):
                result["status"] = "blocked_publish"
                result["publish_blocked"] = "renderer_unapproved"
                repo.finish_job(
                    job_key,
                    "blocked_publish",
                    json.dumps({"reason": "renderer_unapproved"}),
                )
                return result

            meta = {
                "title": candidate.title,
                "description": _source_description(candidate.summary, packet),
                "tags": cfg["niches"],
            }
            if publish_at:
                staged = publisher.stage_and_schedule(video, thumbs[0], meta, publish_at)
            else:
                staged = publisher.stage(video, thumbs[0], meta)
            result["youtube_video_id"] = staged.video_id
            result["youtube_status"] = staged.status
            pub_status = "scheduled" if (staged.status == "succeeded" and publish_at) else "private"
            record_publication(
                repo,
                episode,
                channel_id,
                staged.video_id,
                pub_status,
            )

        repo.finish_job(
            job_key,
            "succeeded",
            json.dumps({key: value for key, value in result.items() if key != "script"}),
        )
        return result
    except Exception as exc:  # noqa: BLE001 - job boundary records every failure, then re-raises it
        repo.finish_job(job_key, "failed", json.dumps({"error": str(exc)}))
        raise
