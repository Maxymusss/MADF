# Create symbolic links (requires administrator)
Write-Host "`nCreating symbolic links (running as administrator)...`n"

# Create symlink for .cache
if (Test-Path "D:\DevCache\.cache") {
    if (-not (Test-Path "C:\Users\szmen\.cache")) {
        New-Item -ItemType SymbolicLink -Path "C:\Users\szmen\.cache" -Target "D:\DevCache\.cache" -Force
        Write-Host "[OK] Symlink created: C:\Users\szmen\.cache -> D:\DevCache\.cache"
    } else {
        Write-Host "[INFO] C:\Users\szmen\.cache already exists"
    }
} else {
    Write-Host "[WARN] D:\DevCache\.cache not found"
}

# Create symlink for uv
if (Test-Path "D:\DevCache\uv") {
    if (-not (Test-Path "C:\Users\szmen\AppData\Local\uv")) {
        New-Item -ItemType SymbolicLink -Path "C:\Users\szmen\AppData\Local\uv" -Target "D:\DevCache\uv" -Force
        Write-Host "[OK] Symlink created: C:\Users\szmen\AppData\Local\uv -> D:\DevCache\uv"
    } else {
        Write-Host "[INFO] C:\Users\szmen\AppData\Local\uv already exists"
    }
} else {
    Write-Host "[WARN] D:\DevCache\uv not found"
}

Write-Host "`nVerifying symlinks:"
Get-Item "C:\Users\szmen\.cache" -ErrorAction SilentlyContinue | Format-List FullName, LinkType, Target
Get-Item "C:\Users\szmen\AppData\Local\uv" -ErrorAction SilentlyContinue | Format-List FullName, LinkType, Target

Write-Host "`nSymlink creation complete.`n"
