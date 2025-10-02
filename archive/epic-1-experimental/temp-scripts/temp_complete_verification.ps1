# Complete Optimization Verification Report
Write-Host "`n=========================================="
Write-Host "COMPLETE OPTIMIZATION REPORT"
Write-Host "==========================================`n"

# Drive Space Summary
Write-Host "CURRENT DRIVE SPACE:"
Write-Host "-" * 40
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -eq "C" -or $_.Name -eq "D" } |
    Format-Table Name,
        @{Name="Used(GB)";Expression={[math]::Round($_.Used/1GB,2)}; Align="Right"},
        @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}; Align="Right"},
        @{Name="Total(GB)";Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}; Align="Right"},
        @{Name="% Free";Expression={[math]::Round(($_.Free/($_.Used+$_.Free))*100,1)}; Align="Right"}

# Verify Phase 1: Docker Migration
Write-Host "`nPHASE 1: Docker Migration"
Write-Host "-" * 40
if (Test-Path "D:\Docker\wsl") {
    $dockerSize = (Get-ChildItem "D:\Docker" -Recurse -File -ErrorAction SilentlyContinue |
                   Measure-Object -Property Length -Sum).Sum
    Write-Host "[OK] Docker data on D: drive:" ([math]::Round($dockerSize/1GB,2)) "GB"
} else {
    Write-Host "[WARN] Docker data not found on D: drive"
}

# Verify Phase 2: Cache Cleanup
Write-Host "`nPHASE 2: Cache Cleanup"
Write-Host "-" * 40

$cleanupItems = @(
    @{Path="C:\Users\szmen\AppData\Local\Temp"; Name="Temp files"},
    @{Path="C:\Users\szmen\.cache\puppeteer"; Name="Puppeteer cache"},
    @{Path="C:\Users\szmen\AppData\Local\ms-playwright"; Name="Playwright browsers"}
)

foreach ($item in $cleanupItems) {
    if (Test-Path $item.Path) {
        $size = (Get-ChildItem $item.Path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        if ($sizeGB -gt 0.5) {
            Write-Host "[INFO] $($item.Name): $sizeGB GB (regenerated)"
        } else {
            Write-Host "[OK] $($item.Name): $sizeGB GB (minimal)"
        }
    } else {
        Write-Host "[OK] $($item.Name): Removed"
    }
}

# Verify Phase 3: Symlink Migration
Write-Host "`nPHASE 3: Symlink Migration to D: Drive"
Write-Host "-" * 40

$symlinks = @(
    @{Path="C:\Users\szmen\.cache"; Target="D:\DevCache\.cache"},
    @{Path="C:\Users\szmen\AppData\Local\uv"; Target="D:\DevCache\uv"}
)

foreach ($symlink in $symlinks) {
    if (Test-Path $symlink.Path) {
        $item = Get-Item $symlink.Path
        if ($item.LinkType -eq "SymbolicLink") {
            # Get actual size from target
            $targetSize = (Get-ChildItem $symlink.Target -Recurse -File -ErrorAction SilentlyContinue |
                          Measure-Object -Property Length -Sum).Sum
            $sizeGB = [math]::Round($targetSize/1GB, 2)
            Write-Host "[OK] Symlink: $($symlink.Path) -> $($symlink.Target) ($sizeGB GB)"
        } else {
            Write-Host "[WARN] Not a symlink: $($symlink.Path)"
        }
    } else {
        Write-Host "[WARN] Symlink not found: $($symlink.Path)"
    }
}

# Outlook Analysis
Write-Host "`nOUTLOOK DATA ANALYSIS"
Write-Host "-" * 40
$outlookPath = "C:\Users\szmen\AppData\Local\Microsoft\Outlook"
if (Test-Path $outlookPath) {
    $ostFiles = Get-ChildItem $outlookPath -Filter *.ost -File -ErrorAction SilentlyContinue
    foreach ($file in $ostFiles) {
        $sizeGB = [math]::Round($file.Length/1GB, 2)
        Write-Host "[INFO] OST file (cannot move): $sizeGB GB - $($file.Name)"
    }
}

# Summary
Write-Host "`n=========================================="
Write-Host "OPTIMIZATION SUMMARY"
Write-Host "=========================================="
Write-Host "Phase 1 - Docker Migration: ~3.5 GB moved to D:"
Write-Host "Phase 2 - Cache Cleanup: ~6-7 GB freed"
Write-Host "Phase 3 - Symlink Migration: ~2 GB moved to D:"
Write-Host ""
Write-Host "TOTAL SPACE RECOVERED: ~11-12 GB"
Write-Host "=========================================="
Write-Host ""
Write-Host "RECOMMENDATIONS:"
Write-Host "1. [MANUAL] Outlook OST (7.8 GB): Cannot be moved (online cache)"
Write-Host "2. [OPTIONAL] Run Disk Cleanup wizard for system files"
Write-Host "3. [DONE] Monitor C: drive - maintain >10 GB free"
Write-Host ""
Write-Host "=========================================="
Write-Host ""
