# Analyze Google cache folder
Write-Host "`n=========================================="
Write-Host "GOOGLE CACHE ANALYSIS (3.29 GB)"
Write-Host "==========================================`n"

$googlePath = "C:\Users\szmen\AppData\Local\Google"

if (Test-Path $googlePath) {
    Write-Host "GOOGLE FOLDER BREAKDOWN:"
    Write-Host "-" * 80

    $folders = Get-ChildItem $googlePath -Directory -ErrorAction SilentlyContinue

    $results = @()
    foreach ($folder in $folders) {
        $size = (Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum

        if ($size -gt 50MB) {
            $results += [PSCustomObject]@{
                Component = $folder.Name
                SizeGB = [math]::Round($size/1GB, 2)
                SizeMB = [math]::Round($size/1MB, 2)
                Path = $folder.FullName
            }
        }
    }

    $results | Sort-Object SizeGB -Descending | Format-Table Component, SizeGB, SizeMB -AutoSize

    # Check Chrome specifically
    if (Test-Path "C:\Users\szmen\AppData\Local\Google\Chrome") {
        Write-Host "`nCHROME DETAILED BREAKDOWN:"
        Write-Host "-" * 80

        $chromeFolders = @(
            @{Name="User Data"; Path="C:\Users\szmen\AppData\Local\Google\Chrome\User Data"},
            @{Name="Application"; Path="C:\Users\szmen\AppData\Local\Google\Chrome\Application"}
        )

        foreach ($cf in $chromeFolders) {
            if (Test-Path $cf.Path) {
                $size = (Get-ChildItem $cf.Path -Recurse -File -ErrorAction SilentlyContinue |
                         Measure-Object -Property Length -Sum).Sum
                $sizeGB = [math]::Round($size/1GB, 2)
                Write-Host "$sizeGB GB - $($cf.Name)"

                # Check for cache subdirectories
                $subfolders = Get-ChildItem $cf.Path -Directory -ErrorAction SilentlyContinue |
                              Where-Object {$_.Name -like "*Cache*" -or $_.Name -like "*GPUCache*" -or $_.Name -like "*Service Worker*"}

                foreach ($sub in $subfolders) {
                    $subSize = (Get-ChildItem $sub.FullName -Recurse -File -ErrorAction SilentlyContinue |
                                Measure-Object -Property Length -Sum).Sum
                    if ($subSize -gt 10MB) {
                        $subSizeMB = [math]::Round($subSize/1MB, 2)
                        Write-Host "  - $subSizeMB MB in $($sub.Name)"
                    }
                }
            }
        }
    }

    # Check GoogleUpdater
    if (Test-Path "C:\Users\szmen\AppData\Local\Google\GoogleUpdater") {
        Write-Host "`nGOOGLE UPDATER CACHE:"
        Write-Host "-" * 80
        $updaterSize = (Get-ChildItem "C:\Users\szmen\AppData\Local\Google\GoogleUpdater" -Recurse -File -ErrorAction SilentlyContinue |
                        Measure-Object -Property Length -Sum).Sum
        $updaterGB = [math]::Round($updaterSize/1GB, 2)
        Write-Host "$updaterGB GB - Updater cache (can be cleared)"
    }

} else {
    Write-Host "[ERROR] Google folder not found"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "CLEANUP OPTIONS"
Write-Host "=========================================="
Write-Host ""
Write-Host "SAFE TO CLEAR:"
Write-Host "1. Chrome caches (already cleared browser caches earlier)"
Write-Host "2. GoogleUpdater cache files"
Write-Host "3. Temp/log files"
Write-Host ""
Write-Host "KEEP:"
Write-Host "1. Chrome User Data (bookmarks, passwords, extensions)"
Write-Host "2. Chrome Application (program files)"
Write-Host ""
Write-Host "RECOMMENDED ACTION:"
Write-Host "- Clear GoogleUpdater cache if large"
Write-Host "- Chrome caches already cleared in Phase 4"
Write-Host "- Consider moving User Data to D: via symlink (advanced)"
Write-Host ""
Write-Host "=========================================="
Write-Host ""
