# PowerShell script to set up daily documentation refresh task
# Run as Administrator to create scheduled task

param(
    [switch]$Remove,
    [string]$Time = "08:00"
)

$TaskName = "MADF-Daily-Docs-Refresh"
$ScriptPath = "D:\OneDrive\MADF\.claude\scripts\daily-docs-refresh.bat"
$LogPath = "D:\OneDrive\MADF\.claude\logs\daily-refresh.log"

# Create logs directory if it doesn't exist
$LogDir = Split-Path $LogPath -Parent
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force
    Write-Host "Created log directory: $LogDir"
}

if ($Remove) {
    # Remove existing task
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
        Write-Host "✅ Removed scheduled task: $TaskName"
    } catch {
        Write-Host "⚠️  Task '$TaskName' not found or could not be removed"
    }
    exit
}

# Check if script exists
if (!(Test-Path $ScriptPath)) {
    Write-Host "❌ Script not found: $ScriptPath"
    exit 1
}

# Remove existing task if it exists
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

# Create scheduled task
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ScriptPath`" >> `"$LogPath`" 2>&1"
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Daily refresh of MADF documentation cache and CLAUDE.md timestamp"
    Write-Host "✅ Created scheduled task: $TaskName"
    Write-Host "   Runs daily at: $Time"
    Write-Host "   Script: $ScriptPath"
    Write-Host "   Logs: $LogPath"
    Write-Host ""
    Write-Host "To remove this task, run: .\setup-daily-refresh.ps1 -Remove"
    Write-Host "To change time, run: .\setup-daily-refresh.ps1 -Time '14:30'"
} catch {
    Write-Host "❌ Failed to create scheduled task: $($_.Exception.Message)"
    Write-Host "   Make sure you're running as Administrator"
    exit 1
}