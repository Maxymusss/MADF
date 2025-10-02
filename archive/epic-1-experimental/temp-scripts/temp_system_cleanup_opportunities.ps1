# Analyze system cleanup opportunities
Write-Host "`n=========================================="
Write-Host "SYSTEM CLEANUP OPPORTUNITIES"
Write-Host "==========================================`n"

# WinSxS folder (component store)
Write-Host "WINDOWS COMPONENT STORE (WinSxS):"
Write-Host "-" * 40
if (Test-Path "C:\Windows\WinSxS") {
    $winsxsSize = (Get-ChildItem "C:\Windows\WinSxS" -Recurse -File -ErrorAction SilentlyContinue |
                   Measure-Object -Property Length -Sum).Sum
    $sizeGB = [math]::Round($winsxsSize/1GB, 2)
    Write-Host "$sizeGB GB - WinSxS folder"
    Write-Host "[INFO] Use DISM to clean: Dism.exe /online /Cleanup-Image /StartComponentCleanup"
}

# Check installer cache
Write-Host "`nINSTALLER CACHES:"
Write-Host "-" * 40
$installerPaths = @(
    "C:\Windows\Installer",
    "C:\ProgramData\Package Cache",
    "C:\Windows\Downloaded Program Files"
)

foreach ($path in $installerPaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        if ($sizeGB -gt 0.1) {
            Write-Host "$sizeGB GB - $path"
        }
    }
}

# System Restore points
Write-Host "`nSYSTEM RESTORE:"
Write-Host "-" * 40
try {
    $restorePoints = Get-ComputerRestorePoint -ErrorAction SilentlyContinue
    if ($restorePoints) {
        Write-Host "System Restore is enabled"
        Write-Host "Restore points found: $($restorePoints.Count)"
        Write-Host "[OPTION] Disable or reduce restore point space allocation"
    } else {
        Write-Host "No restore points found or System Restore disabled"
    }
} catch {
    Write-Host "Could not check System Restore status"
}

# Check for old Windows installations
Write-Host "`nOLD WINDOWS INSTALLATIONS:"
Write-Host "-" * 40
$oldWindowsPaths = @(
    "C:\Windows.old",
    "C:\`$Windows.~BT",
    "C:\`$Windows.~WS"
)

foreach ($path in $oldWindowsPaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        Write-Host "$sizeGB GB - $path [CAN DELETE via Disk Cleanup]"
    }
}

# Check for crash dumps
Write-Host "`nCRASH DUMPS:"
Write-Host "-" * 40
$dumpPaths = @(
    "C:\Windows\Minidump",
    "C:\Windows\MEMORY.DMP",
    "C:\Users\szmen\AppData\Local\CrashDumps"
)

foreach ($path in $dumpPaths) {
    if (Test-Path $path) {
        if ((Get-Item $path).PSIsContainer) {
            $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue |
                     Measure-Object -Property Length -Sum).Sum
        } else {
            $size = (Get-Item $path).Length
        }
        $sizeGB = [math]::Round($size/1GB, 2)
        if ($sizeGB -gt 0.1) {
            Write-Host "$sizeGB GB - $path"
        }
    }
}

Write-Host "`n=========================================="
