# Analyze Bloomberg cache
Write-Host "`n=========================================="
Write-Host "BLOOMBERG CACHE ANALYSIS (1.47 GB)"
Write-Host "==========================================`n"

$bloombergPath = "C:\Users\szmen\AppData\Local\Bloomberg"

if (Test-Path $bloombergPath) {
    Write-Host "BLOOMBERG FOLDER BREAKDOWN:"
    Write-Host "-" * 80

    # Overall size
    $totalSize = (Get-ChildItem $bloombergPath -Recurse -File -ErrorAction SilentlyContinue |
                  Measure-Object -Property Length -Sum).Sum
    $totalGB = [math]::Round($totalSize/1GB, 2)
    Write-Host "Total: $totalGB GB"
    Write-Host ""

    # Subfolder breakdown
    $folders = Get-ChildItem $bloombergPath -Directory -ErrorAction SilentlyContinue

    $results = @()
    foreach ($folder in $folders) {
        $size = (Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum

        if ($size -gt 10MB) {
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

    # Check for cache/temp directories
    Write-Host "`nCACHE/TEMP DIRECTORIES:"
    Write-Host "-" * 80

    $cacheFolders = Get-ChildItem $bloombergPath -Recurse -Directory -ErrorAction SilentlyContinue |
                    Where-Object {$_.Name -like "*cache*" -or $_.Name -like "*Cache*" -or $_.Name -like "*temp*" -or $_.Name -like "*Temp*" -or $_.Name -like "*log*"}

    if ($cacheFolders) {
        foreach ($cache in $cacheFolders) {
            $cacheSize = (Get-ChildItem $cache.FullName -Recurse -File -ErrorAction SilentlyContinue |
                          Measure-Object -Property Length -Sum).Sum
            if ($cacheSize -gt 1MB) {
                $cacheSizeMB = [math]::Round($cacheSize/1MB, 2)
                Write-Host "$cacheSizeMB MB - $($cache.Name) [$($cache.Parent.Name)]"
            }
        }
    } else {
        Write-Host "No obvious cache directories found"
    }

} else {
    Write-Host "[ERROR] Bloomberg folder not found"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "ABOUT BLOOMBERG TERMINAL"
Write-Host "=========================================="
Write-Host ""
Write-Host "Bloomberg Terminal is a professional financial data platform."
Write-Host "Subscription-based service for market data, news, analytics."
Write-Host ""
Write-Host "CLEANUP OPTIONS:"
Write-Host "1. Check if actively subscribed and using"
Write-Host "2. Check last modified dates above"
Write-Host "3. If subscription ended, uninstall via Settings > Apps"
Write-Host "4. If actively used, contact Bloomberg support before clearing cache"
Write-Host "5. Bloomberg may have built-in cache management tools"
Write-Host ""
Write-Host "WARNING: Do NOT manually delete Bloomberg data without guidance"
Write-Host "         May require re-download of market data (time-consuming)"
Write-Host ""
Write-Host "=========================================="
Write-Host ""
