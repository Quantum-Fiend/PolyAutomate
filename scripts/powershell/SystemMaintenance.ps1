# System Maintenance Script for Windows
# Performs system cleanup and updates

Write-Host "🔧 OmniTasker System Maintenance" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Clean temporary files
Write-Host "🧹 Cleaning temporary files..." -ForegroundColor Yellow
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# Clean Windows Update cache
Write-Host "📦 Cleaning Windows Update cache..." -ForegroundColor Yellow
Stop-Service -Name wuauserv -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service -Name wuauserv -ErrorAction SilentlyContinue

# Disk cleanup
Write-Host "💾 Running Disk Cleanup..." -ForegroundColor Yellow
cleanmgr /sagerun:1 | Out-Null

# Disk usage report
Write-Host "💾 Disk Usage Report:" -ForegroundColor Green
Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -gt 0} | Format-Table Name, @{Label="Used(GB)";Expression={[math]::Round($_.Used/1GB,2)}}, @{Label="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}}

Write-Host "✅ System maintenance completed!" -ForegroundColor Green
