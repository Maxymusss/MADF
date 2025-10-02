# Analyze OpenFin cache
Write-Host "`n=========================================="
Write-Host "OPENFIN CACHE ANALYSIS (1.67 GB)"
Write-Host "==========================================`n"

$openfinPath = "C:\Users\szmen\AppData\Local\OpenFin"

if (Test-Path $openfinPath) {
    Write-Host "OPENFIN FOLDER BREAKDOWN:"
    Write-Host "-" * 80

    # Overall size
    $totalSize = (Get-ChildItem $openfinPath -Recurse -File -ErrorAction SilentlyContinue |
                  Measure-Object -Property Length -Sum).Sum
    $totalGB = [math]::Round($totalSize/1GB, 2)
    Write-Host "Total: $totalGB GB"
    Write-Host ""

    # Subfolder breakdown
    $folders = Get-ChildItem $openfinPath -Directory -ErrorAction SilentlyContinue

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
            }
        }
    }

    $results | Sort-Object SizeGB -Descending | Format-Table Folder, SizeGB, SizeMB -AutoSize

    # Check for cache directories
    Write-Host "`nCACHE DIRECTORIES:"
    Write-Host "-" * 80

    $cacheFolders = Get-ChildItem $openfinPath -Recurse -Directory -ErrorAction SilentlyContinue |
                    Where-Object {$_.Name -like "*cache*" -or $_.Name -like "*Cache*" -or $_.Name -like "*temp*"}

    if ($cacheFolders) {
        foreach ($cache in $cacheFolders) {
            $cacheSize = (Get-ChildItem $cache.FullName -Recurse -File -ErrorAction SilentlyContinue |
                          Measure-Object -Property Length -Sum).Sum
            if ($cacheSize -gt 1MB) {
                $cacheSizeMB = [math]::Round($cacheSize/1MB, 2)
                Write-Host "$cacheSizeMB MB - $($cache.FullName)"
            }
        }
    } else {
        Write-Host "No obvious cache directories found"
    }

} else {
    Write-Host "[ERROR] OpenFin folder not found"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "ABOUT OPENFIN"
Write-Host "=========================================="
Write-Host ""
Write-Host "OpenFin is a desktop application framework for financial services."
Write-Host "Used by trading platforms, Bloomberg Terminal integrations, etc."
Write-Host ""
Write-Host "CLEANUP OPTIONS:"
Write-Host "1. Check if actively used (for trading/finance apps)"
Write-Host "2. If unused, uninstall via Settings > Apps"
Write-Host "3. If actively used, cache may be needed"
Write-Host "4. Contact IT/app vendor before clearing cache"
Write-Host ""
Write-Host "RECOMMENDATION: If not actively trading, consider uninstalling"
Write-Host ""
Write-Host "=========================================="
Write-Host ""
