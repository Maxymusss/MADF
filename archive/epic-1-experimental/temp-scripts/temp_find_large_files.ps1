# Find large files on C: drive
$files = Get-ChildItem -Path "C:\" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 100MB } |
    Sort-Object Length -Descending |
    Select-Object -First 50

Write-Host "`nTop 50 files over 100MB on C: drive:"
Write-Host "=" * 80

foreach ($f in $files) {
    $sizeGB = [math]::Round($f.Length/1GB, 2)
    Write-Host "$sizeGB GB - $($f.FullName)"
}

Write-Host "`n`nDrive space summary:"
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -eq "C" -or $_.Name -eq "D" } |
    Select-Object Name,
        @{Name="Used(GB)";Expression={[math]::Round($_.Used/1GB,2)}},
        @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}},
        @{Name="Total(GB)";Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}}
