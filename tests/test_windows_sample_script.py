from pathlib import Path


def test_render_samples_stops_when_python_renderer_fails():
    script = Path("scripts/render_samples.ps1").read_text(encoding="utf-8")

    assert "if ($LASTEXITCODE -ne 0)" in script
    assert "Sample render failed" in script
