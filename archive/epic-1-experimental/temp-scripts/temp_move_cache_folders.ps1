# Phase 3: Move cache folders to D: drive with symlinks
Write-Host "`n=========================================="
Write-Host "Phase 3: Advanced Cache Migration"
Write-Host "==========================================`n"

# Check current .cache size
if (Test-Path 'C:\Users\szmen\.cache') {
    $cacheSize = (Get-ChildItem 'C:\Users\szmen\.cache' -Recurse -File -ErrorAction SilentlyContinue |
                  Measure-Object -Property Length -Sum).Sum
    Write-Host "Current .cache size:" ([math]::Round($cacheSize/1GB, 2)) "GB"

    # Create DevCache directory on D:
    New-Item -ItemType Directory -Path "D:\DevCache" -Force -ErrorAction SilentlyContinue | Out-Null

    # Move .cache folder
    Write-Host "Moving .cache folder to D:\DevCache\.cache..."
    Move-Item "C:\Users\szmen\.cache" "D:\DevCache\.cache" -Force

    # Create symlink
    Write-Host "Creating symbolic link..."
    New-Item -ItemType SymbolicLink -Path "C:\Users\szmen\.cache" -Target "D:\DevCache\.cache" -Force

    Write-Host "[OK] .cache folder migrated successfully`n"
} else {
    Write-Host "[INFO] .cache folder not found, skipping...`n"
}

# Check and move uv cache
if (Test-Path 'C:\Users\szmen\AppData\Local\uv') {
    $uvSize = (Get-ChildItem 'C:\Users\szmen\AppData\Local\uv' -Recurse -File -ErrorAction SilentlyContinue |
               Measure-Object -Property Length -Sum).Sum
    Write-Host "Current uv cache size:" ([math]::Round($uvSize/1GB, 2)) "GB"

    # Move uv folder
    Write-Host "Moving uv cache to D:\DevCache\uv..."
    Move-Item "C:\Users\szmen\AppData\Local\uv" "D:\DevCache\uv" -Force

    # Create symlink
    Write-Host "Creating symbolic link..."
    New-Item -ItemType SymbolicLink -Path "C:\Users\szmen\AppData\Local\uv" -Target "D:\DevCache\uv" -Force

    Write-Host "[OK] uv cache migrated successfully`n"
} else {
    Write-Host "[INFO] uv cache not found, skipping...`n"
}

Write-Host "=========================================="
Write-Host "Cache Migration Complete"
Write-Host "==========================================`n"

# Verify symlinks created
Write-Host "Verifying symbolic links:"
Get-Item "C:\Users\szmen\.cache" -ErrorAction SilentlyContinue | Select-Object FullName, LinkType, Target
Get-Item "C:\Users\szmen\AppData\Local\uv" -ErrorAction SilentlyContinue | Select-Object FullName, LinkType, Target
