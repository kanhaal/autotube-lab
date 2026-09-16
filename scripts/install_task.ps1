param([string]$ProjectPath = (Resolve-Path ".").Path)
$exe = Join-Path $ProjectPath ".venv\Scripts\autotube.exe"
$action = New-ScheduledTaskAction -Execute $exe -Argument "run-daily --render" -WorkingDirectory $ProjectPath
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00PM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "AutoTubeLab-Daily" -Action $action -Trigger $trigger -Settings $settings -Description "Generate KernelRush and LobbySignal daily episodes" -Force
