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
    if ($LASTEXITCODE -ne 0) {
        throw "Sample render failed for $fixture with exit code $LASTEXITCODE."
    }
}

Write-Host "Sample renders complete. V4 keeps every render under output/samples/<channel>/runs/<run-id>."
Write-Host "Use output/samples/kernelrush/latest.json and output/samples/lobbysignal/latest.json to find the newest runs."
Write-Host "Do not delete older runs unless you intentionally want to remove render history."
