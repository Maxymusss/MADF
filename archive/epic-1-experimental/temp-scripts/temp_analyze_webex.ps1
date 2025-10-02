# Analyze WebEx cache
Write-Host "`n=========================================="
Write-Host "WEBEX CACHE ANALYSIS (1.28 GB)"
Write-Host "==========================================`n"

$webexPath = "C:\Users\szmen\AppData\Local\WebEx"

if (Test-Path $webexPath) {
    Write-Host "WEBEX FOLDER BREAKDOWN:"
    Write-Host "-" * 80

    # Overall size
    $totalSize = (Get-ChildItem $webexPath -Recurse -File -ErrorAction SilentlyContinue |
                  Measure-Object -Property Length -Sum).Sum
    $totalGB = [math]::Round($totalSize/1GB, 2)
    Write-Host "Total: $totalGB GB"
    Write-Host ""

    # Subfolder breakdown
    $folders = Get-ChildItem $webexPath -Directory -ErrorAction SilentlyContinue

    $results = @()
    foreach ($folder in $folders) {
        $size = (Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum

        if ($size -gt 5MB) {
            $results += [PSCustomObject]@{
                Folder = $folder.Name
                SizeGB = [math]::Round($size/1GB, 2)
                SizeMB = [math]::Round($size/1MB, 2)
                Path = $folder.FullName
                LastModified = $folder.LastWriteTime
            }
        }
    }

    $results | Sort-Object SizeGB -Descending | Format-Table Folder, SizeGB, SizeMB, LastModified -AutoSize

    # Check for recordings/cache
    Write-Host "`nLARGE FILES (RECORDINGS/CACHE):"
    Write-Host "-" * 80

    $largeFiles = Get-ChildItem $webexPath -Recurse -File -ErrorAction SilentlyContinue |
                  Where-Object {$_.Length -gt 10MB} |
                  Sort-Object Length -Descending |
                  Select-Object -First 10

    if ($largeFiles) {
        foreach ($file in $largeFiles) {
            $sizeMB = [math]::Round($file.Length/1MB, 2)
            Write-Host "$sizeMB MB - $($file.Name) [$($file.Extension)]"
        }
    } else {
        Write-Host "No large individual files found"
    }

    # Check for temp/cache directories
    Write-Host "`nCACHE/TEMP DIRECTORIES:"
    Write-Host "-" * 80

    $cacheFolders = Get-ChildItem $webexPath -Recurse -Directory -ErrorAction SilentlyContinue |
                    Where-Object {$_.Name -like "*cache*" -or $_.Name -like "*temp*" -or $_.Name -like "*log*" -or $_.Name -like "*recording*"}

    if ($cacheFolders) {
        foreach ($cache in $cacheFolders) {
            $cacheSize = (Get-ChildItem $cache.FullName -Recurse -File -ErrorAction SilentlyContinue |
                          Measure-Object -Property Length -Sum).Sum
            if ($cacheSize -gt 1MB) {
                $cacheSizeMB = [math]::Round($cacheSize/1MB, 2)
                Write-Host "$cacheSizeMB MB - $($cache.Name)"
            }
        }
    } else {
        Write-Host "No obvious cache directories found"
    }

} else {
    Write-Host "[ERROR] WebEx folder not found"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "CLEANUP OPTIONS FOR WEBEX"
Write-Host "=========================================="
Write-Host ""
Write-Host "SAFE TO CLEAR:"
Write-Host "1. Old meeting recordings (if backed up elsewhere)"
Write-Host "2. Cache files"
Write-Host "3. Log files"
Write-Host ""
Write-Host "HOW TO CLEAR:"
Write-Host "1. Open WebEx app settings"
Write-Host "2. Look for 'Clear cache' or 'Storage' option"
Write-Host "3. Or manually delete temp/cache folders identified above"
Write-Host "4. Keep recordings you need, delete old ones"
Write-Host ""
Write-Host "RECOVERY POTENTIAL: 0.5-1 GB (depending on recordings)"
Write-Host ""
Write-Host "=========================================="
Write-Host ""
