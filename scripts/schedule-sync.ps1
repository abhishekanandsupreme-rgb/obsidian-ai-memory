# schedule-sync.ps1
# Creates a Windows Scheduled Task to run the Obsidian Agent Memory sync every 15 minutes.
# The task runs whether the user is logged in or not, with the highest run level.

param(
    [string]$BatchPath = "C:\Users\asus\Documents\Obsidian Vault\scripts\sync-all-agents.bat",
    [string]$TaskName = "Obsidian Agent Memory Sync",
    [int]$IntervalMinutes = 15
)

$ErrorActionPreference = "Stop"

# Validate batch file exists
if (-not (Test-Path -Path $BatchPath -PathType Leaf)) {
    Write-Error "Batch file not found: $BatchPath"
    exit 1
}

# Remove existing task if present (idempotent)
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[INFO] Removing existing task: $TaskName"
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Define the action
$action = New-ScheduledTaskAction -Execute $BatchPath

# Define the trigger: every 15 minutes, indefinitely
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)

# Define settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0)

# Define principal: use S4U logon type so it works without storing a password.
# S4U runs in the user's context without requiring interactive logon.
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Highest

# Register the task
Write-Host "[INFO] Creating scheduled task: $TaskName"
Write-Host "[INFO]   Script:  $BatchPath"
Write-Host "[INFO]   Interval: every $IntervalMinutes minutes"
Write-Host "[INFO]   Logon:    whether user is logged in or not (SYSTEM)"
Write-Host "[INFO]   RunLevel: Highest"

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Syncs Obsidian AI Memory vault with recent agent activity every $IntervalMinutes minutes." | Out-Null

# Verify registration
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
$state = $task.State

Write-Host "[OK] Scheduled task created successfully."
Write-Host "[INFO]   Name:      $TaskName"
Write-Host "[INFO]   State:     $state"
Write-Host "[INFO]   Next run:  $(($task.Triggers | Select-Object -First 1).StartBoundary)"

# Show task info
$task | Format-List TaskName, State, @{Name='NextRun';Expression={($_.Triggers | Select-Object -First 1).StartBoundary}}

exit 0
