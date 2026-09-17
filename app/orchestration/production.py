from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Mapping

from app.quality.models import QualityIssue, QualityReport

ProductionState = dict[str, Any]
StageResult = Mapping[str, Any] | None
Stage = Callable[[ProductionState], StageResult]


@dataclass(frozen=True)
class ProductionStages:
    editorial: Stage
    assets: Stage
    narration: Stage
    captions: Stage
    audio: Stage
    render: Stage
    thumbnails: Stage
    qa: Stage


@dataclass(frozen=True)
class ProductionResult:
    state: ProductionState
    quality_report: QualityReport

    @property
    def publishable(self) -> bool:
        return self.quality_report.ok

    @property
    def long_video(self) -> Path | None:
        value = self.state.get("long_video")
        return Path(value) if value else None

    @property
    def short_video(self) -> Path | None:
        value = self.state.get("short_video")
        return Path(value) if value else None

    @property
    def thumbnails(self) -> tuple[Path, ...]:
        return tuple(Path(path) for path in self.state.get("thumbnails", ()))


_STAGE_NAMES = (
    "editorial",
    "assets",
    "narration",
    "captions",
    "audio",
    "render",
    "thumbnails",
    "qa",
)


def produce_episode(seed: Mapping[str, Any], stages: ProductionStages) -> ProductionResult:
    """Run production stages in the fixed professional production order."""

    state: ProductionState = dict(seed)
    for name in _STAGE_NAMES:
        update = getattr(stages, name)(state)
        if update is not None:
            state.update(dict(update))

    report = state.get("quality_report")
    if not isinstance(report, QualityReport):
        raise TypeError("qa stage must provide a QualityReport as quality_report")
    return ProductionResult(state=state, quality_report=report)


def apply_visual_review(
    result: ProductionResult,
    *,
    channel_id: str,
    output_dir: Path,
    stages: ProductionStages,
    llm,
    contact_sheet_builder=None,
    critic=None,
    visual_corrector=None,
) -> ProductionResult:
    """Run advisory visual QA after hard QA, with at most one opt-in correction rerender."""

    if not result.quality_report.ok or result.long_video is None or llm is None:
        return result
    if int(result.state.get("visual_correction_attempts", 0) or 0) >= 1:
        return result

    from app.quality.contact_sheet import build_contact_sheet
    from app.quality.visual_critic import critique_contact_sheet

    state = dict(result.state)
    build_sheet = contact_sheet_builder or build_contact_sheet
    review = critic or critique_contact_sheet
    contact_path = Path(output_dir) / "contact-sheet.jpg"

    try:
        contact_sheet = Path(build_sheet(result.long_video, contact_path))
        critique = review(channel_id, contact_sheet, result.thumbnails, llm)
    except Exception as exc:  # noqa: BLE001 - visual critic is advisory during supervised rollout
        state["visual_critic_error"] = str(exc)
        return ProductionResult(state=state, quality_report=result.quality_report)

    state["contact_sheet"] = contact_sheet
    state["visual_critic_ok"] = critique.ok
    state["visual_issues"] = tuple(
        {"code": issue.code, "message": issue.message} for issue in critique.issues
    )
    state["visual_targeted_changes"] = tuple(critique.targeted_changes)
    state["visual_correction_requested"] = bool(
        not critique.ok and critique.targeted_changes
    )

    if critique.ok or not critique.targeted_changes or visual_corrector is None:
        return ProductionResult(state=state, quality_report=result.quality_report)

    try:
        correction = visual_corrector(state, critique)
    except Exception as exc:  # noqa: BLE001 - advisory correction must not erase validated output
        state["visual_correction_error"] = str(exc)
        return ProductionResult(state=state, quality_report=result.quality_report)

    if not correction:
        return ProductionResult(state=state, quality_report=result.quality_report)

    corrected = dict(state)
    corrected.update(dict(correction))
    corrected["visual_correction_attempts"] = 1
    try:
        for stage_name in ("render", "thumbnails", "qa"):
            update = getattr(stages, stage_name)(corrected)
            if update is not None:
                corrected.update(dict(update))
    except Exception as exc:  # noqa: BLE001 - critic cannot invalidate the previously validated output
        state["visual_correction_attempts"] = 1
        state["visual_correction_error"] = str(exc)
        return ProductionResult(state=state, quality_report=result.quality_report)

    corrected_report = corrected.get("quality_report")
    if not isinstance(corrected_report, QualityReport):
        state["visual_correction_attempts"] = 1
        state["visual_correction_error"] = "correction QA did not return QualityReport"
        return ProductionResult(state=state, quality_report=result.quality_report)
    return ProductionResult(state=corrected, quality_report=corrected_report)


