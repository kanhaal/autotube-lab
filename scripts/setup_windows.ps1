$ErrorActionPreference = "Stop"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3.11+ is required" }
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[youtube]"
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Host "FFmpeg not found. Install with: winget install Gyan.FFmpeg"
}
& .\.venv\Scripts\autotube.exe init
Write-Host "Install Ollama from https://ollama.com and run: ollama pull qwen3.5:9b"
Write-Host "Fallback for lower VRAM pressure: set AUTOTUBE_LLM_MODEL=qwen3:8b after pulling that model."
