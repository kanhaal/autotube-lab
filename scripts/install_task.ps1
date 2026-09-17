param([string]$ProjectPath = (Resolve-Path ".").Path)
$exe = Join-Path $ProjectPath ".venv\Scripts\autotube.exe"
if (-not (Test-Path $exe)) {
    throw "AutoTube executable not found at $exe. Run scripts/setup_windows.ps1 first."
}
$action = New-ScheduledTaskAction -Execute $exe -Argument "run-daily --render --renderer professional" -WorkingDirectory $ProjectPath
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00PM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "AutoTubeLab-Daily" -Action $action -Trigger $trigger -Settings $settings -Description "Generate supervised professional KernelRush and LobbySignal renders" -Force
