$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Project virtualenv Python not found at $python. Run scripts/setup_windows.ps1 first."
}

$fixtures = @(
    "tests/fixtures/media/kernelrush_story.json",
    "tests/fixtures/media/lobbysignal_story.json"
)

foreach ($fixture in $fixtures) {
    Write-Host "Rendering synthetic sample: $fixture"
    & $python scripts/render_sample_story.py $fixture --output output/samples
}

Write-Host "Sample renders complete. Review output/samples/kernelrush and output/samples/lobbysignal before approving the professional renderer."
