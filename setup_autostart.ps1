# Setup Script to Register Django Server as Startup Task
# Run this script as Administrator

$TaskName = "ExcellenceMedCare_Django_Server"
$ScriptPath = "c:\excellence_med_care\start_server.bat"
$Description = "Automatically starts Excellence Med Care Django server on system boot"

Write-Host "Setting up auto-start for Django server..." -ForegroundColor Green

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit
}

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create the scheduled task action
$Action = New-ScheduledTaskAction -Execute $ScriptPath

# Create the trigger (at startup)
$Trigger = New-ScheduledTaskTrigger -AtStartup

# Set task to run with highest privileges
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Configure settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# Register the scheduled task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Principal $Principal `
        -Settings $Settings `
        -Description $Description `
        -Force | Out-Null
    
    Write-Host "`nTask registered successfully!" -ForegroundColor Green
    Write-Host "Task Name: $TaskName" -ForegroundColor Cyan
    Write-Host "The Django server will start automatically on next boot." -ForegroundColor Yellow
    Write-Host "`nTo manually start the server now, run: .\start_server.bat" -ForegroundColor Gray
    Write-Host "To view task: Open Task Scheduler and look for '$TaskName'" -ForegroundColor Gray
    Write-Host "To disable: Run 'Disable-ScheduledTask -TaskName `"$TaskName`"'" -ForegroundColor Gray
    Write-Host "To remove: Run 'Unregister-ScheduledTask -TaskName `"$TaskName`" -Confirm:`$false'" -ForegroundColor Gray
} catch {
    Write-Host "Error registering task: $_" -ForegroundColor Red
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
