# Analyze Windows Installer Cache
Write-Host "`n=========================================="
Write-Host "WINDOWS INSTALLER CACHE ANALYSIS"
Write-Host "==========================================`n"

$installerPath = "C:\Windows\Installer"

if (Test-Path $installerPath) {
    # Overall size
    Write-Host "TOTAL INSTALLER CACHE SIZE:"
    Write-Host "-" * 40
    $totalSize = (Get-ChildItem $installerPath -Recurse -File -ErrorAction SilentlyContinue |
                  Measure-Object -Property Length -Sum).Sum
    $totalGB = [math]::Round($totalSize/1GB, 2)
    Write-Host "$totalGB GB total in $installerPath"
    Write-Host ""

    # Large MSI files
    Write-Host "LARGE MSI FILES (>100 MB):"
    Write-Host "-" * 40
    $msiFiles = Get-ChildItem $installerPath -Filter *.msi -File -ErrorAction SilentlyContinue |
                Where-Object {$_.Length -gt 100MB} |
                Sort-Object Length -Descending |
                Select-Object -First 20

    if ($msiFiles.Count -gt 0) {
        foreach ($file in $msiFiles) {
            $sizeMB = [math]::Round($file.Length/1MB, 2)
            Write-Host "$sizeMB MB - $($file.Name)"
        }
        Write-Host ""
        Write-Host "Found $($msiFiles.Count) MSI files over 100MB"
    } else {
        Write-Host "No large MSI files found"
    }

    # Large MSP files (patches)
    Write-Host "`nLARGE MSP FILES (>50 MB):"
    Write-Host "-" * 40
    $mspFiles = Get-ChildItem $installerPath -Filter *.msp -File -ErrorAction SilentlyContinue |
                Where-Object {$_.Length -gt 50MB} |
                Sort-Object Length -Descending |
                Select-Object -First 20

    if ($mspFiles.Count -gt 0) {
        foreach ($file in $mspFiles) {
            $sizeMB = [math]::Round($file.Length/1MB, 2)
            Write-Host "$sizeMB MB - $($file.Name)"
        }
        Write-Host ""
        Write-Host "Found $($mspFiles.Count) MSP files over 50MB"
    } else {
        Write-Host "No large MSP files found"
    }

    # File type breakdown
    Write-Host "`nFILE TYPE BREAKDOWN:"
    Write-Host "-" * 40
    $fileTypes = Get-ChildItem $installerPath -Recurse -File -ErrorAction SilentlyContinue |
                 Group-Object Extension |
                 ForEach-Object {
                     $size = ($_.Group | Measure-Object Length -Sum).Sum
                     [PSCustomObject]@{
                         Extension = $_.Name
                         Count = $_.Count
                         SizeMB = [math]::Round($size/1MB, 2)
                     }
                 } | Sort-Object SizeMB -Descending

    $fileTypes | Format-Table -AutoSize

} else {
    Write-Host "[ERROR] Windows Installer path not found"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "PATCHCLEANER TOOL RECOMMENDATION"
Write-Host "=========================================="
Write-Host ""
Write-Host "WARNING: Do NOT manually delete files from Windows\Installer"
Write-Host "These files may be needed for application repairs/uninstalls"
Write-Host ""
Write-Host "SAFE METHOD: Use PatchCleaner tool"
Write-Host "1. Download: https://www.homedev.com.au/Free/PatchCleaner"
Write-Host "2. Run PatchCleaner (free tool)"
Write-Host "3. It identifies orphaned installer files safely"
Write-Host "4. Move orphaned files to backup location"
Write-Host "5. Delete backup after confirming no issues (30 days)"
Write-Host ""
Write-Host "Alternative: Use Windows 'cleanmgr' with 'Clean up system files'"
Write-Host ""
Write-Host "=========================================="
Write-Host ""