def _blocked(state: ProductionState) -> bool:
    return not bool(state.get("fact_ok", True)) or bool(state.get("layout_issues"))


def _merge_report(
    base: QualityReport,
    *extra_groups: tuple[QualityIssue, ...],
) -> QualityReport:
    issues = list(base.issues)
    for group in extra_groups:
        issues.extend(group)
    frozen = tuple(issues)
    return QualityReport(ok=not any(issue.fatal for issue in frozen), issues=frozen)


def _release(resource) -> None:
    release = getattr(resource, "release", None)
    if callable(release):
        release()


def build_professional_stages(
    *,
    channel_id: str,
    channel_cfg: dict,
    packet: dict,
    title: str,
    output_dir: Path,
    tts,
    editorial_llm=None,
    asset_capturer=None,
    editorial_preparer=None,
    asset_preparer=None,
    short_builder=None,
    caption_aligner=None,
    transcriber=None,
    audio_masterer=None,
    package_builder=None,
    render_runner=None,
    thumbnail_renderer=None,
) -> ProductionStages:
    """Build the real professional pipeline as explicit, testable production stages."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    def editorial(state: ProductionState) -> StageResult:
        from app.editorial.ollama import OllamaJsonClient
        from app.orchestration.editorial import prepare_editorial
        from app.quality.layout import validate_scene_layout_metadata
        from app.shorts.pipeline import build_short_story
        from app.validation.facts import validate_script

        prepare = editorial_preparer or prepare_editorial
        owned_llm = editorial_llm is None
        llm = editorial_llm or OllamaJsonClient()
        try:
            bundle, scene_plan = prepare(packet, channel_id, llm)
            script = bundle.script
            fact_check = validate_script(script, packet)
            layout_issues = validate_scene_layout_metadata(scene_plan, channel_id)

            (output / "script.txt").write_text(script, encoding="utf-8")
            (output / "editorial.json").write_text(
                json.dumps(asdict(bundle), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (output / "scenes.json").write_text(
                json.dumps(asdict(scene_plan), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            result: ProductionState = {
                "editorial_bundle": bundle,
                "scene_plan": scene_plan,
                "script": script,
                "fact_check": fact_check,
                "fact_ok": fact_check.ok,
                "layout_issues": layout_issues,
            }
            if not fact_check.ok or layout_issues:
                return result

            make_short = short_builder or build_short_story
            try:
                short_story = make_short(channel_id, packet, script, llm)
            except Exception as exc:  # noqa: BLE001 - optional Short cannot invalidate long-form
                result["short_error"] = str(exc)
            else:
                result["short_story"] = short_story
                result["short_scene_plan"] = short_story.scene_plan
                result["short_script"] = short_story.script
            return result
        finally:
            if owned_llm:
                unload = getattr(llm, "unload", None)
                if callable(unload):
                    unload()

    def assets(state: ProductionState) -> StageResult:
        if _blocked(state):
            return {}
        from app.assets.service import prepare_assets
        from app.orchestration.editorial import prepare_episode_assets

        prepare_long = asset_preparer or prepare_episode_assets
        long_assets = prepare_long(
            state["scene_plan"],
            packet,
            channel_cfg,
            output,
            asset_capturer,
        )
        result: ProductionState = {"asset_manifest": long_assets}
        short_plan = state.get("short_scene_plan")
        if short_plan is not None:
            try:
                short_assets = prepare_assets(
                    short_plan,
                    packet,
                    channel_cfg,
                    output / "short-assets",
                    asset_capturer,
                )
            except Exception as exc:  # noqa: BLE001 - optional Short cannot invalidate long-form
                result["short_error"] = str(exc)
            else:
                result["short_asset_manifest"] = short_assets
        return result

    def narration(state: ProductionState) -> StageResult:
        if _blocked(state):
            return {}
        try:
            result: ProductionState = {
                "narration": Path(tts.synthesize(state["script"], output / "narration.wav"))
            }
            if state.get("short_script") and state.get("short_asset_manifest") is not None:
                try:
                    result["short_narration"] = Path(
                        tts.synthesize(state["short_script"], output / "short-narration.wav")
                    )
                except Exception as exc:  # noqa: BLE001 - optional Short cannot invalidate long-form
                    result["short_error"] = str(exc)
            return result
        finally:
            _release(tts)

    def captions(state: ProductionState) -> StageResult:
        if _blocked(state) or state.get("narration") is None:
            return {}
        from app.captions.align import FasterWhisperTranscriber, align_narration

        align = caption_aligner or align_narration
        speech_transcriber = transcriber or FasterWhisperTranscriber()
        try:
            result: ProductionState = {
                "captions": align(state["narration"], state["script"], speech_transcriber)
            }
            if state.get("short_narration") is not None:
                try:
                    result["short_captions"] = align(
                        state["short_narration"],
                        state["short_script"],
                        speech_transcriber,
                    )
                except Exception as exc:  # noqa: BLE001 - optional Short cannot invalidate long-form
                    result["short_error"] = str(exc)
            return result
        finally:
            _release(speech_transcriber)

    def audio(state: ProductionState) -> StageResult:
        if _blocked(state) or state.get("narration") is None:
            return {}
        from app.rendering.pipeline import _master_audio

        master = audio_masterer or _master_audio
        result: ProductionState = {
            "audio": Path(master(state["narration"], channel_cfg, output / "master.wav"))
        }
        if state.get("short_narration") is not None and state.get("short_captions") is not None:
            try:
                result["short_audio"] = Path(
                    master(
                        state["short_narration"],
                        channel_cfg,
                        output / "short-master.wav",
                    )
                )
            except Exception as exc:  # noqa: BLE001 - optional Short cannot invalidate long-form
                result["short_error"] = str(exc)
        return result

    def render(state: ProductionState) -> StageResult:
        if _blocked(state) or state.get("audio") is None:
            return {}
        from app.rendering.package import build_render_package
        from app.rendering.pipeline import composition_id
        from app.rendering.runner import RemotionRunner

        package = package_builder or build_render_package
        runner = render_runner or RemotionRunner()
        long_package = package(
            channel_cfg,
            title,
            state["script"],
            state["scene_plan"],
            state["captions"],
            state["asset_manifest"],
            state["audio"],
            output / "render-package-long",
            format="long",
        )
        long_video = runner.render(
            long_package,
            composition_id(channel_id, "long"),
            output / "video.mp4",
        )
        result: ProductionState = {
            "render_package": Path(long_package),
            "long_video": Path(long_video),
        }

        short_ready = all(
            state.get(key) is not None
            for key in (
                "short_scene_plan",
                "short_script",
                "short_asset_manifest",
                "short_captions",
                "short_audio",
            )
        )
        if short_ready:
            try:
                short_package = package(
                    channel_cfg,
                    title,
                    state["short_script"],
                    state["short_scene_plan"],
                    state["short_captions"],
                    state["short_asset_manifest"],
                    state["short_audio"],
                    output / "render-package-short",
                    format="short",
                )
                short_video = runner.render(
                    short_package,
                    composition_id(channel_id, "short"),
                    output / "short.mp4",
                )
            except Exception as exc:  # noqa: BLE001 - optional Short cannot invalidate long-form
                result["short_error"] = str(exc)
            else:
                result["short_render_package"] = Path(short_package)
                result["short_video"] = Path(short_video)
        return result

    def thumbnails(state: ProductionState) -> StageResult:
        if _blocked(state) or state.get("long_video") is None:
            return {"thumbnails": ()}
        from app.visuals.thumbnail_v2 import render_thumbnail_variants

        renderer = thumbnail_renderer or render_thumbnail_variants
        paths = renderer(
            channel_cfg,
            title,
            state["scene_plan"],
            state["asset_manifest"],
            output / "thumbnails",
            count=5,
        )
        return {"thumbnails": tuple(Path(path) for path in paths)}

    def qa(state: ProductionState) -> StageResult:
        from app.quality.validation import validate_longform, validate_short
        from app.rendering.ffmpeg import probe_media

        layout_issues = tuple(state.get("layout_issues", ()))
        fact_check = state.get("fact_check")
        fact_issues: tuple[QualityIssue, ...] = ()
        if fact_check is not None and not fact_check.ok:
            fact_issues = tuple(
                QualityIssue("fact_gate_failed", str(reason), fatal=True)
                for reason in fact_check.reasons
            ) or (QualityIssue("fact_gate_failed", "verified-fact gate did not pass"),)

        if state.get("long_video") is None:
            issues = layout_issues + fact_issues
            if not issues:
                issues = (QualityIssue("missing_video", "professional render did not produce video"),)
            return {"quality_report": QualityReport(ok=False, issues=issues)}

        expected_duration = probe_media(Path(state["audio"])).format_duration
        outputs = SimpleNamespace(
            long_video=state.get("long_video"),
            short_video=state.get("short_video"),
            thumbnails=state.get("thumbnails", ()),
            render_package=state.get("render_package"),
            short_render_package=state.get("short_render_package"),
        )
        long_report = validate_longform(outputs, expected_duration, fact_ok=True)
        report = _merge_report(long_report, layout_issues, fact_issues)

        optional_issues: list[QualityIssue] = []
        short_error = state.get("short_error")
        if short_error:
            optional_issues.append(QualityIssue("short_failed", str(short_error), fatal=False))
        if state.get("short_video") is not None:
            short_report = validate_short(outputs)
            optional_issues.extend(
                QualityIssue(issue.code, issue.message, fatal=False)
                for issue in short_report.issues
            )
        if optional_issues:
            report = _merge_report(report, tuple(optional_issues))
        return {"quality_report": report}

    return ProductionStages(
        editorial=editorial,
        assets=assets,
        narration=narration,
        captions=captions,
        audio=audio,
        render=render,
        thumbnails=thumbnails,
        qa=qa,
    )


def _visual_critic_enabled() -> bool:
    return os.getenv("AUTOTUBE_VISUAL_CRITIC", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def produce_professional_episode(
    *,
    channel_id: str,
    channel_cfg: dict,
    packet: dict,
    title: str,
    output_dir: Path,
    tts,
    visual_llm=None,
    visual_corrector=None,
    contact_sheet_builder=None,
    visual_critic=None,
    **stage_dependencies,
) -> ProductionResult:
    stages = build_professional_stages(
        channel_id=channel_id,
        channel_cfg=channel_cfg,
        packet=packet,
        title=title,
        output_dir=output_dir,
        tts=tts,
        **stage_dependencies,
    )
    result = produce_episode(
        {
            "channel_id": channel_id,
            "channel_cfg": channel_cfg,
            "packet": packet,
            "title": title,
            "output_dir": Path(output_dir),
        },
        stages,
    )
    owned_visual_llm = False
    if visual_llm is None and _visual_critic_enabled():
        from app.editorial.ollama import OllamaJsonClient

        visual_llm = OllamaJsonClient()
        owned_visual_llm = True
    try:
        return apply_visual_review(
            result,
            channel_id=channel_id,
            output_dir=Path(output_dir),
            stages=stages,
            llm=visual_llm,
            contact_sheet_builder=contact_sheet_builder,
            critic=visual_critic,
            visual_corrector=visual_corrector,
        )
    finally:
        if owned_visual_llm:
            unload = getattr(visual_llm, "unload", None)
            if callable(unload):
                unload()
