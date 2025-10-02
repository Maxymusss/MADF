# Verify Docker migration completion
Write-Host "`nDocker Migration Verification Report"
Write-Host "=" * 80

$oldPath = 'C:\Users\szmen\AppData\Local\Docker'
$newPath = 'D:\Docker'

if (Test-Path $oldPath) {
    $oldSize = (Get-ChildItem $oldPath -Recurse -File -ErrorAction SilentlyContinue |
                Measure-Object -Property Length -Sum).Sum
    $oldSizeGB = [math]::Round($oldSize/1GB, 2)
    Write-Host "`nOld location (C:\Users\szmen\AppData\Local\Docker): $oldSizeGB GB"
} else {
    Write-Host "`nOld location (C:): NOT FOUND (fully migrated)"
}

if (Test-Path $newPath) {
    $newSize = (Get-ChildItem $newPath -Recurse -File -ErrorAction SilentlyContinue |
                Measure-Object -Property Length -Sum).Sum
    $newSizeGB = [math]::Round($newSize/1GB, 2)
    Write-Host "New location (D:\Docker): $newSizeGB GB"
} else {
    Write-Host "New location (D:): NOT FOUND"
}

Write-Host "`n" + ("=" * 80)
Write-Host "`nCurrent C: and D: drive space:"
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -eq "C" -or $_.Name -eq "D" } |
    Select-Object Name,
        @{Name="Used(GB)";Expression={[math]::Round($_.Used/1GB,2)}},
        @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}},
        @{Name="Total(GB)";Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}}
