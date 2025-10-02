# Analyze AppData\Local folder sizes
Write-Host "`nLarge folders in C:\Users\szmen\AppData\Local (over 100MB):`n"

$folders = Get-ChildItem 'C:\Users\szmen\AppData\Local' -Directory -ErrorAction SilentlyContinue

$results = @()
foreach ($folder in $folders) {
    $size = (Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum

    if ($size -gt 100MB) {
        $results += [PSCustomObject]@{
            SizeGB = [math]::Round($size/1GB, 2)
            Name = $folder.Name
        }
    }
}

$results | Sort-Object SizeGB -Descending | ForEach-Object {
    Write-Host "$($_.SizeGB) GB - $($_.Name)"
}
