# Django Server Startup Script
# This script starts the Django development server in the background

$ProjectPath = "c:\excellence_med_care"
$LogFile = "$ProjectPath\server_startup.log"
$Port = 8000

# Change to project directory
Set-Location $ProjectPath

# Log startup
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $LogFile -Value "`n=== Server Starting at $timestamp ==="

# Check if virtual environment exists and activate it
$VenvPath = "$ProjectPath\venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    Add-Content -Path $LogFile -Value "Activating virtual environment"
    & $VenvPath
} else {
    Add-Content -Path $LogFile -Value "No virtual environment found, using system Python"
}

# Start Django development server
Write-Host "Starting Django server on port $Port..." -ForegroundColor Cyan
Add-Content -Path $LogFile -Value "Starting Django server on port $Port"

try {
    # Start the server and redirect output to log file
    Start-Process -FilePath "python" `
                  -ArgumentList "manage.py", "runserver", "0.0.0.0:$Port" `
                  -WorkingDirectory $ProjectPath `
                  -WindowStyle Hidden `
                  -RedirectStandardOutput "$ProjectPath\server_output.log" `
                  -RedirectStandardError "$ProjectPath\server_error.log"
    
    Add-Content -Path $LogFile -Value "Server started successfully"
    Write-Host "Server started successfully!" -ForegroundColor Green
    Write-Host "Access at: http://192.168.1.122:$Port" -ForegroundColor Yellow
    Write-Host "Logs: $ProjectPath\server_output.log" -ForegroundColor Gray
} catch {
    Add-Content -Path $LogFile -Value "Error starting server: $_"
    Write-Host "Error starting server: $_" -ForegroundColor Red
}
