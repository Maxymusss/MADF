# Quick Wins - Space Recovery Script
Write-Host "`n=========================================="
Write-Host "PHASE 4: QUICK WINS CLEANUP"
Write-Host "==========================================`n"

# Check hibernation file
Write-Host "1. CHECKING HIBERNATION STATUS:"
Write-Host "-" * 40
if (Test-Path 'C:\hiberfil.sys') {
    $hibFile = Get-Item 'C:\hiberfil.sys' -Force
    $hibSizeGB = [math]::Round($hibFile.Length/1GB, 2)
    Write-Host "[FOUND] Hibernation file: $hibSizeGB GB"
    Write-Host "[ACTION] Will disable hibernation to recover space"
} else {
    Write-Host "[OK] Hibernation already disabled - no file found"
}

# Current space
Write-Host "`n2. CURRENT DRIVE SPACE:"
Write-Host "-" * 40
$beforeFree = (Get-PSDrive C).Free
$beforeFreeGB = [math]::Round($beforeFree/1GB, 2)
Write-Host "C: Drive Free Space: $beforeFreeGB GB"

Write-Host "`n=========================================="
Write-Host "Ready to execute cleanup actions."
Write-Host "This will be done in phases to track progress."
Write-Host "=========================================="
