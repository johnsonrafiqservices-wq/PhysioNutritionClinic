@echo off
REM Django Server Startup Batch Script
REM This runs the PowerShell script to start the Django server

cd /d c:\excellence_med_care
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "c:\excellence_med_care\start_server.ps1"
