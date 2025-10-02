# Comprehensive C: drive space analysis for additional recovery
Write-Host "`n=========================================="
Write-Host "ADDITIONAL SPACE RECOVERY ANALYSIS"
Write-Host "==========================================`n"

# Current space
Write-Host "CURRENT C: DRIVE STATUS:"
Write-Host "-" * 40
Get-PSDrive C | Format-Table Name,
    @{Name="Used(GB)";Expression={[math]::Round($_.Used/1GB,2)}},
    @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}},
    @{Name="Total(GB)";Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}}

# Analyze large folders in AppData\Local
Write-Host "`nLARGE FOLDERS IN AppData\Local (>500MB):"
Write-Host "-" * 40
$localAppData = "C:\Users\szmen\AppData\Local"
$folders = Get-ChildItem $localAppData -Directory -ErrorAction SilentlyContinue

$largeFolders = @()
foreach ($folder in $folders) {
    $size = (Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum

    if ($size -gt 500MB) {
        $largeFolders += [PSCustomObject]@{
            Name = $folder.Name
            SizeGB = [math]::Round($size/1GB, 2)
            Path = $folder.FullName
        }
    }
}

$largeFolders | Sort-Object SizeGB -Descending | Format-Table -AutoSize

# Check for Windows Update cache
Write-Host "`nWINDOWS UPDATE & SYSTEM CACHE:"
Write-Host "-" * 40
$systemPaths = @(
    "C:\Windows\SoftwareDistribution\Download",
    "C:\Windows\Temp",
    "C:\Windows\Logs\CBS",
    "C:\Windows\System32\config\systemprofile\AppData\Local\Temp"
)

foreach ($path in $systemPaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        if ($sizeGB -gt 0.1) {
            Write-Host "$sizeGB GB - $path"
        }
    }
}

# Check user profile folders
Write-Host "`nUSER PROFILE FOLDERS (>500MB):"
Write-Host "-" * 40
$userFolders = @(
    "C:\Users\szmen\Downloads",
    "C:\Users\szmen\Documents",
    "C:\Users\szmen\Videos",
    "C:\Users\szmen\Pictures",
    "C:\Users\szmen\Music",
    "C:\Users\szmen\Desktop"
)

foreach ($path in $userFolders) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        if ($sizeGB -gt 0.5) {
            Write-Host "$sizeGB GB - $path"
        }
    }
}

# Check OneDrive cache
Write-Host "`nONEDRIVE CACHE:"
Write-Host "-" * 40
$onedrivePaths = @(
    "C:\Users\szmen\AppData\Local\Microsoft\OneDrive",
    "C:\Users\szmen\OneDrive"
)

foreach ($path in $onedrivePaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        Write-Host "$sizeGB GB - $path"
    }
}

# Check browser caches
Write-Host "`nBROWSER CACHES:"
Write-Host "-" * 40
$browserPaths = @(
    @{Name="Chrome"; Path="C:\Users\szmen\AppData\Local\Google\Chrome\User Data\Default\Cache"},
    @{Name="Chrome (Cache)"; Path="C:\Users\szmen\AppData\Local\Google\Chrome\User Data\Default\Code Cache"},
    @{Name="Edge"; Path="C:\Users\szmen\AppData\Local\Microsoft\Edge\User Data\Default\Cache"},
    @{Name="Firefox"; Path="C:\Users\szmen\AppData\Local\Mozilla\Firefox\Profiles"}
)

foreach ($browser in $browserPaths) {
    if (Test-Path $browser.Path) {
        $size = (Get-ChildItem $browser.Path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        if ($sizeGB -gt 0.1) {
            Write-Host "$sizeGB GB - $($browser.Name)"
        }
    }
}

# Check for virtual machines
Write-Host "`nVIRTUAL MACHINES & CONTAINERS:"
Write-Host "-" * 40
$vmPaths = @(
    "C:\Users\szmen\VirtualBox VMs",
    "C:\Users\szmen\.virtualbox",
    "C:\ProgramData\Docker"
)

foreach ($path in $vmPaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        if ($sizeGB -gt 0.5) {
            Write-Host "$sizeGB GB - $path"
        }
    }
}

# Hibernation file
Write-Host "`nSYSTEM FILES:"
Write-Host "-" * 40
if (Test-Path "C:\hiberfil.sys") {
    $hibFile = Get-Item "C:\hiberfil.sys" -Force
    $sizeGB = [math]::Round($hibFile.Length/1GB, 2)
    Write-Host "$sizeGB GB - Hibernation file (hiberfil.sys)"
}

if (Test-Path "C:\pagefile.sys") {
    $pageFile = Get-Item "C:\pagefile.sys" -Force
    $sizeGB = [math]::Round($pageFile.Length/1GB, 2)
    Write-Host "$sizeGB GB - Page file (pagefile.sys)"
}

if (Test-Path "C:\swapfile.sys") {
    $swapFile = Get-Item "C:\swapfile.sys" -Force
    $sizeGB = [math]::Round($swapFile.Length/1GB, 2)
    Write-Host "$sizeGB GB - Swap file (swapfile.sys)"
}

Write-Host "`n=========================================="
