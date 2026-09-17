$ErrorActionPreference = "Stop"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3.11+ is required" }
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[youtube,media,voice]"
& .\.venv\Scripts\python.exe -m playwright install chromium
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Host "FFmpeg not found. Install with: winget install Gyan.FFmpeg"
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  Write-Host "Node.js 22 LTS is required for the professional Remotion renderer. Install with: winget install OpenJS.NodeJS.LTS"
} else {
  Push-Location video
  npm install
  Pop-Location
}
& .\.venv\Scripts\autotube.exe init
Write-Host "Install Ollama from https://ollama.com and run: ollama pull qwen3.5:9b"
Write-Host "Fallback for lower VRAM pressure: set AUTOTUBE_LLM_MODEL=qwen3:8b after pulling that model."
Write-Host "Production narration uses local Chatterbox with Kokoro fallback; run 'autotube health' to verify imports."
Write-Host "Professional video rendering uses the Remotion project in video/."
