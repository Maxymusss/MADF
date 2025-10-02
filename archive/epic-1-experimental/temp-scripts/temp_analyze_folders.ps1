# Analyze folder sizes in user directory
Write-Host "`nAnalyzing C:\Users\szmen folder sizes...`n"

$folders = Get-ChildItem -Path "C:\Users\szmen" -Directory -ErrorAction SilentlyContinue

foreach ($folder in $folders) {
    $size = (Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum

    if ($size -gt 100MB) {
        $sizeGB = [math]::Round($size/1GB, 2)
        Write-Host "$sizeGB GB - $($folder.Name)"
    }
}

Write-Host "`n`nChecking common cache locations:"
Write-Host "=" * 80

$cachePaths = @(
    "C:\Users\szmen\.cache",
    "C:\Users\szmen\AppData\Local\Temp",
    "C:\Users\szmen\AppData\Local\Microsoft\Windows\INetCache",
    "C:\Users\szmen\AppData\Local\npm-cache",
    "C:\Windows\Temp",
    "C:\Windows\SoftwareDistribution\Download"
)

foreach ($path in $cachePaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        Write-Host "$sizeGB GB - $path"
    }
}
