# Final verification of space recovery
Write-Host "`n=========================================="
Write-Host "Phase 2 Cleanup - Final Verification"
Write-Host "==========================================`n"

# Check drive space
Write-Host "Current Drive Space:"
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -eq "C" -or $_.Name -eq "D" } |
    Format-Table Name,
        @{Name="Used(GB)";Expression={[math]::Round($_.Used/1GB,2)}; Align="Right"},
        @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}; Align="Right"},
        @{Name="Total(GB)";Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}; Align="Right"}

# Verify removed directories
Write-Host "`nVerifying Cleanup Results:"
Write-Host "-" * 40

$checks = @(
    @{Path="C:\Users\szmen\AppData\Local\Temp"; Name="Temp folder"},
    @{Path="C:\Users\szmen\.cache\puppeteer"; Name="Puppeteer cache"},
    @{Path="C:\Users\szmen\AppData\Local\ms-playwright"; Name="Playwright browsers"}
)

foreach ($check in $checks) {
    if (Test-Path $check.Path) {
        $size = (Get-ChildItem $check.Path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        Write-Host "[INFO] $($check.Name): $sizeGB GB remaining"
    } else {
        Write-Host "[OK] $($check.Name): Fully removed"
    }
}

Write-Host "`n=========================================="
Write-Host "Cleanup Complete"
Write-Host "==========================================`n"
