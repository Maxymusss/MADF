# Clear WebEx cache
Write-Host "`n=========================================="
Write-Host "Clearing WebEx Cache"
Write-Host "==========================================`n"

$wbxCachePath = "C:\Users\szmen\AppData\Local\WebEx\wbxcache"

if (Test-Path $wbxCachePath) {
    # Check size before
    Write-Host "Calculating current cache size..."
    $beforeSize = (Get-ChildItem $wbxCachePath -Recurse -File -ErrorAction SilentlyContinue |
                   Measure-Object -Property Length -Sum).Sum
    $beforeMB = [math]::Round($beforeSize/1MB, 2)
    $beforeGB = [math]::Round($beforeSize/1GB, 2)

    Write-Host "Current WebEx cache: $beforeGB GB ($beforeMB MB)"
    Write-Host ""
    Write-Host "Clearing cache..."

    # Clear the cache
    Remove-Item "$wbxCachePath\*" -Recurse -Force -ErrorAction SilentlyContinue

    Write-Host "[OK] WebEx cache cleared successfully"
    Write-Host ""
    Write-Host "Space recovered: $beforeGB GB"

} else {
    Write-Host "[ERROR] WebEx cache folder not found at: $wbxCachePath"
}

Write-Host ""
Write-Host "=========================================="
Write-Host ""

# Check current drive space
Write-Host "Updated C: Drive Space:"
Get-PSDrive C | Format-Table Name,
    @{Name="Used(GB)";Expression={[math]::Round($_.Used/1GB,2)}},
    @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}},
    @{Name="Total(GB)";Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}}

Write-Host ""
