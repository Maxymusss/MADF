# Clear browser caches
Write-Host "`nClearing browser caches...`n"

# Chrome Cache
Write-Host "Clearing Chrome cache..."
$chromePaths = @(
    "C:\Users\szmen\AppData\Local\Google\Chrome\User Data\Default\Cache",
    "C:\Users\szmen\AppData\Local\Google\Chrome\User Data\Default\Code Cache"
)

foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        $before = (Get-ChildItem $path -Recurse -File -EA 0 | Measure-Object Length -Sum).Sum
        Remove-Item "$path\*" -Recurse -Force -ErrorAction SilentlyContinue
        $beforeMB = [math]::Round($before/1MB, 2)
        Write-Host "  Cleared: $beforeMB MB from $path"
    }
}

# Edge Cache
Write-Host "`nClearing Edge cache..."
$edgePath = "C:\Users\szmen\AppData\Local\Microsoft\Edge\User Data\Default\Cache"
if (Test-Path $edgePath) {
    $before = (Get-ChildItem $edgePath -Recurse -File -EA 0 | Measure-Object Length -Sum).Sum
    Remove-Item "$edgePath\*" -Recurse -Force -ErrorAction SilentlyContinue
    $beforeMB = [math]::Round($before/1MB, 2)
    Write-Host "  Cleared: $beforeMB MB"
}

# Firefox Cache (if exists)
Write-Host "`nClearing Firefox cache..."
$firefoxBase = "C:\Users\szmen\AppData\Local\Mozilla\Firefox\Profiles"
if (Test-Path $firefoxBase) {
    $profiles = Get-ChildItem $firefoxBase -Directory -EA 0
    foreach ($profile in $profiles) {
        $cachePath = Join-Path $profile.FullName "cache2"
        if (Test-Path $cachePath) {
            $before = (Get-ChildItem $cachePath -Recurse -File -EA 0 | Measure-Object Length -Sum).Sum
            Remove-Item "$cachePath\*" -Recurse -Force -ErrorAction SilentlyContinue
            $beforeMB = [math]::Round($before/1MB, 2)
            Write-Host "  Cleared: $beforeMB MB from Firefox"
        }
    }
}

Write-Host "`n[OK] Browser caches cleared`n"
