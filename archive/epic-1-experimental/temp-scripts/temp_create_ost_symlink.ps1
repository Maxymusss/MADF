# Create symbolic link for OST file (requires administrator)
Write-Host "`n=========================================="
Write-Host "Creating OST Symbolic Link"
Write-Host "==========================================`n"

$sourcePath = "C:\Users\szmen\AppData\Local\Microsoft\Outlook\max.meng@pinpointfund.com - max.ost"
$targetPath = "D:\OutlookData\max.meng@pinpointfund.com - max.ost"

# Verify target exists
if (-not (Test-Path $targetPath)) {
    Write-Host "[ERROR] Target OST file not found: $targetPath"
    exit 1
}

# Verify source doesn't exist
if (Test-Path $sourcePath) {
    Write-Host "[ERROR] Source path already exists: $sourcePath"
    Write-Host "Cannot create symlink over existing file."
    exit 1
}

# Create symlink
Write-Host "Creating symbolic link..."
Write-Host "From: $sourcePath"
Write-Host "To:   $targetPath"
Write-Host ""

try {
    New-Item -ItemType SymbolicLink -Path $sourcePath -Target $targetPath -Force -ErrorAction Stop
    Write-Host "[OK] Symbolic link created successfully"

    # Verify symlink
    $item = Get-Item $sourcePath
    if ($item.LinkType -eq "SymbolicLink") {
        Write-Host "[OK] Verified: Link Type = SymbolicLink"
        Write-Host "[OK] Target: $($item.Target)"
    }
} catch {
    Write-Host "[ERROR] Failed to create symlink: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "This script must be run as Administrator."
    exit 1
}

Write-Host "`n==========================================`n"
