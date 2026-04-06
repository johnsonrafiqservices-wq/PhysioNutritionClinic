# Check Django Server Status
# This script checks if the Django server is running and displays status

$Port = 8000

Write-Host "`n=== Django Server Status Check ===" -ForegroundColor Cyan

# Check for running Python processes with manage.py
$processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*manage.py*runserver*"
}

if ($processes) {
    Write-Host "`n✓ Server is RUNNING" -ForegroundColor Green
    Write-Host "`nProcess Details:" -ForegroundColor Yellow
    foreach ($process in $processes) {
        Write-Host "  Process ID: $($process.Id)" -ForegroundColor Cyan
        Write-Host "  Memory: $([math]::Round($process.WorkingSet64 / 1MB, 2)) MB" -ForegroundColor Gray
        Write-Host "  Start Time: $($process.StartTime)" -ForegroundColor Gray
    }
    
    # Try to check if port is listening
    $portCheck = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($portCheck) {
        Write-Host "`n✓ Port $Port is listening" -ForegroundColor Green
        Write-Host "  Access: http://localhost:$Port" -ForegroundColor Yellow
    } else {
        Write-Host "`n⚠ Port $Port is not listening" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n✗ Server is NOT running" -ForegroundColor Red
    Write-Host "To start the server, run: .\start_server.bat" -ForegroundColor Yellow
}

# Check scheduled task status
$taskName = "ExcellenceMedCare_Django_Server"
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($task) {
    Write-Host "`nScheduled Task Status:" -ForegroundColor Cyan
    Write-Host "  Name: $taskName" -ForegroundColor Gray
    Write-Host "  State: $($task.State)" -ForegroundColor $(if ($task.State -eq "Ready") { "Green" } else { "Yellow" })
    
    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
    if ($taskInfo) {
        Write-Host "  Last Run: $($taskInfo.LastRunTime)" -ForegroundColor Gray
        Write-Host "  Last Result: $($taskInfo.LastTaskResult)" -ForegroundColor Gray
        Write-Host "  Next Run: $($taskInfo.NextRunTime)" -ForegroundColor Gray
    }
} else {
    Write-Host "`n⚠ Auto-start task not configured" -ForegroundColor Yellow
    Write-Host "To setup auto-start, run as Admin: .\setup_autostart.ps1" -ForegroundColor Gray
}

# Check log files
Write-Host "`nLog Files:" -ForegroundColor Cyan
$logFiles = @("server_startup.log", "server_output.log", "server_error.log")
foreach ($logFile in $logFiles) {
    $path = "c:\excellence_med_care\$logFile"
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        $sizeKB = [math]::Round($size / 1KB, 2)
        Write-Host "  $logFile - ${sizeKB} KB" -ForegroundColor Gray
    } else {
        Write-Host "  $logFile - Not found" -ForegroundColor DarkGray
    }
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
