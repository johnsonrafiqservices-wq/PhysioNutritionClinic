# Script to download all CDN assets locally
# Run this from c:\excellence_med_care

Write-Host "Creating directory structure..." -ForegroundColor Green

# Create directories
New-Item -ItemType Directory -Force -Path "static\vendor\bootstrap\css" | Out-Null
New-Item -ItemType Directory -Force -Path "static\vendor\bootstrap\js" | Out-Null
New-Item -ItemType Directory -Force -Path "static\vendor\bootstrap-icons\fonts" | Out-Null
New-Item -ItemType Directory -Force -Path "static\vendor\select2\css" | Out-Null
New-Item -ItemType Directory -Force -Path "static\vendor\select2\js" | Out-Null
New-Item -ItemType Directory -Force -Path "static\vendor\fontawesome\css" | Out-Null
New-Item -ItemType Directory -Force -Path "static\vendor\fontawesome\webfonts" | Out-Null

Write-Host "Downloading Bootstrap CSS..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" `
    -OutFile "static\vendor\bootstrap\css\bootstrap.min.css"

Write-Host "Downloading Bootstrap JS..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" `
    -OutFile "static\vendor\bootstrap\js\bootstrap.bundle.min.js"

Write-Host "Downloading Bootstrap Icons CSS..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" `
    -OutFile "static\vendor\bootstrap-icons\bootstrap-icons.css"

Write-Host "Downloading Bootstrap Icons fonts..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff2" `
    -OutFile "static\vendor\bootstrap-icons\fonts\bootstrap-icons.woff2"
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff" `
    -OutFile "static\vendor\bootstrap-icons\fonts\bootstrap-icons.woff"

Write-Host "Downloading Select2 CSS..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" `
    -OutFile "static\vendor\select2\css\select2.min.css"

Write-Host "Downloading Select2 JS..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js" `
    -OutFile "static\vendor\select2\js\select2.min.js"

Write-Host "Downloading Select2 Bootstrap 5 theme..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/select2-bootstrap-5-theme.min.css" `
    -OutFile "static\vendor\select2\css\select2-bootstrap-5-theme.min.css"

Write-Host "Downloading Font Awesome CSS..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" `
    -OutFile "static\vendor\fontawesome\css\all.min.css"

Write-Host "Downloading Font Awesome webfonts..." -ForegroundColor Cyan
$webfonts = @(
    "fa-brands-400.woff2",
    "fa-brands-400.ttf",
    "fa-regular-400.woff2",
    "fa-regular-400.ttf",
    "fa-solid-900.woff2",
    "fa-solid-900.ttf",
    "fa-v4compatibility.woff2",
    "fa-v4compatibility.ttf"
)

foreach ($font in $webfonts) {
    Write-Host "  - $font" -ForegroundColor Gray
    Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/$font" `
        -OutFile "static\vendor\fontawesome\webfonts\$font"
}

Write-Host "`nAll files downloaded successfully!" -ForegroundColor Green
Write-Host "Files are in: static\vendor\" -ForegroundColor Yellow
Write-Host "`nYour Django templates are already configured to use these local files." -ForegroundColor Green
