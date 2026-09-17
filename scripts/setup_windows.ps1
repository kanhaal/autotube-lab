$ErrorActionPreference = "Stop"

function Require-Command([string]$Name, [string]$InstallHint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is required. $InstallHint"
    }
    Write-Host "Found $Name"
}

Require-Command "python" "Install Python 3.11 or newer."
Require-Command "ffmpeg" "Install with: winget install Gyan.FFmpeg"
Require-Command "ffprobe" "FFprobe is included with FFmpeg; ensure the FFmpeg bin directory is on PATH."
Require-Command "ollama" "Install Ollama from https://ollama.com."
Require-Command "node" "Install Node.js 22 LTS with: winget install OpenJS.NodeJS.LTS"
Require-Command "npm" "npm is installed with Node.js."

python -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ is required'"
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[youtube,media,voice]"
& .\.venv\Scripts\python.exe -m playwright install chromium

Push-Location video
try {
    npm ci
} finally {
    Pop-Location
}

& .\.venv\Scripts\autotube.exe init

Write-Host "Setup complete. Large local model weights are not downloaded automatically."
Write-Host "Install the configured local LLM manually with: ollama pull qwen3.5:9b"
Write-Host "Then run: .\.venv\Scripts\autotube.exe media-smoke"
Write-Host "For the sequential model-load + tiny-render check, run: .\.venv\Scripts\autotube.exe media-smoke --deep"
Write-Host "Keep the scheduler on run-daily --render --renderer professional until supervised KernelRush + LobbySignal review is complete."
