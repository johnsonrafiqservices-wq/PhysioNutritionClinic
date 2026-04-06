# Stop Django Server Script
# This script stops the running Django development server

$ProjectPath = "c:\excellence_med_care"
$LogFile = "$ProjectPath\server_startup.log"

Write-Host "Stopping Django server..." -ForegroundColor Yellow

# Find and stop Python processes running manage.py
$processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*manage.py*runserver*"
}

if ($processes) {
    $count = $processes.Count
    Write-Host "Found $count Django server process(es). Stopping..." -ForegroundColor Cyan
    
    foreach ($process in $processes) {
        try {
            Stop-Process -Id $process.Id -Force
            Write-Host "  Stopped process ID: $($process.Id)" -ForegroundColor Green
        } catch {
            Write-Host "  Failed to stop process ID: $($process.Id) - $_" -ForegroundColor Red
        }
    }
    
    # Log the stop event
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "=== Server Stopped at $timestamp ==="
    
    Write-Host "`nDjango server stopped successfully!" -ForegroundColor Green
} else {
    Write-Host "No Django server processes found running." -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
