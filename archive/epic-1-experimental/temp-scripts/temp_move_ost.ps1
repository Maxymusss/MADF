# Move Outlook OST file to D: drive
Write-Host "`n=========================================="
Write-Host "Moving Outlook OST File"
Write-Host "==========================================`n"

$sourcePath = "C:\Users\szmen\AppData\Local\Microsoft\Outlook"
$targetPath = "D:\OutlookData"

# List current OST files
Write-Host "Current OST files:"
$ostFiles = Get-ChildItem "$sourcePath\*.ost" -ErrorAction SilentlyContinue

if ($ostFiles.Count -eq 0) {
    Write-Host "[ERROR] No OST files found in $sourcePath"
    exit 1
}

foreach ($file in $ostFiles) {
    $sizeGB = [math]::Round($file.Length/1GB, 2)
    Write-Host "  $sizeGB GB - $($file.Name)"
}

Write-Host "`nMoving OST file(s) to $targetPath..."

foreach ($file in $ostFiles) {
    $targetFile = Join-Path $targetPath $file.Name
    Write-Host "Moving: $($file.Name)"
    Move-Item $file.FullName $targetFile -Force
    Write-Host "[OK] Moved to: $targetFile"
}

Write-Host "`nVerifying move complete..."
$movedFiles = Get-ChildItem "$targetPath\*.ost" -ErrorAction SilentlyContinue

if ($movedFiles.Count -gt 0) {
    Write-Host "[OK] OST files successfully moved to D:\OutlookData"
    foreach ($file in $movedFiles) {
        $sizeGB = [math]::Round($file.Length/1GB, 2)
        Write-Host "  $sizeGB GB - $($file.Name)"
    }
} else {
    Write-Host "[ERROR] Move verification failed"
}

Write-Host "`n==========================================`n"
