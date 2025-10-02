# Analyze Microsoft folder in AppData\Local
Write-Host "`nFolders in C:\Users\szmen\AppData\Local\Microsoft (over 50MB):`n"

$folders = Get-ChildItem 'C:\Users\szmen\AppData\Local\Microsoft' -Directory -ErrorAction SilentlyContinue

$results = @()
foreach ($folder in $folders) {
    $size = (Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum

    if ($size -gt 50MB) {
        $results += [PSCustomObject]@{
            SizeGB = [math]::Round($size/1GB, 2)
            Name = $folder.Name
        }
    }
}

$results | Sort-Object SizeGB -Descending | ForEach-Object {
    Write-Host "$($_.SizeGB) GB - $($_.Name)"
}

# Check for WSL distributions
Write-Host "`n`nWSL Distributions (if any):"
if (Test-Path "$env:LOCALAPPDATA\Packages") {
    $wslFolders = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Directory -ErrorAction SilentlyContinue |
                  Where-Object { $_.Name -like "*CanonicalGroup*" -or $_.Name -like "*TheDebianProject*" -or $_.Name -like "*SUSE*" }

    foreach ($wslFolder in $wslFolders) {
        $size = (Get-ChildItem $wslFolder.FullName -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        Write-Host "$sizeGB GB - $($wslFolder.Name)"
    }
}
