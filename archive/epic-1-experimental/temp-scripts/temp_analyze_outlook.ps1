# Analyze Outlook PST files
Write-Host "`n=========================================="
Write-Host "Analyzing Outlook Data Files"
Write-Host "==========================================`n"

$outlookPath = "C:\Users\szmen\AppData\Local\Microsoft\Outlook"

if (Test-Path $outlookPath) {
    Write-Host "Searching for PST/OST files in Outlook directory...`n"

    $pstFiles = Get-ChildItem $outlookPath -Recurse -Include *.pst, *.ost -File -ErrorAction SilentlyContinue

    if ($pstFiles.Count -gt 0) {
        $totalSize = 0
        foreach ($file in $pstFiles) {
            $sizeGB = [math]::Round($file.Length/1GB, 2)
            $totalSize += $sizeGB
            Write-Host "$sizeGB GB - $($file.Name)"
            Write-Host "  Path: $($file.FullName)"
            Write-Host "  Modified: $($file.LastWriteTime)"
            Write-Host ""
        }
        Write-Host "Total Outlook data: $totalSize GB`n"

        Write-Host "RECOMMENDATION:"
        Write-Host "- OST files (Online cache): Cannot be moved, auto-regenerates"
        Write-Host "- PST files (Archives): Can be moved to D: drive"
        Write-Host "  1. Open Outlook > File > Account Settings > Data Files"
        Write-Host "  2. Select PST file > Settings > Move to D:\OutlookArchive\"
        Write-Host "  3. Restart Outlook`n"
    } else {
        Write-Host "No PST/OST files found in Outlook directory`n"
    }
} else {
    Write-Host "Outlook directory not found`n"
}

# Check alternative locations
Write-Host "Checking alternative Outlook locations..."
$altPaths = @(
    "C:\Users\szmen\Documents\Outlook Files",
    "C:\Users\szmen\OneDrive\Documents\Outlook Files"
)

foreach ($path in $altPaths) {
    if (Test-Path $path) {
        $files = Get-ChildItem $path -Include *.pst, *.ost -File -ErrorAction SilentlyContinue
        if ($files.Count -gt 0) {
            Write-Host "`nFound Outlook files in: $path"
            foreach ($file in $files) {
                $sizeGB = [math]::Round($file.Length/1GB, 2)
                Write-Host "  $sizeGB GB - $($file.Name)"
            }
        }
    }
}

Write-Host "`n=========================================="
