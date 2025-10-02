# Analyze AppData\Local\Programs folder
Write-Host "`n=========================================="
Write-Host "AppData\Local\Programs ANALYSIS"
Write-Host "==========================================`n"

$programsPath = "C:\Users\szmen\AppData\Local\Programs"

if (Test-Path $programsPath) {
    Write-Host "PROGRAMS FOLDER BREAKDOWN:"
    Write-Host "-" * 80

    $folders = Get-ChildItem $programsPath -Directory -ErrorAction SilentlyContinue

    $results = @()
    foreach ($folder in $folders) {
        $size = (Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum

        if ($size -gt 0) {
            $results += [PSCustomObject]@{
                Application = $folder.Name
                SizeGB = [math]::Round($size/1GB, 2)
                Path = $folder.FullName
                LastModified = $folder.LastWriteTime
            }
        }
    }

    $results | Sort-Object SizeGB -Descending | Format-Table Application, SizeGB, LastModified -AutoSize

    $totalSize = ($results | Measure-Object -Property SizeGB -Sum).Sum
    Write-Host ""
    Write-Host "Total: $totalSize GB in $($results.Count) applications"

    # Identify potentially removable apps
    Write-Host "`nPOTENTIALLY UNINSTALLABLE APPLICATIONS:"
    Write-Host "-" * 80
    Write-Host ""

    $removable = $results | Where-Object {$_.SizeGB -gt 0.1} | Sort-Object SizeGB -Descending

    foreach ($app in $removable) {
        Write-Host "$($app.SizeGB) GB - $($app.Application)"

        # Check for uninstaller
        $uninstallers = Get-ChildItem $app.Path -Recurse -Include "uninstall*.exe","Uninstall*.exe" -File -ErrorAction SilentlyContinue
        if ($uninstallers) {
            Write-Host "  [INFO] Has uninstaller: $($uninstallers[0].Name)"
        }

        # Check if it's a known app type
        if ($app.Application -like "*updater*") {
            Write-Host "  [NOTE] Updater application - check if parent app is still installed"
        }
        if ($app.Application -like "*-updater") {
            Write-Host "  [NOTE] Auto-updater - check if parent app is still installed"
        }

        Write-Host ""
    }

} else {
    Write-Host "[ERROR] Programs folder not found"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "RECOMMENDATIONS"
Write-Host "=========================================="
Write-Host ""
Write-Host "1. Review each application above"
Write-Host "2. Use 'Settings > Apps > Installed apps' to uninstall safely"
Write-Host "3. Or use application's own uninstaller if available"
Write-Host "4. Check for '-updater' apps - parent may be uninstalled already"
Write-Host ""
Write-Host "=========================================="
Write-Host ""
