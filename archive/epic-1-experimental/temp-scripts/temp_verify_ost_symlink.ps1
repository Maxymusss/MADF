# Verify OST symlink
Write-Host "`nVerifying OST Symlink...`n"

$symlinkPath = "C:\Users\szmen\AppData\Local\Microsoft\Outlook\max.meng@pinpointfund.com - max.ost"

if (Test-Path $symlinkPath) {
    $item = Get-Item $symlinkPath

    Write-Host "Path: $($item.FullName)"
    Write-Host "LinkType: $($item.LinkType)"
    Write-Host "Target: $($item.Target)"

    if ($item.LinkType -eq "SymbolicLink") {
        Write-Host "`n[OK] Symlink created successfully"

        # Verify target file exists
        if (Test-Path $item.Target) {
            $targetFile = Get-Item $item.Target
            $sizeGB = [math]::Round($targetFile.Length/1GB, 2)
            Write-Host "[OK] Target file exists: $sizeGB GB"
        }
    } else {
        Write-Host "`n[WARN] File exists but is not a symlink"
    }
} else {
    Write-Host "[ERROR] Symlink not found at: $symlinkPath"
}

Write-Host ""
