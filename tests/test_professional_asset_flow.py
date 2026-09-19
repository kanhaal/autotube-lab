import json
from datetime import datetime, timezone
from pathlib import Path

from app.assets.manifest import sha256_file
from app.assets.models import AssetRecord
from app.domain.models import StoryCandidate
from app.orchestration.daily import run_channel
from app.storage.sqlite import Repository


class FakeLLM:
    def __init__(self):
        self.replies = iter([
            {
                "strongest_signal": "Alpha launched a local developer tool.",
                "what_changed": "The tool is available.",
                "why_now": "It launched this week.",
                "context": ["Alpha builds developer software."],
                "evidence_order": ["Primary", "Secondary"],
                "tension": "Whether local execution changes deployment choices.",
                "implication": "Developers have another deployment option.",
                "uncertainty": "Adoption is not known yet.",
                "takeaway": "Watch actual usage.",
            },
            {
                "hooks": [
                    {"text": "Alpha just changed where this tool can run.", "specificity": 9, "curiosity": 8, "clarity": 9, "brevity": 8, "fact_supported": True},
                    {"text": "This launch changes a deployment choice.", "specificity": 8, "curiosity": 7, "clarity": 9, "brevity": 8, "fact_supported": True},
                    {"text": "Alpha will dominate everything.", "specificity": 8, "curiosity": 9, "clarity": 8, "brevity": 8, "fact_supported": False},
                ]
            },
            {
                "script": "Alpha released a local developer tool this week. The release gives developers another deployment option. Why it matters: local execution changes where teams can run the tool and what they may choose to test next. Adoption is not known yet."
            },
            {"needs_rewrite": False, "issues": [], "strengths": ["clear and sourced"]},
            {
                "channel_id": "kernelrush",
                "format": "longform",
                "scenes": [
                    {
                        "id": "s1",
                        "narration": "Alpha released a local developer tool this week.",
                        "purpose": "show the primary source",
                        "scene_type": "source_browser",
                        "headline": "ALPHA GOES LOCAL",
                        "subheadline": "",
                        "source_ids": ["source_1"],
                        "asset_ids": [],
                        "motion": "slow_zoom",
                        "emphasis": ["local"],
                        "transition": "cut",
                        "fallback_scene_type": "fallback_editorial",
                        "data": {},
                    }
                ],
            },
        ])

    def generate_json(self, *args, **kwargs):
        return next(self.replies)


class FakeCapturer:
    def capture(self, request, out_dir: Path):
        target = Path(out_dir) / f"{request.id}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"verified-source-png")
        return AssetRecord(
            id=request.id,
            kind=request.kind,
            local_path=str(target),
            source_url=request.source_url,
            source_name=request.source_name,
            usage=request.purpose,
            license_note="source-page screenshot",
            sha256=sha256_file(target),
            captured_at=datetime.now(timezone.utc),
        )


def test_dry_run_emits_asset_manifest_and_local_verified_png(monkeypatch, tmp_path: Path):
    now = datetime.now(timezone.utc)
    candidate = StoryCandidate(
        "alpha",
        "ai_software",
        "Alpha launch",
        "https://primary.example/alpha",
        "Primary",
        "rss",
        now,
        now,
        ("Alpha",),
        "Alpha released a local developer tool.",
        {},
        0.9,
        "official source",
    )
    research = {
        "topic": "Alpha launch",
        "candidate": {"title": "Alpha launch", "summary": candidate.summary},
        "sources": [
            {"source_name": "Primary", "url": "https://primary.example/alpha", "text": "Alpha released a local developer tool this week."},
            {"source_name": "Secondary", "url": "https://secondary.example/alpha", "text": "The release gives developers another deployment option through local execution."},
        ],
    }

    monkeypatch.setattr("app.orchestration.daily.collect_for_niche", lambda niche: [candidate])
    monkeypatch.setattr("app.orchestration.daily.research_candidate", lambda item: research)

    repo = Repository(tmp_path / "state.db")
    repo.init()
    result = run_channel(
        "kernelrush",
        repo,
        day_index=0,
        output_dir=tmp_path / "output",
        dry_run=True,
        editorial_llm=FakeLLM(),
        asset_capturer=FakeCapturer(),
    )

    latest = json.loads(
        (tmp_path / "output" / "kernelrush" / "latest.json").read_text(encoding="utf-8")
    )
    episode_dir = Path(latest["path"])
    assert episode_dir.parts[-3:-1] == ("kernelrush", "runs")
    assert result["status"] == "generated"
    assert result["asset_manifest"] == str(episode_dir / "asset-manifest.json")
    assert (episode_dir / "asset-manifest.json").exists()
    assert (episode_dir / "assets" / "source-1.png").read_bytes() == b"verified-source-png"
