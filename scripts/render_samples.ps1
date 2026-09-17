$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$fixtures = @(
    "tests/fixtures/media/kernelrush_story.json",
    "tests/fixtures/media/lobbysignal_story.json"
)

foreach ($fixture in $fixtures) {
    Write-Host "Rendering synthetic sample: $fixture"
    python scripts/render_sample_story.py $fixture --output output/samples
}

Write-Host "Sample renders complete. Review output/samples/kernelrush and output/samples/lobbysignal before approving the professional renderer."
